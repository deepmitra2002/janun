import json
from datetime import timedelta
import pytest
from sqlalchemy import select
from app import ai
from app.models import Source, SourceVersion, Chunk, now
from app.ingestion import register_version
from app.knowledge import retrieve
from test_api import env, auth


def imported(env):
    _, db, service, _ = env
    source = Source(service_id=service.id, title='Team research: Sachin / birth-fixture',
        agency='Uploaded team research — Sachin', url='https://bdris.gov.bd/')
    db.add(source); db.flush()
    version = register_version(db, source,
        'JANUN EDITORIAL SERVICE SUMMARY — NOT AN ORIGINAL GOVERNMENT DOCUMENT\n'
        'Birth registration fixture: prepare the supplied application summary. Scope: fixture locality only.')
    db.commit()
    return db, source, version, service


def fake_provider(monkeypatch):
    calls = []
    monkeypatch.setattr(ai.settings, 'openai_api_key', 'fixture')
    monkeypatch.setattr(ai.settings, 'llm_model', 'fixture-model')
    monkeypatch.setattr(ai, 'embedding_for', lambda *_: None)
    def generate(payload):
        data = json.loads(payload); calls.append(data)
        return json.dumps({'answer':'CONNECTION_OK' if data['evidence'][0]['id']=='janun-connection-test' else 'Prepare the supplied application summary.',
            'citation_ids':[data['evidence'][0]['id']],
            'sufficient_evidence':True,'needs_clarification':False})
    monkeypatch.setattr(ai, 'generate_answer', generate)
    return calls


def test_existing_team_import_answers_without_publication_and_keeps_status(env, monkeypatch):
    db, source, version, service = imported(env)
    calls = fake_provider(monkeypatch)
    result = ai.chat(db, 'birth registration', 'en')
    assert result['status'] == 'source_explanation_review_pending'
    assert 'review pending' in result['answer'].lower()
    assert result['sources'][0]['review_status'] == 'supplied_research'
    assert result['sources'][0]['verified_at'] is None
    assert calls[0]['evidence'][0]['review_status'] == 'supplied_research'
    assert 'fixture locality' in calls[0]['evidence'][0]['text']
    assert service.status == 'draft' and version.status == 'pending'
    assert retrieve(db, 'birth registration') == []


@pytest.mark.parametrize('state', ['rejected','archived','stale','verified','published'])
def test_unavailable_team_versions_are_never_used(env,monkeypatch,state):
    db, _, version, _ = imported(env)
    version.status = state; db.commit()
    calls = fake_provider(monkeypatch)
    assert ai.chat(db,'birth registration','en')['status'] == 'insufficient_evidence'
    assert calls == []


@pytest.mark.parametrize('field,value', [('status','archived'),('status','superseded')])
def test_withdrawn_service_is_never_used(env,monkeypatch,field,value):
    db, _, _, service = imported(env)
    setattr(service,field,value); db.commit()
    calls = fake_provider(monkeypatch)
    assert ai.chat(db,'birth registration','en')['sources'] == []
    assert calls == []


def test_private_admin_draft_is_not_exposed_as_team_research(env,monkeypatch):
    _, db, _, version = env
    version.content = 'birth registration private admin draft'; db.commit()
    calls = fake_provider(monkeypatch)
    assert ai.chat(db,'birth registration','en')['sources'] == []
    assert calls == []


def test_only_current_team_version_is_searchable(env,monkeypatch):
    db, source, version, _ = imported(env)
    register_version(db,source,'Replacement evidence about an entirely different service.'); db.commit()
    # Names still match, but the retrieved text must be the replacement, never old content.
    calls = fake_provider(monkeypatch)
    ai.chat(db,'birth registration','en')
    assert calls
    assert all('supplied application summary' not in e['text'] for e in calls[0]['evidence'])


def test_expired_previously_reviewed_record_cannot_be_downgraded_into_research(env,monkeypatch):
    db, _, version, _ = imported(env)
    version.status = 'review'; version.verified_at=now()-timedelta(days=40)
    version.review_due=now()-timedelta(days=10); db.commit()
    calls = fake_provider(monkeypatch)
    assert ai.chat(db,'birth registration','en')['sources'] == []
    assert calls == []


def test_fabricated_citation_still_rejects_supplied_answer(env,monkeypatch):
    db, *_ = imported(env)
    fake_provider(monkeypatch)
    monkeypatch.setattr(ai,'generate_answer',lambda _:json.dumps({
        'answer':'Invented answer','citation_ids':['invented'],
        'sufficient_evidence':True,'needs_clarification':False}))
    assert ai.chat(db,'birth registration','en')['status']=='insufficient_evidence'


