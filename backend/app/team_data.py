"""Uploaded team research catalogue and additive draft import. No publication decisions."""
import json,hashlib,re
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlsplit
from sqlalchemy import select
from .models import Service,Source,SourceVersion
from .ingestion import register_version

CATALOGUE=Path(__file__).resolve().parent.parent/'data'/'team-catalogue.json'
@lru_cache(maxsize=1)
def catalogue():return json.loads(CATALOGUE.read_text(encoding='utf-8'))

def search(q='',owner='',table='',kind='',page=1,page_size=25):
 data=catalogue();rows=data['records'];tokens=q.casefold().split()
 found=[r for r in rows if (not owner or r['owner']==owner) and (not table or r['table']==table) and (not kind or r['kind']==kind) and all(t in json.dumps(r,ensure_ascii=False).casefold() for t in tokens)]
 items=[{k:v for k,v in r.items() if k!='payload'} for r in found[(page-1)*page_size:page*page_size]]
 return {'items':items,'total':len(found),'page':page,'page_size':page_size,'owners':sorted({r['owner'] for r in rows}),'tables':sorted({r['table'] for r in rows if not owner or r['owner']==owner})}

def urls(value):
 result=[]
 for u in re.findall(r'https://[^\s<>";]+',str(value)):
  u=u.rstrip('.,)');p=urlsplit(u)
  if p.hostname and not p.username and not p.password:result.append(u)
 return result

def prepare(r):
 p=r['payload']
 if r['owner']=='Sachin':
  return p['service'],p['source_upload']['url'],p['source_upload']['content']
 category={'Deep':'welfare','Tammam':'education','Sami':'identity','Nafiew':'business'}[r['owner']]
 if 'legal' in r['table'] or 'police' in r['table'] or 'notary' in r['table']:category='legal'
 if 'passport' in r['table']:category='passport'
 if 'transport' in r['table']:category='transport'
 if 'tax' in r['table']:category='tax'
 links=[]
 for k in ['official_source_url','source_url','official_information_url','application_url','online_application_url','sources']:
  links+=urls(p.get(k,''))
 if not links:
  ids=set(re.split(r'[;,|\s]+',p.get('source_id',p.get('source_ids',''))))
  for a in catalogue()['records']:
   if a['owner']==r['owner'] and a['table'] in ['sources','source_catalog'] and a['payload'].get('source_id') in ids:
    links+=urls(a['payload'].get('url',a['payload'].get('source_url','')))
 if not links:return None
 slug='team-'+r['owner'].lower()+'-'+re.sub(r'[^a-z0-9]+','-',r['original_id'].lower()).strip('-')
 svc={'slug':slug[:120],'name_bn':r['name'][:200],'name_en':(r['name_en'] or r['name'])[:200],'category':category,'description_bn':'টিমের সংগৃহীত তথ্য; প্রকাশের আগে উৎস, প্রযোজ্য এলাকা ও বর্তমানতা যাচাই করুন।','description_en':'Team research awaiting source review.','official_url':links[0]}
 text='JANUN EDITORIAL TEAM RESEARCH — NOT AN ORIGINAL GOVERNMENT DOCUMENT\nOwner: '+r['owner']+'\nOriginal record: '+r['original_id']+'\nTable: '+r['table']+'\nStatus: pending human review; do not infer national applicability.\n'+json.dumps(p,ensure_ascii=False,indent=2)+'\nSource links:\n'+'\n'.join(dict.fromkeys(links))
 return svc,links[0],text

def import_drafts(db):
 report={'created':0,'skipped':0,'needs_source':[],'conflicts':[]}
 for r in catalogue()['records']:
  if not r['import_enabled'] or r['kind']!='service':continue
  item=prepare(r)
  if not item:report['needs_source'].append(r['id']);continue
  spec,url,content=item
  svc=db.scalar(select(Service).where(Service.slug==spec['slug']))
  title='Team research: '+r['owner']+' / '+r['original_id']
  if svc:
   source=db.scalar(select(Source).where(Source.service_id==svc.id,Source.title==title))
   v=db.get(SourceVersion,source.current_version) if source and source.current_version else None
   if v and v.content_hash==hashlib.sha256(content.encode()).hexdigest():report['skipped']+=1
   else:report['conflicts'].append(r['id'])
   continue
  svc=Service(**spec,status='draft');db.add(svc);db.flush()
  source=Source(service_id=svc.id,url=url,title=title[:300],agency='Uploaded team research — '+r['owner']);db.add(source);db.flush()
  register_version(db,source,content);report['created']+=1
 db.commit();return report
