"""Reproduce the user-authorized five-document release, retaining full provenance.

Reads DOCX XML including table cells, hyperlinks and embedded images. Original
research is retained; explicit semantic mappings replace fields, never guessed
URL-based matches. No source-confirmed statement implies a complete service.
"""
from pathlib import Path
import hashlib,json,re,zipfile
from lxml import etree as ET

ROOT=Path(__file__).resolve().parents[1]
INPUT=ROOT/'research/documents-2026-10-25'
EVIDENCE=ROOT/'public/evidence/documents-2026-10-25'
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','a':'http://schemas.openxmlformats.org/drawingml/2006/main','r':'http://schemas.openxmlformats.org/officeDocument/2006/relationships'}
DATE='2026-10-25'
def unique(items):return list(dict.fromkeys(v for v in items if v))
def urls(text):return unique(u.rstrip(').,،') for u in re.findall(r'https?://(?:(?!https?://)[^\s<>"()])+',text))
def save(path,data):path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,ensure_ascii=False,indent=2))

def extract(number):
 path=INPUT/f'{number}.docx';raw=path.read_bytes()
 with zipfile.ZipFile(path) as z:
  rels={r.get('Id'):r.get('Target') for r in ET.fromstring(z.read('word/_rels/document.xml.rels'))}
  media={};assets=[]
  for name in z.namelist():
   if name.startswith('word/media/'):
    content=z.read(name);digest=hashlib.sha256(content).hexdigest();filename=f'doc-{number}-{digest[:16]}{Path(name).suffix}'
    EVIDENCE.mkdir(parents=True,exist_ok=True);(EVIDENCE/filename).write_bytes(content)
    media[name]='/evidence/documents-2026-10-25/'+filename
    assets.append({'url':media[name],'sha256':digest,'original_path':name})
  def paragraph(p):
   images=[]
   for drawing in p.xpath('.//a:blip',namespaces=NS):
    target=rels.get(drawing.get('{'+NS['r']+'}embed'),'')
    key='word/'+target
    if key in media:images.append(media[key])
   text=''.join((node.text or '') if node.tag=='{'+NS['w']+'}t' else '\n' if node.tag=='{'+NS['w']+'}br' else '\t' if node.tag=='{'+NS['w']+'}tab' else '' for node in p.iter()).strip()
   return {'text':text,'links':unique(rels.get(a.get('{'+NS['r']+'}id')) for a in p.xpath('.//w:hyperlink',namespaces=NS)),'images':images}
  body=ET.fromstring(z.read('word/document.xml')).find('w:body',NS)
  paras=[paragraph(p) for p in body.findall('w:p',NS)]
  tables=[[[[paragraph(p) for p in c.findall('w:p',NS)] for c in r.findall('w:tc',NS)] for r in t.findall('w:tr',NS)] for t in body.findall('w:tbl',NS)]
 result={'filename':path.name,'sha256':hashlib.sha256(raw).hexdigest(),'paragraphs':paras,'tables':tables,'assets':assets,'hyperlinks':unique(v for v in rels.values() if v.startswith(('https://','http://')))}
 save(INPUT/f'{number}-extracted.json',result)
 return result

def source(url,title,agency,preview=None):
 return {'id':hashlib.sha256((url+title).encode()).hexdigest()[:24],'url':url,'title':title,'agency':agency,'review_status':'source_confirmed_document','checked_at':DATE,**({'local_preview':preview} if preview else {})}
