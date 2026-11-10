import json
from datetime import timedelta
import pytest
from app.models import Source, SourceVersion, Service, now
from test_api import env


def supplied(db, service, version):
    source = db.get(Source, version.source_id)
    source.title = 'Team research: Sami / TEST-001'
    source.agency = 'Uploaded team research — Sami'
    version.content = 'JANUN EDITORIAL TEAM RESEARCH\n' + json.dumps({
        'required_documents': 'Birth certificate',
        'application_method': 'Check the applicable registrar',
        'geographic_scope': 'Local jurisdiction only',
        'verification_status': 'conflicting_sources',
        'notes': 'Requirements need independent review.',
    })
    db.commit()
    return source


def test_imported_catalogue_visible_without_publishing(env):
    c, db, service, version = env
    supplied(db, service, version)
    listing = c.get('/api/services?q=jonmo').json()
    assert listing['total'] == 1
    assert listing['items'][0]['status'] == 'supplied_research'
    assert listing['items'][0]['verification_status'] == 'needs_review'
    assert listing['items'][0]['last_verified_at'] is None
    assert c.get('/api/categories/identity/services').json()['total'] == 1
    detail = c.get('/api/services/' + service.slug).json()
    assert detail['documents'] == ['Birth certificate']
    assert detail['steps'] == ['Check the applicable registrar']
    assert detail['scope'] == 'Local jurisdiction only'
    assert detail['raw_fields']['verification_status'] == 'conflicting_sources'
    assert detail['review_status'] == 'supplied_research'
    assert detail['sources'][0]['review_status'] == 'supplied_research'
    assert detail['sources'][0]['verified_at'] is None
    assert service.status == 'draft' and version.status == 'pending'


@pytest.mark.parametrize('change', ['private', 'rejected', 'archived', 'superseded', 'verified', 'expired', 'old_version'])
def test_withdrawn_or_private_import_is_not_exposed(env, change):
    c, db, service, version = env
    source = supplied(db, service, version)
    if change == 'private': source.title = 'Private reviewer draft'
    elif change == 'superseded': service.status = 'superseded'
    elif change == 'expired': version.review_due = now() - timedelta(days=1)
    elif change == 'old_version': source.current_version = None
    else: version.status = change
    db.commit()
    assert c.get('/api/services').json()['total'] == 0
    assert c.get('/api/services/' + service.slug).status_code == 404


def test_supplied_claims_never_become_supported_by_exact_match(env):
    c, db, service, version = env
    supplied(db, service, version)
    result = c.post('/api/check', json={'service_slug': service.slug, 'text': 'Birth certificate', 'language': 'en'})
    assert result.status_code == 200
    assert result.json()['claims'][0]['status'] == 'insufficient'
    assert result.json()['claims'][0]['evidence'] == []


def test_supplied_journey_is_a_localized_source_review_starting_point(env):
    c, db, service, version = env
    supplied(db, service, version)
    result = c.post('/api/journeys', json={'goal': 'new baby', 'language': 'bn'}).json()
    assert result['steps']
    assert 'জন্ম' in result['title']
    assert 'পর্যালোচনা বাকি' in result['notice']
    assert result['steps'][0]['slug'] == service.slug
    assert result['steps'][0]['depends_on'] == []
    assert result['steps'][0]['sources'][0]['verified_at'] is None


def test_imported_search_paginates_and_does_not_duplicate_sources(env):
    c, db, service, version = env
    supplied(db, service, version)
    other = Service(slug='another-birth', name_en='Another birth', name_bn='জন্ম', category='identity', status='published')
    db.add(other)
    extra = Source(service_id=service.id, title='Team research: Sami / EXTRA', agency='Uploaded team research — Sami', url='https://bdris.gov.bd/', current_version=version.id)
    db.add(extra); db.commit()
    assert c.get('/api/services?page_size=1').json()['total'] == 2
    first = c.get('/api/services?page_size=1').json()['items'][0]
    second = c.get('/api/services?page_size=1&page=2').json()['items'][0]
    assert first['id'] != second['id']
    assert c.get('/api/services?sort=name_desc').json()['items'][0]['name_en'] == 'Birth registration'


def test_reviewed_detail_takes_precedence(env):
    c, db, service, version = env
    supplied(db, service, version)
    service.status = 'published'; version.status = 'published'
    version.verified_at = now(); version.review_due = now() + timedelta(days=5)
    version.claims = {'documents': ['Reviewed requirement']}
    db.commit()
    assert c.get('/api/services/' + service.slug).json()['documents'] == ['Reviewed requirement']


def test_private_published_version_of_a_draft_service_does_not_leak(env):
    c, db, service, version = env
    supplied(db, service, version)
    source = Source(service_id=service.id, title='Private draft', url='https://bdris.gov.bd/')
    db.add(source); db.flush()
    private = SourceVersion(source_id=source.id, content='Private reviewer content', content_hash='private',
        status='published', verified_at=now(), review_due=now()+timedelta(days=3),
        claims={'documents':['Private reviewer content']})
    db.add(private); db.flush(); source.current_version=private.id; db.commit()
    detail=c.get('/api/services/'+service.slug).json()
    assert detail['documents']==['Birth certificate']
    result=c.post('/api/check',json={'service_slug':service.slug,'text':'Private reviewer content','language':'en'}).json()
    assert result['claims'][0]['status']=='insufficient'


def test_real_catalogue_details_and_sachin_hash_bound_projection(env):
    from app.team_data import import_drafts
    from app.cli import CATEGORIES
    from app.models import Category
    from sqlalchemy import select
    c, db, *_=env
    for slug, en, bn, icon in CATEGORIES:
        if not db.get(Category,slug):db.add(Category(slug=slug,name_en=en,name_bn=bn,icon=icon))
    db.commit(); import_drafts(db)
    # Every card returned by the live catalogue must open a real detail page,
    # including old aliases whose document-release canonical row isn't imported.
    for page in range(1,6):
        for row in c.get('/api/services',params={'page_size':50,'page':page}).json()['items']:
            response=c.get('/api/services/'+row['slug'])
            assert response.status_code==200, row['slug']
            assert response.json()['slug']==row['slug']
    assert c.get('/api/services?q=passport').json()['total']>0
    assert c.get('/api/categories/identity/services').json()['total']>0
    passport=c.get('/api/services/team-nafiew-janun-pass-001').json()
    assert passport['documents'] and passport['raw_fields']['service_id']=='JANUN-PASS-001'
    assert passport['review_status']=='supplied_research'
    land=c.get('/api/services/land-mutation-fees').json()
    assert '১,১০০' in land['fees']
    source=db.scalar(select(Source).join(Service,Source.service_id==Service.id).where(Service.slug=='land-mutation-fees'))
    db.get(SourceVersion,source.current_version).content='Edited summary without any confirmed fee.'
    db.commit()
    assert c.get('/api/services/land-mutation-fees').json()['fees'] is None


def test_public_unverified_version_is_not_called_reviewed_evidence(env):
    c,db,service,version=env
    service.status='published';version.status='published'
    version.review_due=now()+timedelta(days=3)
    version.claims={'documents':['Birth certificate']}
    db.commit()
    response=c.post('/api/check',json={'service_slug':service.slug,'text':'Birth certificate','language':'en'})
    assert response.json()['claims'][0]['status']=='insufficient'
