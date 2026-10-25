import json
from pathlib import Path
import pytest
from app.checking import compare_official_rules
from app.speech import audio_signature
from app.main import app
from fastapi.testclient import TestClient

fixtures=json.loads((Path(__file__).resolve().parents[2]/'tests/fixtures/scoped-claims.json').read_text())
@pytest.mark.parametrize('case',fixtures)
def test_claim_rules_match_browser_fixtures(case):
    result=compare_official_rules(case['claim'],'team-nafiew-janun-pass-001','en')
    assert (result['status'] if result else 'insufficient')==case['status']

def test_speech_errors_are_honest_when_unconfigured(monkeypatch):
    from app.config import settings
    monkeypatch.setattr(settings,'openai_api_key','')
    with TestClient(app) as c:
        r=c.post('/api/speech/speak',json={'text':'Test fixture','language':'bn'})
        assert r.status_code==503
        assert 'not configured' in r.json()['detail']
        assert r.headers['cache-control']=='no-store'
        assert c.get('/api/capabilities').json()['ai'] is False

def test_audio_signature_validation():
    assert audio_signature(b'\x1aE\xdf\xa3' + b'fixture','audio/webm')
    assert audio_signature(b'RIFF0000WAVE' + b'fixture','audio/wav')
    assert not audio_signature(b'<script>fixture</script>','audio/webm')
