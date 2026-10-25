from sqlalchemy import select,func
from app.models import Service,SourceVersion,Category
from app.team_data import catalogue,search,import_drafts
from app.cli import CATEGORIES
from test_api import env,auth

def test_all_team_data_present_and_searchable():
 d=catalogue();assert {p['owner'] for p in d['packages']}=={'Nafiew','Deep','Sachin','Tammam','Sami'}
 assert len({r['id'] for r in d['records']})==len(d['records'])
 assert sum(r['kind']=='service' for r in d['records'])==254
 assert search(owner='Deep',table='health_facilities')['total']==816
 assert search(owner='Tammam',kind='service')['total']==43
 assert search(q='পাসপোর্ট',owner='Nafiew')['total']>0
 assert search(page=1,page_size=10)['items']!=search(page=2,page_size=10)['items']

def test_catalogue_requires_login(env):
 c,*_=env
 assert c.get('/api/admin/team-data').status_code==401
 auth(c);r=c.get('/api/admin/team-data?owner=Sachin&kind=service').json();assert r['total']==69
 rid=r['items'][0]['id']
 assert c.get('/api/admin/team-data/record',params={'record_id':rid}).json()['payload']
 assert c.get('/api/admin/team-data?page=0').status_code==422

def test_additive_import_is_idempotent_and_never_publishes(env):
 c,db,*_=env
 for slug,en,bn,icon in CATEGORIES:
  if not db.get(Category,slug):db.add(Category(slug=slug,name_en=en,name_bn=bn,icon=icon))
 db.commit();a=import_drafts(db);assert a['created']==242 and not a['conflicts']
 count=db.scalar(select(func.count()).select_from(Service))
 b=import_drafts(db);assert b['created']==0 and b['skipped']==a['created']
 assert db.scalar(select(func.count()).select_from(Service))==count
 assert c.get('/api/services').json()['total']==0
 assert not db.scalar(select(SourceVersion).where(SourceVersion.status=='published'))
