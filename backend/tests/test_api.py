import os
os.environ['DATABASE_URL']='sqlite+pysqlite:///:memory:'
from datetime import timedelta
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as DBSession
from sqlalchemy.pool import StaticPool
import pytest
from app.database import Base, get_db
from app.models import Category, Service, Source, SourceVersion, Chunk, Admin, now
from app.security import password_hash
from app.main import app

@pytest.fixture
def env():
 engine=create_engine('sqlite+pysqlite:///:memory:',connect_args={'check_same_thread':False},poolclass=StaticPool)
 Base.metadata.create_all(engine)
 with DBSession(engine,expire_on_commit=False) as db:
  db.add(Category(slug='identity',name_en='Identity',name_bn='পরিচয়'))
  db.add(Admin(username='reviewer',password_hash=password_hash('long-test-password')))
  db.flush()
  svc=Service(slug='birth-registration',name_en='Birth registration',name_bn='জন্ম নিবন্ধন',category='identity',status='draft')
  db.add(svc);db.flush()
  src=Source(service_id=svc.id,url='https://bdris.gov.bd/',title='Test fixture')
  db.add(src);db.flush()
  ver=SourceVersion(source_id=src.id,content='Test evidence for birth registration. This is a test fixture.',content_hash='test')
  db.add(ver);db.flush();src.current_version=ver.id
  db.add(Chunk(version_id=ver.id,text=ver.content,ordinal=0));db.commit()
  app.dependency_overrides[get_db]=lambda:db
  with TestClient(app) as client: yield client,db,svc,ver
  app.dependency_overrides.clear()

def auth(c):
 h={'origin':'http://localhost:3000','x-janun-request':'1'}
 r=c.post('/api/admin/login',json={'username':'reviewer','password':'long-test-password'},headers=h)
 assert r.status_code==200,r.text
 return h

def test_health_and_unpublished_filter(env):
 c,db,svc,ver=env
 assert c.get('/health').status_code==200
 assert c.get('/api/services').json()['total']==0
 assert c.get('/api/services/birth-registration').status_code==404

def test_admin_requires_session_and_csrf(env):
 c,*_=env
 assert c.get('/api/admin/overview').status_code==401
 assert c.post('/api/admin/login',json={'username':'reviewer','password':'long-test-password'}).status_code==403

def test_review_gates_and_stale_filter(env):
 c,db,svc,ver=env;h=auth(c)
 p=f'/api/admin/versions/{ver.id}/review'
 assert c.post(p,json={'status':'published','note':'Reviewed carefully'},headers=h).status_code==409
 for status in ['review','verified','published']:
  r=c.post(p,json={'status':status,'note':'Fixture evidence reviewed','claims':{'steps':['Prepare the test fixture']} if status=='verified' else None},headers=h)
  assert r.status_code==200,r.text
 assert c.post(f'/api/admin/services/{svc.id}/publish',headers=h).status_code==200
 assert c.get('/api/services?q=jonmo').json()['total']==1
 detail=c.get('/api/services/birth-registration').json()
 assert detail['steps']==['Prepare the test fixture']
 ver.review_due=now()-timedelta(days=1);db.commit()
 detail=c.get('/api/services/birth-registration').json()
 assert detail['steps']==[]
 assert detail['sources']==[]

def test_empty_evidence_abstains(env):
 c,*_=env
 r=c.post('/api/chat',json={'question':'passport korte ki lage','language':'en'})
 assert r.status_code==200
 assert r.json()['status']=='insufficient_evidence'
 assert r.json()['sources']==[]

def test_journey_does_not_invent_unpublished_steps(env):
 c,*_=env
 r=c.post('/api/journeys',json={'goal':'new baby','language':'en'})
 assert r.status_code==200
 assert r.json()['steps']==[]
 assert r.json()['gaps']

def test_feedback_validation(env):
 c,*_=env
 assert c.post('/api/feedback',json={'message':'x'}).status_code==422
 assert c.post('/api/feedback',json={'message':'Please add more services'}).status_code==201

def test_invalid_content_length_is_rejected(env):
 c,*_=env
 assert c.post('/api/feedback',json={'message':'A useful suggestion'},headers={'content-length':'invalid'}).status_code==400

def test_chunked_oversized_request_is_rejected(env,monkeypatch):
 from app.config import settings
 c,*_=env
 monkeypatch.setattr(settings,'max_source_bytes',100)
 assert c.post('/api/feedback',content=iter([b'x'*110_000]),headers={'content-type':'application/json'}).status_code==413

def test_directory_summary_requires_current_published_evidence(env):
 c,db,svc,ver=env
 svc.status='published';db.commit()
 row=c.get('/api/services').json()['items'][0]
 assert row['verification_status']=='needs_review'
 assert row['last_verified_at'] is None
 ver.status='published';ver.verified_at=now();ver.review_due=now()+timedelta(days=5);db.commit()
 row=c.get('/api/services').json()['items'][0]
 assert row['verification_status']=='current'
 assert row['source_count']==1
 assert row['last_verified_at']
 ver.review_due=now()-timedelta(seconds=1);db.commit()
 assert c.get('/api/services').json()['items'][0]['source_count']==0

def test_directory_validates_categories_and_searches_descriptions(env):
 c,db,svc,ver=env
 svc.status='published';svc.description_en='A newborn registration guide';db.commit()
 assert c.get('/api/services',params={'q':'  newborn  '}).json()['total']==1
 assert c.get('/api/services',params={'q':'  '}).json()['total']==1
 assert c.get('/api/services',params={'q':'%_'}).json()['total']==0
 assert c.get('/api/services?category=not-real').status_code==404
 assert c.get('/api/categories/not-real/services').status_code==404
 assert c.get('/api/categories/identity/services').json()['total']==1
