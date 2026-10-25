import os
os.environ['DATABASE_URL']='sqlite+pysqlite:///:memory:'
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import Mock
import json
import pytest
from sqlalchemy import create_engine,select
from sqlalchemy.orm import Session
from app.database import Base
from app.models import Category,Service,Source,SourceVersion,Chunk,now
from app.ingestion import register_version
from app import ai

@pytest.fixture
def record():
 engine=create_engine('sqlite+pysqlite:///:memory:');Base.metadata.create_all(engine)
 with Session(engine,expire_on_commit=False) as db:
  db.add(Category(slug='identity',name_en='Identity',name_bn='পরিচয়'));db.flush()
  svc=Service(slug='birth-registration',name_en='Birth',name_bn='জন্ম',category='identity',status='published');db.add(svc);db.flush()
  src=Source(service_id=svc.id,url='https://bdris.gov.bd/',title='Fixture');db.add(src);db.flush()
  a=register_version(db,src,'A: this is an official source test fixture, not real government guidance.')
  a.status='published';a.verified_at=now();a.review_due=now()+timedelta(days=30);db.commit()
  yield db,src,a,svc

def test_source_recurrence_requires_new_review(record):
 db,src,a,svc=record
 b=register_version(db,src,'B: changed test fixture content, not real government guidance.')
 b.status='published';b.review_due=now()+timedelta(days=30);db.commit()
 reverted=register_version(db,src,a.content);db.commit()
 assert src.current_version==reverted.id
 assert reverted.id!=a.id
 assert reverted.status=='pending'
 assert b.status=='stale'

def provider(monkeypatch,record,result):
 db,src,a,svc=record;chunk=db.scalar(select(Chunk).where(Chunk.version_id==a.id))
 monkeypatch.setattr(ai,'retrieve',lambda *args:[(chunk,a,src,svc)])
 monkeypatch.setattr(ai,'embedding_for',lambda *args:None)
 monkeypatch.setattr(ai.settings,'openai_api_key','fixture')
 monkeypatch.setattr(ai.settings,'llm_model','fixture')
 result['citation_ids']=[chunk.id if x=='VALID' else x for x in result['citation_ids']]
 fake=SimpleNamespace(responses=SimpleNamespace(create=lambda **kw:SimpleNamespace(output_text=json.dumps(result))))
 monkeypatch.setattr(ai,'client',lambda:fake)
 return ai.chat(db,'What do I need?','en')

def test_any_fabricated_citation_rejects_entire_answer(monkeypatch,record):
 result=provider(monkeypatch,record,{'answer':'An unsupported fee is 999.','citation_ids':['VALID','invented'],'sufficient_evidence':True,'needs_clarification':False})
 assert result['status']!='answered'

def test_string_boolean_is_not_accepted(monkeypatch,record):
 result=provider(monkeypatch,record,{'answer':'Wrong type','citation_ids':['VALID'],'sufficient_evidence':'false','needs_clarification':'false'})
 assert result['status']!='answered'

def test_clarification_is_preserved(monkeypatch,record):
 result=provider(monkeypatch,record,{'answer':'Which applicant category applies to you?','citation_ids':[],'sufficient_evidence':False,'needs_clarification':True})
 assert result['needs_clarification'] is True
 assert 'applicant category' in result['answer']

def test_oversized_robots_is_rejected_before_document(monkeypatch):
 from app import ingestion
 monkeypatch.setattr(ingestion,'validate_public_url',lambda url:'8.8.8.8')
 class Response:
  status_code=200;headers={'content-type':'text/plain'}
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def iter_bytes(self):yield b'x'*300_000
 class Client:
  calls=[]
  def __init__(self,*args,**kwargs):pass
  def __enter__(self):return self
  def __exit__(self,*args):pass
  def stream(self,method,url,**kwargs):self.calls.append(url);return Response()
 monkeypatch.setattr(ingestion.httpx,'Client',Client)
 with pytest.raises(ValueError,match='size limit'):ingestion.fetch_source('https://bdris.gov.bd/')
 assert len(Client.calls)==1
