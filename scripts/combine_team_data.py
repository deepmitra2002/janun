"""Build a lossless, namespaced team catalogue from the five supplied archives."""
import csv,io,json,hashlib,re,zipfile,argparse
from pathlib import Path

def build(folder):
 records=[];packages=[]
 for p in sorted(Path(folder).glob('*.zip')):
  owner=next((v for k,v in [('Nafiew','Nafiew'),('deep_health','Deep'),('National','Sachin'),('tammam','Tammam'),('sami','Sami')] if k in p.name),None)
  if not owner:continue
  pkg={'owner':owner,'filename':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'tables':[]};packages.append(pkg)
  with zipfile.ZipFile(p) as z:
   if owner=='Sachin':
    data=json.loads(z.read('Janun-National-Data-Pack/janun-data.json'))
    for r in data['services']:
     records.append({'id':'sachin:'+r['service']['slug'],'owner':owner,'table':'services','original_id':r['service']['slug'],'name':r['service']['name_bn'],'name_en':r['service']['name_en'],'kind':'service','payload':r,'import_enabled':r['import_enabled']})
    for n in ['office-directory.json','geography.json','provider-service-areas.json','service-master-v2.json','record-relationships.json','coverage.json']:
     value=json.loads(z.read('Janun-National-Data-Pack/'+n));items=value if isinstance(value,list) else value.get('offices',value.get('districts',value.get('services',[value])))
     for i,r in enumerate(items): records.append({'id':f'sachin:{n}:{i}','owner':owner,'table':n,'original_id':str(i),'name':r.get('office_name_bn',r.get('district_bn',r.get('service_id',n))),'name_en':'','kind':'reference','payload':r,'import_enabled':False})
    continue
   for n in sorted(z.namelist()):
    if not n.endswith('.csv') or any(s in Path(n).parts for s in ['original','originals']):continue
    table=Path(n).stem
    if table.startswith('original_'):continue
    rows=list(csv.DictReader(io.StringIO(z.read(n).decode('utf-8-sig'))));pkg['tables'].append({'path':n,'rows':len(rows)})
    core=(owner=='Nafiew' and table in ['business_services','national_services','passport_services','professional_services','tax_services','transport_services']) or (owner=='Deep' and table=='programs') or (owner=='Tammam' and table=='services') or (owner=='Sami' and table in ['attestation_notary_services','certificates','civil_registration','legal_aid_services','marriage_divorce_services','nid_services','police_services'])
    for i,r in enumerate(rows):
     oid=next((r[k] for k in ['service_id','record_id','certificate_id','facility_id','institution_id','contact_id','source_id'] if r.get(k)),str(i+1))
     name=next((r[k] for k in ['service_name_bn','name_bn','program_bn','facility_name_bn','facility_name_en','institution_bn','contact_name_bn','source_title','title','topic'] if r.get(k)),oid)
     en=next((r[k] for k in ['service_name_en','name_en','program_en','facility_name_en'] if r.get(k)),'')
     records.append({'id':f'{owner.lower()}:{table}:{oid}:{i+1}','owner':owner,'table':table,'original_id':oid,'name':name,'name_en':en,'kind':'service' if core else 'reference','payload':r,'import_enabled':core})
 ids=[r['id'] for r in records];assert len(ids)==len(set(ids))
 names={}
 for r in records:
  if r['kind']=='service':names.setdefault(re.sub(r'\W','',r['name_en'].casefold() or r['name']),[]).append(r['id'])
 duplicates=[v for v in names.values() if len(v)>1]
 return {'format':'janun-team-catalogue-v1','packages':packages,'records':records,'duplicate_candidates':duplicates,'policy':'Uploaded research; source verification labels are preserved, not upgraded to human approval.'}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('folder');p.add_argument('--output',default='backend/data/team-catalogue.json');a=p.parse_args();d=build(a.folder);Path(a.output).write_text(json.dumps(d,ensure_ascii=False));print(json.dumps({'records':len(d['records']),'services':sum(r['kind']=='service' for r in d['records']),'packages':len(d['packages']),'duplicate_groups':len(d['duplicate_candidates'])}))
