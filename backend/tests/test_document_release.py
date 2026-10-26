from sqlalchemy import select,func
from app.document_release import import_document_release,release
from app.models import Service,Source,SourceVersion,Category
from app.ingestion import register_version
from test_api import env

def test_document_import_replaces_preserves_history_and_is_idempotent(env):
 c,db,*_=env
 db.add(Category(slug='education',name_en='Education',name_bn='শিক্ষা'));db.flush()
 svc=Service(slug='team-tammam-edu-021',name_en='Old equivalence',name_bn='পুরোনো',category='education',status='published');db.add(svc);db.flush()
 old=Source(service_id=svc.id,title='Old source',url='https://ugc.gov.bd/');db.add(old);db.flush()
 version=register_version(db,old,'Old source containing an obsolete fee and checklist.')
 version.status='published';version.claims={'fees':'obsolete fee','documents':['obsolete checklist']};db.commit()
 a=import_document_release(db);assert a['created']==83 and a['replaced']==1
 assert db.get(SourceVersion,version.id).status=='archived'
 detail=c.get('/api/services/team-tammam-edu-021').json()
 assert detail['id']==svc.id and '৫,০০০' in detail['fees']
 assert 'obsolete checklist' not in detail['documents']
 assert detail['document_update']['document']=='3.docx'
 count=db.scalar(select(func.count()).select_from(SourceVersion))
 b=import_document_release(db);assert b['unchanged']==84 and not b['created'] and not b['replaced']
 assert db.scalar(select(func.count()).select_from(SourceVersion))==count
 assert all(v.verified_at is None for v in db.scalars(select(SourceVersion)))
 assert c.get('/api/services/team-sami-janun-nid-005').json()['slug']=='team-sami-janun-id-002'
 assert c.get('/api/services?q=UGC').json()['total']>0

def test_all_release_sources_are_bounded_and_deduplicated():
 rows=release()['services'];assert len(rows)==84
 assert len({r['slug'] for r in rows})==84
 assert all(r['scope'] and r['document_update']['facts_bn'] for r in rows)
 assert next(r for r in rows if r['slug']=='team-sami-janun-pl-002')['fees'] is None
