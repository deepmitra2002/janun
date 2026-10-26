"""Explicit, idempotent import of the owner's five-document release.

Old versions remain in the database. Source-confirmed upload provenance is
distinct from independent verification; verified_at is never fabricated.
"""
import hashlib,json
from datetime import timedelta
from functools import lru_cache
from pathlib import Path
from sqlalchemy import select
from .models import Category,Service,Source,SourceVersion,now
from .ingestion import register_version

@lru_cache(maxsize=1)
def release():
 return json.loads((Path(__file__).resolve().parent.parent/'data/document-release.json').read_text())

def resolve_slug(slug):
 for row in release()['services']:
  if slug in row.get('aliases',[]):return row['slug']
 return slug

def import_document_release(db):
 report={'created':0,'replaced':0,'unchanged':0,'superseded_aliases':0}
 for row in release()['services']:
  if not db.get(Category,row['category']):
   db.add(Category(slug=row['category'],name_en=row['category'].replace('-',' ').title(),name_bn=row['category'],icon='folder'));db.flush()
  service=db.scalar(select(Service).where(Service.slug==row['slug']))
  created=service is None
  if created:service=Service(slug=row['slug']);db.add(service)
  for key in ['name_en','name_bn','category','description_en','description_bn','official_url']:setattr(service,key,row[key])
  service.status='published';db.flush()
  title='Supplied document release: '+release()['release']
  src=db.scalar(select(Source).where(Source.service_id==service.id,Source.title==title))
  if not src:
   src=Source(service_id=service.id,title=title,url=row['official_url'],agency='Owner-supplied source-confirmed documents');db.add(src);db.flush()
  content='OWNER-SUPPLIED SOURCE-CONFIRMED DOCUMENT; INDEPENDENT REVIEW PENDING.\n'+json.dumps(row,ensure_ascii=False,sort_keys=True)
  old=db.get(SourceVersion,src.current_version) if src.current_version else None
  if old and old.content_hash==hashlib.sha256(content.encode()).hexdigest():report['unchanged']+=1;continue
  # Archive superseded evidence from this exact service, retaining every row.
  for previous in db.scalars(select(SourceVersion).join(Source,SourceVersion.source_id==Source.id).where(Source.service_id==service.id,SourceVersion.status=='published')):previous.status='archived'
  version=register_version(db,src,content)
  version.claims={k:row[k] for k in ['steps','documents','eligibility','fees','processing_time','deadline','document_update','scope','conflicts','source_confirmed_at']}
  version.status='published';version.verified_at=None;version.review_due=now()+timedelta(days=30)
  report['created' if created else 'replaced']+=1
  for alias in row.get('aliases',[]):
   previous=db.scalar(select(Service).where(Service.slug==alias))
   if previous and previous.status!='superseded':previous.status='superseded';report['superseded_aliases']+=1
 db.commit();return report
