"""Provider contract tests: real SDK + local HTTP transport, no live keys."""
import json
import httpx
import pytest
from openai import OpenAI as RealOpenAI
from sqlalchemy import select
from app import ai
from app.config import Settings
from app.main import capabilities
from app.models import Chunk
from test_regressions import record


def configure(monkeypatch, **kwargs):
    config = Settings(_env_file=None, openai_api_key='', **kwargs)
    from app import main
    monkeypatch.setattr(ai, 'settings', config)
    monkeypatch.setattr(main, 'settings', config)
    return config


def test_gemini_configuration_uses_its_own_key(monkeypatch):
    config = configure(monkeypatch, llm_provider='gemini', gemini_api_key='fixture', llm_model='fixture-model')
    assert config.ai_configured is True
    assert capabilities()['ai'] is True
    assert capabilities()['speech_synthesis'] is False
    assert 'fixture' not in json.dumps(capabilities())


@pytest.mark.parametrize('provider', ['openai', 'gemini'])
def test_missing_selected_provider_key_does_not_enable_ai(monkeypatch, provider):
    config = configure(monkeypatch, llm_provider=provider, gemini_api_key='fixture' if provider=='openai' else '', llm_model='fixture-model')
    assert config.ai_configured is False


@pytest.mark.parametrize('scenario', ['valid', 'invented_citation', 'malformed', 'rate_limit', 'truncated'])
def test_gemini_chat_preserves_evidence_validation(monkeypatch, record, scenario):
    configure(monkeypatch, llm_provider='gemini', gemini_api_key='fixture-google-key', llm_model='fixture-model')
    db, source, version, service = record
    chunk = db.scalar(select(Chunk).where(Chunk.version_id==version.id))
    monkeypatch.setattr(ai, 'retrieve', lambda *args: [(chunk,version,source,service)])
    calls=[]
    def handle(request):
        calls.append(request)
        assert str(request.url)=='https://generativelanguage.googleapis.com/v1beta/openai/chat/completions'
        assert request.headers['authorization']=='Bearer fixture-google-key'
        body=json.loads(request.content)
        assert body['model']=='fixture-model'
        assert body['response_format']=={'type':'json_object'}
        assert body['messages'][0]['role']=='system'
        payload=json.loads(body['messages'][1]['content'])
        assert payload['response_language']=='bn'
        assert payload['evidence'][0]['id']==chunk.id
        if scenario=='rate_limit':
            return httpx.Response(429,json={'error':{'message':'fixture quota','type':'rate_limit'}})
        result={'answer':'পরীক্ষামূলক উত্তর','citation_ids':[chunk.id if scenario!='invented_citation' else 'invented'], 'sufficient_evidence':True,'needs_clarification':False}
        content='invalid json' if scenario=='malformed' else json.dumps(result)
        return httpx.Response(200,json={'id':'fixture','object':'chat.completion','created':0,'model':'fixture-model','choices':[{'index':0,'message':{'role':'assistant','content':content},'finish_reason':'length' if scenario=='truncated' else 'stop'}]})
    monkeypatch.setattr(ai, 'OpenAI', lambda **kwargs: RealOpenAI(**kwargs,http_client=httpx.Client(transport=httpx.MockTransport(handle))))
    result=ai.chat(db,'passport korte ki lagbe','bn')
    assert calls, 'The selected Gemini provider must be called when reviewed evidence exists.'
    assert (result['status']=='answered') is (scenario=='valid')
    if scenario=='valid':
        assert result['answer']=='পরীক্ষামূলক উত্তর'
        assert result['sources'][0]['id']==chunk.id


def test_no_reviewed_evidence_never_calls_gemini(monkeypatch, record):
    configure(monkeypatch,llm_provider='gemini',gemini_api_key='fixture',llm_model='fixture-model')
    monkeypatch.setattr(ai,'retrieve',lambda *args:[])
    monkeypatch.setattr(ai,'OpenAI',lambda **kwargs:pytest.fail('Provider called without reviewed evidence'))
    assert ai.chat(record[0],'question','en')['status']=='insufficient_evidence'


def test_invalid_provider_rejected():
    with pytest.raises(ValueError):
        Settings(_env_file=None,llm_provider='typo')
