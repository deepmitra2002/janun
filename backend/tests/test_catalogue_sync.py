import json
from pathlib import Path
from collections import Counter
from sqlalchemy import select,func
import pytest
from app.models import Category,Service,Source,SourceVersion,Chunk,now
from app.cli import CATEGORIES
from app.team_data import import_drafts
from test_api import env


def setup_imports(db):
    for slug,en,bn,icon in CATEGORIES:
        if not db.get(Category,slug):db.add(Category(slug=slug,name_en=en,name_bn=bn,icon=icon))
    db.commit();import_drafts(db)


def test_sync_matches_public_categories_counts_and_updated_document_facts(env):
    from app.catalogue_sync import sync_public_catalogue
    c,db,*_=env;setup_imports(db)
    before=set(db.scalars(select(SourceVersion.id)))
    sync_public_catalogue(db)
    categories=c.get('/api/categories').json()
    assert len(categories)==13
    assert {r['slug'] for r in categories}>={'land','agriculture','local-government','utilities','health','welfare'}
    assert next(r for r in categories if r['slug']=='education')['name_bn']=='শিক্ষা ও কর্মজীবন'
    assert c.get('/api/services?page_size=1').json()['total']==271
    assert c.get('/api/services?category=education').json()['total']==46
    snapshot=json.loads((Path(__file__).resolve().parents[1]/'data/public-catalogue.json').read_text())
    for row in snapshot['services']:
        result=c.get('/api/services/'+row['slug'])
        assert result.status_code==200,row['slug']
        detail=result.json()
        for key in ('name_bn','name_en','category','description_bn','documents','steps','fees','scope','conflicts'):
            assert detail.get(key)==row.get(key),(row['slug'],key)
    passport=c.get('/api/services/team-nafiew-janun-pass-001').json()
    assert passport['document_update']['document']
    assert all(s.get('verified_at') is None for s in passport['sources'])
    assert before.issubset(set(db.scalars(select(SourceVersion.id))))
    assert not db.scalar(select(SourceVersion).where(SourceVersion.verified_at.is_not(None)))
    assert not db.scalar(select(Service).where(Service.status=='published'))
    counts=tuple(db.scalar(select(func.count()).select_from(model)) for model in (Service,Source,SourceVersion,Chunk))
    report=sync_public_catalogue(db)
    assert report['created']==0 and report['updated']==0
    assert counts==tuple(db.scalar(select(func.count()).select_from(model)) for model in (Service,Source,SourceVersion,Chunk))


@pytest.mark.parametrize('change',['reviewed','rejected','archived','metadata','content','private','source_url','deleted_current'])
def test_sync_preserves_human_changes_and_withdrawal(env,change):
    from app.catalogue_sync import sync_public_catalogue
    c,db,*_=env;setup_imports(db)
    service=db.scalar(select(Service).where(Service.slug=='team-nafiew-janun-pass-001'))
    source=db.scalar(select(Source).where(Source.service_id==service.id))
    version=db.get(SourceVersion,source.current_version)
    if change=='reviewed':version.status='verified';version.verified_at=now()
    elif change=='rejected':version.status='rejected'
    elif change=='archived':service.status='archived'
    elif change=='metadata':service.description_bn='My manually edited service'
    elif change=='content':version.content='My manually edited evidence'
    elif change=='private':source.title='Private admin source'
    elif change=='source_url':source.url='https://example.gov.bd/manually-corrected'
    else:source.current_version=None
    db.commit()
    before=(service.status,service.description_bn,source.current_version,version.content,version.status)
    report=sync_public_catalogue(db)
    assert service.slug in report['protected']
    assert before==(service.status,service.description_bn,source.current_version,version.content,version.status)


def test_sync_does_not_resurrect_a_withdrawn_synced_record(env):
    from app.catalogue_sync import sync_public_catalogue
    c,db,*_=env;sync_public_catalogue(db)
    service=db.scalar(select(Service).where(Service.slug=='team-nafiew-janun-pass-001'))
    service.status='archived';db.commit()
    sync_public_catalogue(db)
    assert c.get('/api/services/'+service.slug).status_code==404


def test_sync_preserves_renamed_withdrawn_record_and_category_edits(env):
    from app.catalogue_sync import sync_public_catalogue
    c,db,*_=env;sync_public_catalogue(db)
    original='team-nafiew-janun-pass-001'
    service=db.scalar(select(Service).where(Service.slug==original))
    service.slug='my-edited-passport';service.status='archived'
    category=db.get(Category,'education');category.name_bn='My custom education'
    db.commit();report=sync_public_catalogue(db)
    assert original in report['protected']
    assert not db.scalar(select(Service).where(Service.slug==original))
    assert service.status=='archived'
    assert category.name_bn=='My custom education'