def test_admin_provider_test_requires_login(env):
    client,*_=env
    assert client.post('/api/admin/ai-test',headers={'origin':'http://localhost:3000','x-janun-request':'1'}).status_code==401


def test_admin_provider_test_is_independent_of_published_data(env,monkeypatch):
    client,*_=env; headers=auth(client)
    calls=fake_provider(monkeypatch)
    response=client.post('/api/admin/ai-test',headers=headers)
    assert response.status_code==200,response.text
    assert response.json()['status']=='connected'
    assert response.json()['provider']=='openai'
    assert calls[0]['evidence'][0]['text']=='JANUN connection test. The test response is CONNECTION_OK.'
    assert 'fixture' not in response.text


def test_admin_provider_failure_is_safe_and_explicit(env,monkeypatch):
    client,*_=env; headers=auth(client)
    fake_provider(monkeypatch)
    def fail(_):raise RuntimeError('secret-provider-key-must-not-be-returned')
    monkeypatch.setattr(ai,'generate_answer',fail)
    response=client.post('/api/admin/ai-test',headers=headers)
    assert response.status_code==503
    assert 'secret-provider' not in response.text
    assert 'provider' in response.json()['detail'].lower()


def test_admin_provider_test_reports_missing_credentials(env,monkeypatch):
    client,*_=env; headers=auth(client)
    monkeypatch.setattr(ai.settings,'openai_api_key','')
    monkeypatch.setattr(ai.settings,'gemini_api_key','')
    monkeypatch.setattr(ai,'generate_answer',lambda _:pytest.fail('Unconfigured provider called'))
    response=client.post('/api/admin/ai-test',headers=headers)
    assert response.status_code==503
    assert 'Render' in response.json()['detail']


def test_admin_provider_test_rejects_invalid_model_response(env,monkeypatch):
    client,*_=env; headers=auth(client)
    fake_provider(monkeypatch)
    monkeypatch.setattr(ai,'generate_answer',lambda _:json.dumps({
        'answer':'Unrelated text','citation_ids':['janun-connection-test'],
        'sufficient_evidence':True,'needs_clarification':False}))
    response=client.post('/api/admin/ai-test',headers=headers)
    assert response.status_code==503


def test_research_fallback_can_be_disabled(env,monkeypatch):
    db,*_=imported(env); calls=fake_provider(monkeypatch)
    monkeypatch.setattr(ai.settings,'chat_use_team_research',False)
    assert ai.chat(db,'birth registration','en')['status']=='insufficient_evidence'
    assert calls==[]


def test_original_import_conflicts_follow_every_retrieved_chunk(env,monkeypatch):
    from app.cli import CATEGORIES
    from app.models import Category
    from app.team_data import import_drafts
    _,db,*_=env
    for slug,en,bn,icon in CATEGORIES:
        if not db.get(Category,slug):db.add(Category(slug=slug,name_en=en,name_bn=bn,icon=icon))
    db.commit();import_drafts(db)
    calls=fake_provider(monkeypatch)
    ai.chat(db,'মাধ্যমিক বিদ্যালয় ভর্তি ফি','bn')
    chunks=[e for e in calls[0]['evidence'] if e['title']=='Team research: Tammam / EDU-002']
    assert chunks
    for chunk in chunks:
        assert chunk['record_metadata']['verification_status']=='conflicting_sources'
        assert 'matching cycle' in chunk['record_metadata']['publication_rule']


def test_optional_embeddings_have_shorter_timeout_than_generation(monkeypatch):
    import httpx
    from openai import OpenAI as RealOpenAI
    monkeypatch.setattr(ai.settings,'openai_api_key','fixture')
    monkeypatch.setattr(ai.settings,'embedding_model','fixture-embedding')
    monkeypatch.setattr(ai.settings,'embedding_dimensions',2)
    def handle(request):
        assert request.extensions['timeout']['read']<=4
        return httpx.Response(200,json={'object':'list','data':[{'object':'embedding','index':0,'embedding':[0.1,0.2]}],'model':'fixture-embedding','usage':{'prompt_tokens':1,'total_tokens':1}})
    monkeypatch.setattr(ai,'OpenAI',lambda **kwargs:RealOpenAI(**kwargs,http_client=httpx.Client(transport=httpx.MockTransport(handle))))
    assert ai.embedding_for('fixture query')==[0.1,0.2]
