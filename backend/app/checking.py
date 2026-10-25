"""Conservative claim comparison against current, human-published service claims.
User text is data, never instructions. No model call, persistence or content logging.
"""
import re
from .knowledge import service_detail

def split_claims(text):
    return [x.strip() for x in re.split(r'[\n।!?]+',text) if len(x.strip())>=4][:20]

def check_claims(text, detail, language='bn'):
    bn=language=='bn'
    known={x.strip() for key in ('documents','eligibility','steps') for x in detail[key]}
    sources=detail['sources']
    trusted=bool(sources) and not detail['conflicts']
    rows=[]
    for claim in split_claims(text):
        scoped=compare_official_rules(claim,detail.get('slug',''),language)
        if scoped:
            rows.append(scoped)
            continue
        supported=trusted and claim in known
        rows.append({'claim':claim,'status':'supported' if supported else 'insufficient',
            'explanation':('পর্যালোচিত সেবার শর্তের সঙ্গে বক্তব্য হুবহু মিলে। প্রযোজ্যতা নিশ্চিত করুন।' if bn else 'This statement exactly matches a currently reviewed service requirement. Confirm applicability.') if supported else ('দাবিটি সমর্থন বা খণ্ডনের মতো প্রযোজ্য পর্যালোচিত তথ্য নেই।' if bn else 'There is insufficient applicable reviewed evidence to support or contradict this statement.'),
            'evidence':sources[:3],
            'next_step':'বয়স, এলাকা ও আবেদনকারীর ধরন অনুযায়ী মূল উৎসে নিশ্চিত করুন।' if bn else 'Confirm age, location and applicant category with the original authority.'})
    return rows

# Same deliberately bounded concepts as the browser preview. A published service is
# still required by /api/check; these scoped rules do not publish other research.
def compare_official_rules(claim,slug,language='bn'):
    import json,unicodedata
    from pathlib import Path
    data=json.loads((Path(__file__).resolve().parents[1]/'data/evidence-overlay.json').read_text())
    text=unicodedata.normalize('NFC',claim).lower()
    if re.search(r'^(?:is|are|do|does|can)\b|unless|except|যদি',text):return None
    clauses=re.split(r'\band\b|\bbut\b|এবং|কিন্তু|,',text)
    decisions=[]
    for rule in data['rules']:
        if slug not in rule['applies_to']:continue
        def matches(c):
            if rule['concept']=='attestation':return 'attest' in c or any(unicodedata.normalize('NFC',s) in c for s in ['সত্যায়ন','সত্যায়ন'])
            return bool(re.search(r'photo|photograph|ছবি',c) and re.search(r'form|ফরম|ফর্ম|attach|affix|সংযোজন',c))
        relevant=next((c for c in clauses if matches(c)),None)
        if not relevant:continue
        if re.search(r'under\s*6|৬\s*বছর|certificate.*overseas|সনদ.*বিদেশ',text):continue
        negative=bool(re.search(r'not\s+(?:be\s+)?(?:required|mandatory|needed|necessary)|no\s+(?:need|attestation|requirement)|do(?:es)?\s+not\s+need|without\s+attest|লাগে\s*না|লাগবে\s*না|প্রয়োজন\s*(?:হয়\s*)?নেই|প্রয়োজন\s*(?:হয়\s*)?নেই|প্রয়োজন\s*(?:হয়|হবে)\s*না|প্রয়োজন\s*(?:হয়|হবে)\s*না',relevant))
        positive=bool(re.search(r'required|mandatory|must|need|লাগে|লাগবে|বাধ্যতামূলক|প্রয়োজন|প্রয়োজন',relevant))
        if negative or positive:decisions.append((negative,rule))
    if not decisions:return None
    bn=language=='bn';supported=any(x[0] for x in decisions);conflict=any(not x[0] for x in decisions)
    unknown=bool(re.search(r'fee|cost|ফি|টাকা|approval|অনুমোদন|all\s+documents|কোনো\s+কাগজ',text))
    status='partial' if supported and (conflict or unknown) else 'conflict' if conflict else 'supported'
    explanations={'supported':('The scoped statement agrees with the official instruction checked for this update.','নির্দিষ্ট বক্তব্যটি এই আপডেটে দেখা সরকারি নির্দেশনার সঙ্গে মিলে।'),'conflict':('This says the item is required, while the scoped official instruction says it is not required.','দাবিতে এটি প্রয়োজন বলা হয়েছে; প্রযোজ্য সরকারি নির্দেশনায় এর প্রয়োজন নেই বলা আছে।'),'partial':('Only part is supported; another part conflicts or lacks applicable evidence.','একটি অংশ সমর্থিত; অন্য অংশে অমিল আছে অথবা প্রযোজ্য প্রমাণ নেই।')}
    return {'claim':claim,'status':status,'explanation':explanations[status][int(bn)],'evidence':list({r['source']['id']:r['source'] for _,r in decisions}.values()),'rule_excerpts':[r['text_bn' if bn else 'text_en'] for _,r in decisions],'basis':'Specific official page checked; publication review pending.','next_step':'Confirm applicability and subsequent changes with the original authority.' if not bn else 'মূল উৎসে প্রযোজ্যতা ও পরবর্তী পরিবর্তন নিশ্চিত করুন।'}