records=[];mappings=[];internal=[]
def record(doc,key,slug,bn,en,category,facts,links,scope,authority='',english=None,notes=None,images=None,documents=None,steps=None,eligibility=None,fees=None,time=None,deadline=None,aliases=None):
 facts=[x.strip() for x in facts if x.strip()];links=unique(links)
 r={'id':'document-'+slug,'slug':slug,'name_bn':bn,'name_en':en,'category':category,'description_bn':(facts[0].split('।')[0].rstrip('.। ')+('।' if re.search('[\u0980-\u09ff]',facts[0]) else '.')) if facts else bn,'description_en':((english or [en])[0].split('. ')[0]+'.'),'official_url':links[0] if links else '', 'status':'source_confirmed_document','verification_status':'needs_review','last_verified_at':None,'source_confirmed_at':DATE,'owner':{1:'Nafiew',2:'Deep',3:'Tammam',4:'Sami',5:'Sachin'}[doc],'scope':scope,'notes':notes or [],'conflicts':notes or [],'documents':documents or [],'steps':steps or [],'eligibility':eligibility or [],'fees':fees,'processing_time':time,'deadline':deadline,'sources':[source(u,bn+' — '+('মূল PDF' if '.pdf' in u.lower() else 'মূল উৎস'),authority,(images or [None])[0] if i==0 else None) for i,u in enumerate(links)],'document_update':{'release':'five-documents-2026-10-25','document':f'{doc}.docx','record_keys':[key],'facts_bn':facts,'facts_en':english or [],'evidence_images':images or [],'source_date':scope,'independent_review':'pending','translation_status':'provided' if english else 'Bangla source; English translation not supplied'},'raw_fields':{},'aliases':aliases or []}
 checked='2026-10-24' if doc==2 else None if doc==1 else DATE
 r['source_confirmed_at']=checked
 for s in r['sources']:
  if checked:s['checked_at']=checked
  else:s.pop('checked_at',None)
 r['raw_fields']={'document':f'{doc}.docx','record':key,'authority':authority,'source_scope':scope,'source_confirmed_at':checked,'imported_at':DATE,'facts':facts,'limitations':notes or []}
 r['search_text']=' '.join([bn,en,scope,*facts,*(english or [])]);records.append(r);mappings.append({'document':doc,'record':key,'slug':slug,'aliases':aliases or []});return r

def parse_bounded(d,number):
 p=d['paragraphs'];starts=[]
 for i,a in enumerate(p):
  if not re.match(r'^\d+\s+',a['text']):continue
  if number==2 and i+1<len(p) and p[i+1]['text'].startswith('প্রযোজ্য উৎস'):starts.append(i)
  if number in (3,5) and i+2<len(p) and (p[i+2]['text'].startswith(('EDU-','SCH-','JOB-','Authority'))):starts.append(i)
 result=[]
 for j,start in enumerate(starts):
  end=starts[j+1] if j+1<len(starts) else len(p)
  block=p[start:end]
  for n,x in enumerate(block):
   if x['text'] in ['Main Source URL তালিকা','Original source PDF index']:block=block[:n];break
  result.append(block)
 return result

