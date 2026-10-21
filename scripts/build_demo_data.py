"""Produce an explicitly unverified public demo snapshot, preserving source fields."""
import json,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
x=json.loads((ROOT/'backend/data/team-catalogue.json').read_text())
categories={'business':('Business','ব্যবসা'), 'welfare':('Health & social support','স্বাস্থ্য ও সামাজিক সহায়তা'),'education':('Education & careers','শিক্ষা ও কর্মজীবন'),'identity':('Identity & registration','পরিচয় ও নিবন্ধন'),'legal':('Legal services','আইনি সেবা'),'passport':('Passport','পাসপোর্ট'),'transport':('Transport','পরিবহন'),'tax':('Tax & fees','কর ও ফি'),'land':('Land & property','ভূমি ও সম্পত্তি'),'agriculture':('Agriculture','কৃষি'),'utilities':('Utilities','ইউটিলিটি'),'local-government':('Local government','স্থানীয় সরকার')}
def val(p,*keys):
 return next((p[k] for k in keys if p.get(k)),None)
def items(v):
 if not v:return []
 return [str(a) for a in v] if isinstance(v,list) else [a.strip() for a in str(v).split('\n') if a.strip()]
def urls(v):
 return [u.rstrip('.,)') for u in re.findall(r'https?://[^\s<>";]+',str(v)) if '@' not in u.split('/')[2]]
services=[]
for r in x['records']:
 if r['kind']!='service':continue
 p=r['payload'];s=p.get('service',{});c=p.get('claims',{})
 category=s.get('category') or {'Nafiew':'business','Deep':'welfare','Tammam':'education','Sami':'identity'}[r['owner']]
 for word,cat in [('passport','passport'),('transport','transport'),('tax','tax'),('legal','legal'),('notary','legal'),('police','legal')]:
  if word in r['table']:category=cat
 slug=s.get('slug') or 'team-'+r['owner'].lower()+'-'+re.sub('[^a-z0-9]+','-',r['original_id'].lower()).strip('-')
 links=[]
 for key in ['sources','source_url','source_urls','official_source_url','official_information_url','official_link','application_url','online_application_url']:
  v=p.get(key)
  if isinstance(v,list):
   for a in v:
    if isinstance(a,dict):links+=urls(a.get('url',''))
  else:links+=urls(v or '')
 ids=set(re.split(r'[;,|\s]+',str(val(p,'source_id','source_ids') or '')))
 for ref in x['records']:
  if ref['owner']==r['owner'] and ref['table'] in ['sources','source_catalog'] and ref['payload'].get('source_id') in ids:links+=urls(val(ref['payload'],'url','source_url') or '')
 links=list(dict.fromkeys(links))
 scope=p.get('scope',{})
 scope=scope.get('label_bn') or scope.get('label_en') if isinstance(scope,dict) else scope
 scope=scope or val(p,'geographic_availability','geographic_scope','coverage_area') or 'আওতাভুক্ত এলাকা যাচাই বাকি / Coverage not confirmed'
 notes=items(val(p,'notes_bn','gaps_or_conflicts','missing_information_notes','conflicts_noted','notes'))
 desc=s.get('description_bn') or val(p,'service_description','description') or 'টিমের সংগৃহীত সেবা-তথ্য। মানব যাচাই বাকি।'
 services.append(dict(id=r['id'],slug=slug,name_bn=r['name'],name_en=r['name_en'] or r['name'],category=category,description_bn=desc,description_en=s.get('description_en') or 'Collected team research. Human verification pending.',official_url=s.get('official_url') or val(p,'official_information_url','official_link') or (links[0] if links else ''),status='demo',verification_status='needs_review',last_verified_at=None,owner=r['owner'],scope=scope,notes=notes,eligibility=items(c.get('eligibility') or val(p,'eligibility','eligible_who')),documents=items(c.get('documents') or val(p,'required_documents','documents')),steps=items(c.get('steps') or val(p,'steps','application_procedure','application_method')),fees=c.get('fees') or val(p,'fee_information','govt_fee','fee'),processing_time=c.get('processing_time') or p.get('processing_time') or None,deadline=c.get('deadline') or val(p,'duration_deadline','apply_end'),sources=[dict(id=slug+'-'+str(i),title='Collected source / সংগৃহীত উৎস',url=u,agency='Team research — '+r['owner']) for i,u in enumerate(links)],conflicts=notes,raw_fields=p,search_text=json.dumps(p,ensure_ascii=False)))
assert len({s['slug'] for s in services})==len(services)
used=sorted({s['category'] for s in services})
data={'mode':'unverified_demo','services':services,'categories':[dict(slug=k,name_en=categories.get(k,(k,k))[0],name_bn=categories.get(k,(k,k))[1],icon='FileText') for k in used],'team_records':len(x['records'])}
out=ROOT/'frontend/public/demo-data.json';out.parent.mkdir(exist_ok=True);out.write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')))
print(f'{len(services)} demo records; {len(used)} categories; {out.stat().st_size} bytes')