def main():
 global records
 docs={n:extract(n) for n in range(1,6)}
 # Document 1: all 37 rows, of which four are internal data operations.
 map1={1:['team-nafiew-janun-pass-001','team-nafiew-janun-pass-002','team-nafiew-janun-pass-003','passport-applicant-documents','passport-fees-payment','passport-enrolment','team-nafiew-janun-pass-008','document-attestation-apostille','team-nafiew-janun-travel-visa-001','expatriate-welfare-support'],2:['team-nafiew-janun-tr-dl-001','driving-test-smart-licence','team-nafiew-janun-tr-dl-004','team-nafiew-janun-tr-dl-005','team-nafiew-janun-tr-veh-001','team-nafiew-janun-tr-veh-002','vehicle-fitness-tax-token','brta-service-complaints'],3:['team-nafiew-janun-tax-001','team-nafiew-janun-tax-002','team-nafiew-janun-tax-003','team-nafiew-janun-tax-004','team-nafiew-janun-tax-005','team-nafiew-janun-biz-001','business-licensing-routes','professional-registration-councils','sme-government-support','business-licence-renewal'],4:['national-service-directory','ministry-directorate-directory','national-application-portals','team-nafiew-janun-nat-grs-001','emergency-disaster-directory']}
 for t in range(1,5):
  for i,row in enumerate(docs[1]['tables'][t][1:],1):
   cells=['\n'.join(p['text'] for p in c if p['text']) for c in row]
   if t==4 and i>5:internal.append({'document':'1.docx','table':t,'row':i,'cells':cells});continue
   heading=cells[0].split('\n');bn=re.sub(r'^[কখগঘ]\.\S+\s*','',heading[0]);en=heading[-1].strip('()')
   category={1:'passport',2:'transport',3:'tax' if i<=5 else 'business',4:'legal' if i==4 else 'local-government'}[t]
   authority={1:'DIP / MoFA / relevant authority',2:'BRTA',3:'NBR / RJSC / relevant authority',4:'Government of Bangladesh'}[t]
   facts=cells[1].split('\n')+cells[2].split('\n');ls=unique(urls(cells[3])+[u for c in row for p in c for u in p['links']])
   scope='অক্টোবর ২০২৬ সংগ্রহ; আবেদনকারী, দপ্তর ও এলাকা অনুযায়ী প্রযোজ্য শর্ত নিশ্চিত করুন।'
   notes=[];fee=cells[2] or None
   if (t,i)==(1,4):
    facts=[x.replace('৩. ১৮+ প্রাপ্তবয়স্ক: মূল NID কার্ড বাধ্যতামূলক।','৩. ১৮–২০ বছর: NID অথবা ইংরেজি অনলাইন জন্মনিবন্ধন; ২০ বছরের বেশি দেশে আবেদন: NID। বিদেশের বাংলাদেশ মিশনে অনলাইন জন্মনিবন্ধন গ্রহণযোগ্য।') for x in facts]
    notes.append('1.docx-এর ১৮+ NID শর্তটি সরকারি বয়সভিত্তিক নির্দেশনা অনুযায়ী সংশোধন করা হয়েছে।');ls.append('https://www.bdcgny.org/e-password')
   if (t,i)==(1,8):
    facts=[x for x in facts if 'পুলিশ ক্লিয়ারেন্স' not in x and 'PCC' not in x];fee=None
    notes.append('পুলিশ ক্লিয়ারেন্স আলাদা সেবায় দেখুন। 1.docx-এর ৫০০ টাকা ও 4.docx-এর ১,৫০০ টাকার মধ্যে বিরোধ আছে; বর্তমান মূল পোর্টাল নিশ্চিত করুন।')
   if (t,i)==(3,3):
    # A budget proposal/indexed source conflicts with the uploaded annual threshold.
    facts=[x for x in facts if not any(w in x for w in ['করমুক্ত আয়ের সীমা','ন্যূনতম কর','বাধ্যতামূলক অনলাইন'])];fee=None
    notes.append('ডকুমেন্টের ২০২৬–২৭ করমুক্ত সীমা ও সর্বজনীন বাধ্যতামূলক দাখিলের দাবি পুনরায় যাচাই প্রয়োজন; নিশ্চিত করহার হিসেবে ব্যবহার করা হয়নি।')
   if (t,i)==(3,5):
    facts=[x for x in facts if 'টার্নওভার সীমা' not in x];fee='নিবন্ধন ফি: বিনামূল্যে — সরবরাহকৃত নথি অনুযায়ী।'
    notes.append('টার্নওভার সীমা ও করহার প্রযোজ্য অর্থবছরের কার্যকর আইন অনুযায়ী নিশ্চিত করতে হবে।')
   if (t,i)==(4,5):
    facts=[x.replace('সেবার সময়: দিনরাত ২৪ ঘণ্টা (২৪/৭ নিরবচ্ছিন্ন)।','জরুরি ও দপ্তরভিত্তিক কল সেন্টারের সেবার সময় এক নয়; সংশ্লিষ্ট কর্তৃপক্ষের সময় নিশ্চিত করুন।') for x in facts]
   r=record(1,f'{t}.{i}',map1[t][i-1],bn,en,category,facts,ls,scope,authority,notes=notes,steps=cells[1].split('\n'),fees=fee)
   # A conflicting or suppressed claim must not survive in readiness questions.
   r['steps']=[x for x in facts if x in cells[1].split('\n')]
   if (t,i)==(1,4):r['steps']=facts[:4]
 # Health and social assistance: selected facts, including embedded images.
 map2=['team-deep-hsf-010','hospital-referral-tarakanda','maternal-child-health-tarakanda','team-deep-hsf-011','team-deep-hsf-005','team-deep-hsf-012','team-deep-hsf-001','team-deep-hsf-002','team-deep-hsf-006','team-deep-hsf-007','food-friendly-family-selection','team-deep-hsf-016','team-deep-hsf-014']
 names2=['Hospital services — Aditmari','Outpatient referral — Tarakanda','Maternal and child care — Tarakanda','Family planning counselling — cited local charters','Disability assessment and identity card','Medical assistance application for specified diseases','Old-age allowance published eligibility','Widow and husband-deserted allowance','Mother and child benefit programme','Vulnerable Women Benefit eligibility','Food-friendly programme family selection','NHA project rehabilitation','Disaster humanitarian assistance']
 # Main-source list supplies actual PDF URLs absent from printed link labels.
 all2=docs[2]['paragraphs'];idx=next(i for i,p in enumerate(all2) if p['text']=='Main Source URL তালিকা');source_list={}
 for p in all2[idx+1:]:
  if re.match(r'^\d+ ',p['text']):n=int(p['text'].split()[0])
  elif urls(p['text']):source_list[n]=urls(p['text'])[0]
 for i,b in enumerate(parse_bounded(docs[2],2),1):
  texts=[p['text'] for p in b];a=texts.index('Information');e=texts.index('Main Source URL');facts=[x for x in texts[a+1:e] if x];scope=texts[1].replace('প্রযোজ্য উৎস','').strip();ls=unique([source_list[i]]+[u for p in b for u in p['links']]);images=[u for p in b for u in p['images']]
  record(2,str(i),map2[i-1],re.sub(r'^\d+\s+','',texts[0]),names2[i-1],'health' if i<=4 else 'welfare',facts,ls,scope,notes=['নির্দিষ্ট প্রকাশিত উৎসের তথ্য; স্থানীয় চার্টার সারা দেশের নিয়ম নয়।' if i<=4 else 'নির্বাচন, স্থানীয় যাচাই ও প্রযোজ্য নির্দেশিকা সাপেক্ষে; আবেদন খোলা থাকার নিশ্চয়তা নয়।'],images=images)
 # Education: record identifiers differ from the old CSV IDs, map by meaning.
 map3=['team-tammam-edu-009','team-tammam-edu-010','nu-professional-admission-2027','team-tammam-edu-018','public-diploma-revised-fees-2026','team-tammam-edu-021','team-tammam-sch-004','team-tammam-sch-008','brac-academic-merit-scholarship','team-tammam-job-011','team-tammam-job-007']
 for i,b in enumerate(parse_bounded(docs[3],3),1):
  tx=[p['text'] for p in b];a=tx.index('নিশ্চিত তথ্য');e=tx.index('Confirmed information');last=next(j for j in range(e+1,len(tx)) if tx[j].startswith('Main official source URL'))
  ls=unique([u for p in b for u in p['links']]+[u for p in b for u in urls(p['text'])]);main=next((urls(t)[0] for t in tx if t.startswith('Main official source URL')),None);ls=unique([main]+ls)
  scope=' | '.join(t for t in tx[2:a] if t);facts=tx[a+1:e];english=tx[e+1:last-1];notes=[tx[last-1]];images=[u for p in b for u in p['images']]
  r=record(3,tx[2].split('|')[0].strip(),map3[i-1],re.sub(r'^\d+\s+','',tx[0]),tx[1],'education',facts,ls,scope,tx[2].split('|')[-1].strip(),english,notes,images)
  r['document_update']['evidence_locations']=[t for t in tx if t.startswith('Evidence location')]
  if i==5:r['fees']='অনলাইন আবেদন: ২২০ টাকা; ভর্তি পরীক্ষা: ৩০০ টাকা (এক বা উভয় শিফট), ১ সেপ্টেম্বর ২০২৬ সংশোধনী।'
  if i==6:r.update(fees='প্রতি ডিগ্রি ৫,০০০ টাকা; Pay Order / Bank Draft।',processing_time='৯০–১২০ কর্মদিবস; সময় বাড়তে পারে।')
  if i==10:r['deadline']='১ নভেম্বর ২০২৬ দুপুর ১২টা–৩০ নভেম্বর ২০২৬ সন্ধ্যা ৬টা; প্রযোজ্য User ID-ধারীদের ফি: ৩ ডিসেম্বর সন্ধ্যা ৬টা (বাংলাদেশ সময়)।'
 # Sami's 23 table records; duplicate birth-correction intent is consolidated.
 map4=['team-sami-janun-cr-001','team-sami-janun-cr-002','team-sami-janun-cr-002','team-sami-janun-cr-004','team-sami-janun-cr-005','nid-service-portal','team-sami-janun-id-001','team-sami-janun-id-002','team-sami-janun-id-003','nid-information-help','team-sami-janun-lc-001','team-sami-janun-mr-002','team-sami-janun-dv-001','team-sami-janun-lc-003','name-change-document-routing','team-sami-janun-pl-002','team-sami-janun-pl-001','team-sami-janun-pol-003','team-sami-janun-leg-004','team-sami-janun-nt-001','team-sami-janun-la-001','team-nafiew-janun-nat-grs-001','identity-record-mismatch']
 headings=[p['text'] for p in docs[4]['paragraphs'] if re.match(r'^[AB]\d+ - ',p['text'])]
 alias4={4:['team-sami-janun-cr-003'],5:['team-sami-janun-cr-006'],8:['team-sami-janun-nid-'+str(n).zfill(3) for n in range(5,11)],11:['team-sami-janun-lc-002']}
 for i,(heading,table) in enumerate(zip(headings,docs[4]['tables'][1:]),1):
  cells={''.join(p['text'] for p in row[0]):'\n'.join(p['text'] for p in row[1]) for row in table if len(row)>=2}
  # Preserve paragraph boundaries rather than splitting sentences at abbreviations.
  factrow=next(row for row in table if ''.join(p['text'] for p in row[0])=='Verified information')
  facts=[p['text'] for p in factrow[1] if p['text']];ls=urls(cells['Main official URL'])+urls(cells.get('Additional official sources',''))
  en=heading.split(' - ',1)[1];r=record(4,heading.split(' - ')[0],map4[i-1],en,en,'legal' if i>=16 or i in [12,13] else 'identity',facts,ls,'Bangladesh; local certificates only where covered. Document cut-off 25 October 2026.',cells['Authority'],english=facts,notes=['Local authority, applicant type and cited law determine applicability. Missing fees or checklists have not been inferred.'],aliases=alias4.get(i,[]))
  if i==16:r['fees']=None;r['notes'].append('Fee conflict: 1.docx states Tk 500; 4.docx states Tk 1,500 plus applicable service charge. Confirm the live PCC payment instruction.');r['conflicts']=r['notes'];r['document_update']['facts_bn']=[x for x in facts if 'fee:' not in x];r['document_update']['facts_en']=r['document_update']['facts_bn']
  if i==8:r['fees']='Visible-data correction: Tk 200/300/400 + 15% VAT; other stored information: Tk 100/200/300 + 15% VAT, by correction count — cited 2026 notice.'
  if i==9:r['fees']='Duplicate: normal Tk 200/300/500; urgent Tk 300/500/1,000, plus 15% VAT, by reissue count — cited 2026 notice.'
 # Land/agriculture/utilities: bounded policies must not replace broader unrelated guides.
 map5=['land-application-tracking-complaints','district-land-service-centres','land-acquisition-contingency-policy-2026','aman-seed-flood-support-2026','aman-seedling-flood-support-2026','dhaka-wasa-residential-connection']
 for i,b in enumerate(parse_bounded(docs[5],5),1):
  tx=[p['text'] for p in b];a=tx.index('নিশ্চিত তথ্য');e=tx.index('Confirmed information');last=next(j for j in range(e+1,len(tx)) if tx[j].startswith('Main official source URL'))
  facts=tx[a+1:e];ls=unique([u for p in b for u in urls(p['text'])]+[u for p in b for u in p['links']]);images=[u for p in b for u in p['images']]
  r=record(5,str(i),map5[i-1],re.sub(r'^\d+\s+','',tx[0]),tx[1],'land' if i<=3 else 'agriculture' if i<=5 else 'utilities',facts,ls,' | '.join(tx[2:a]),tx[2].replace('Authority','').strip(),tx[e+1:last-1],[tx[last-1]],images)
  r['document_update']['evidence_locations']=[t for t in tx if t.startswith('Evidence location')]
  if i==6:r.update(fees='আবেদনপত্র ৫৭৫ টাকা (VAT-সহ); মোট সংযোগ খরচ নয়।',processing_time='উদ্ধৃত জোন ১–৪ সনদে ১৪ কর্মদিবস।')
 # Consolidate only an explicit same intent, retaining all incoming provenance.
 merged={}
 for r in records:
  slug=r['slug']
  if slug not in merged:merged[slug]=r;continue
  old=merged[slug]
  # The narrower Sami GRS record supplies the current fields; Nafiew remains evidence.
  winner=r if r['document_update']['document']=='4.docx' else old
  winner['sources']=list({s['url']:s for s in old['sources']+r['sources']}.values())
  winner['document_update']['record_keys']=unique(old['document_update']['record_keys']+r['document_update']['record_keys'])
  winner['document_update']['merged_documents']=unique([old['document_update']['document'],r['document_update']['document']])
  if slug=='team-sami-janun-cr-002':
   winner['document_update']['facts_bn']=unique(old['document_update']['facts_bn']+r['document_update']['facts_bn']);winner['document_update']['facts_en']=winner['document_update']['facts_bn']
  merged[slug]=winner
 records=list(merged.values())
 # Use the original matching English names where this upload has Bangla-only headings.
 original=json.loads((ROOT/'backend/data/team-catalogue.json').read_text())['records']
 names={'team-'+r['owner'].lower()+'-'+re.sub('[^a-z0-9]+','-',r['original_id'].lower()).strip('-'):r['name_en'] for r in original if r['kind']=='service' and r.get('name_en')}
 english_titles={'nid-service-portal':'NID citizen service portal','nid-information-help':'NID account information and help','name-change-document-routing':'Name change by issuing authority','identity-record-mismatch':'Correct mismatched identity records'}
 for r in records:
  if r['document_update']['document']=='4.docx':r['name_en']=names.get(r['slug'],english_titles.get(r['slug'],r['name_en']))
  r['document_update']['evidence_label']='PDF page capture / supplied source screenshot' if r['document_update']['document'] in ['2.docx','3.docx','5.docx'] else 'Illustrative chart / source card'
  if r['slug']=='national-service-directory':r['document_update']['evidence_images']=[a['url'] for a in docs[1]['assets']]
  if r['document_update']['document']=='4.docx':
   domains=['bdris.gov.bd','nidw.gov.bd','pcc.police.gov.bd','gd.police.gov.bd','marriage.gov.bd','prottoyon.gov.bd','nlaso.gov.bd','grs.gov.bd']
   for domain,asset in zip(domains,docs[4]['assets']):
    if any(domain in s['url'] for s in r['sources']):r['document_update']['evidence_images'].append(asset['url'])
 # Corrected September fee revision also applies to the same public diploma route.
 diploma=next(r for r in records if r['slug']=='team-tammam-edu-018')
 revised=next(r for r in records if r['slug']=='public-diploma-revised-fees-2026')
 diploma['fees']=revised['fees'];diploma['sources']+=revised['sources']
 # Explicit checklists use only requirements stated in the new documents.
 checklist={
 'team-nafiew-janun-pass-001':(['প্রিন্ট করা Application Summary ও বারকোডসহ অনলাইন ফরম।','প্রযোজ্য মূল পরিচয়পত্র: ১৮ বছরের কম ইংরেজি অনলাইন জন্মনিবন্ধন; ১৮–২০ NID অথবা জন্মনিবন্ধন; ২০ বছরের বেশি দেশে আবেদন NID, বিদেশের বাংলাদেশ মিশনে জন্মনিবন্ধনও গ্রহণযোগ্য।','পেমেন্ট স্লিপ।','স্বামী/স্ত্রীর নাম যুক্ত করতে চাইলে প্রযোজ্য বিবাহ সনদ।'],[]),
 'team-deep-hsf-005':(['জন্মনিবন্ধন অথবা NID।','স্ক্যান করা স্বাক্ষর, বৈধ মোবাইল নম্বর ও ইমেইল।','নির্ধারিত ডাক্তারি পরীক্ষায় আবেদনের প্রিন্ট কপি।'],[]),
 'team-deep-hsf-012':(['বিশেষজ্ঞের নির্দিষ্ট ছকের মূল প্রত্যয়ন।','সত্যায়িত ব্যবস্থাপত্র বা রিপোর্ট, NID বা জন্মসনদের কপি, ছবি ও রোগীর ঘোষণা।','১৮ বছরের কম বয়সে পিতা, মাতা বা বৈধ অভিভাবকের পরিচয় ও ছবি প্রযোজ্য।'],[]),
 'team-deep-hsf-001':(['জন্মনিবন্ধন বা জাতীয় পরিচিতি নম্বর।'],['বাংলাদেশের স্থায়ী নাগরিক ও সংশ্লিষ্ট এলাকার স্থায়ী বাসিন্দা।','প্রকাশিত উৎসে পুরুষের ন্যূনতম বয়স ৬৫ ও নারীর ৬২; বর্তমান নির্ধারিত বয়স নিশ্চিত করুন।','বাছাই কমিটির নির্বাচন প্রয়োজন।']),
 'team-deep-hsf-006':(['NID, ANC কার্ড এবং নিজের নামে ব্যাংক বা আর্থিক হিসাব।'],['২০২৪ নির্দেশিকা: ২০–৩৫ বছর বয়সী প্রথম বা দ্বিতীয় গর্ভধারণকারী নারী; সংশ্লিষ্ট এলাকায় বসবাস।']),
 'team-tammam-edu-009':(['নিজের মোবাইল নম্বর ও স্ক্যান করা ছবি।','ম্যানুয়ালে প্রযোজ্য বাধ্যতামূলক সংযুক্তি PDF।'],[]),
 'team-tammam-edu-018':(['SSC ফল যাচাই, নিজের মোবাইল নম্বর ও ছবি।'],['উদ্ধৃত ২০২৬–২৭ সরকারি Diploma Engineering: SSC/সমমান ২০২৩–২০২৬; GPA ৩.০০; গণিতে GP ২.০০।']),
 'team-tammam-edu-021':(['সনদ ও transcript, enrollment/on-campus study record, passport/visa এবং syllabus।','প্রযোজ্য thesis/credit-transfer নথি; non-English নথির attested translation।'],['আইন, ফার্মেসি, মেডিকেল ও নার্সিং এই UGC সেবার আওতায় নয়।']),
 'dhaka-wasa-residential-connection':(['ই-আবেদন, আবেদনকারীর ছবি, জমির দলিল অথবা mutation অথবা holding tax copy।','RAJUK অনুমোদিত নকশা, NID ও জমার রসিদ।','ভাড়াটিয়া বা অস্থায়ী আবেদনকারীর ক্ষেত্রে মালিকের ক্ষমতা বা অনাপত্তিপত্র।'],[])
 }
 for r in records:
  if r['slug'] in checklist:r['documents'],r['eligibility']=checklist[r['slug']]
  # Classify only verbatim statements from the replacement document. These
  # remain bounded facts, not a claim that a complete checklist was supplied.
  sentences=[v.strip() for fact in r['document_update']['facts_bn'] for v in re.split(r'(?<=[।])\s*|(?<=\.)\s+(?=[A-Z])',fact) if v.strip()]
  if not r['documents']:
   r['documents']=[v for v in sentences if re.search(r'কাগজপত্র|সংযুক্তিতে|সংযুক্তি.*PDF|প্রয়োজনীয় নথি|প্রয়োজনীয় নথি|পরিচিতি নম্বর থাকতে|supporting evidence|supporting documentation|supporting-document|must provide|Users provide|application collects|form collects|guidance lists records',v,re.I)]
  if not r['eligibility']:
   r['eligibility']=[v for v in sentences if re.search(r'প্রার্থীকে|ন্যূনতম.*বয়স|ন্যূনতম.*বয়স|আবেদনের যোগ্যতা|বয়সী|বয়সী|eligible justice|citizenship.*required',v,re.I)]
  if not r['steps']:
   r['steps']=[v for v in sentences if re.search(r'আবেদন|নিবন্ধন|দাখিল|যাচাই শেষে|appointment|submit|registration|correction.*route|written notice|collect.*identity|online system|portal includes|workflow',v,re.I) and not re.search(r'ফি|fee|টাকা|Tk ',v,re.I)]
  if not r['fees'] and r['slug']!='team-sami-janun-pl-002' and not (r['owner']=='Nafiew' and r['category']=='tax'):
   fees=[v for v in sentences if re.search(r'আবেদন ফি|application fee|প্রতি ডিগ্রির fee',v,re.I)]
   if fees:r['fees']=' '.join(fees)
  if r['slug']=='nu-professional-admission-2027':r['deadline']='১৯ অক্টোবর ২০২৬ বিকাল ৪টা–১৫ নভেম্বর ২০২৬ রাত ১২টা; কলেজে প্রাথমিক ফি ১৬ নভেম্বরের মধ্যে (বাংলাদেশ সময়)।'
  if r['slug']=='dhaka-wasa-residential-connection':r['steps']=['প্রয়োজনীয় তথ্য ও সত্যায়িত প্রমাণপত্র ওয়েবসাইটে আপলোড করুন।','ট্র্যাকিং নম্বর নিয়ে সংশ্লিষ্ট জোনের নির্বাহী প্রকৌশলীর দপ্তরে যোগাযোগ করুন।']
  if r['slug']=='team-tammam-edu-021':r['steps']=['Profile registration করুন।','Original verification-এর appointment নিন।','যাচাই শেষে portal unlock-এর ধাপ সম্পন্ন করুন।']
  more_aliases={
   'passport-applicant-documents':['team-nafiew-janun-pass-006'],
   'driving-test-smart-licence':['team-nafiew-janun-tr-dl-002','team-nafiew-janun-tr-dl-003'],
   'vehicle-fitness-tax-token':['team-nafiew-janun-tr-veh-003','team-nafiew-janun-tr-veh-004']
  }
  r['aliases']=unique(r['aliases']+more_aliases.get(r['slug'],[]))
  r['search_text']=' '.join([r['name_bn'],r['name_en'],r['scope'],*r['document_update']['facts_bn'],*r['document_update']['facts_en']])
 release={'release':'five-documents-2026-10-25','imported_at':DATE,'documents':[{'name':d['filename'],'sha256':d['sha256'],'media_count':len(d['assets'])} for d in docs.values()],'services':records,'mappings':mappings,'internal_operations':internal,'forms_directory':docs[1]['tables'][5],'asset_manifest':[a for d in docs.values() for a in d['assets']]}
 save(ROOT/'backend/data/document-release.json',release)
 save(ROOT/'docs/validation/document-release-manifest.json',{'release':release['release'],'documents':release['documents'],'mappings':mappings,'internal_operations':len(internal),'asset_count':len(release['asset_manifest'])})
 print(f'{len(mappings)} mapped input records -> {len(records)} canonical services; {len(internal)} internal operations; {len(release["asset_manifest"])} evidence images')

if __name__=='__main__':main()
