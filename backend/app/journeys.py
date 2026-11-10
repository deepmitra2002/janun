from .models import Service
from .domain import normalize_query
from .public_catalogue import public_services, public_detail

TEMPLATES={
 'study-abroad':{'terms':['study','abroad','বিদেশ','পড়তে','bidesh'],'title':'Prepare to study abroad','slugs':['team-nafiew-janun-pass-001','team-nafiew-janun-travel-auth-001','e-passport','certificate-attestation']},
 'new-baby':{'terms':['baby','birth','newborn','শিশু','জন্ম','jonmo'],'title':'Welcome a new family member','slugs':['team-sami-janun-cr-001','birth-registration']},
 'start-business':{'terms':['business','restaurant','trade','ব্যবসা','bebsha'],'title':'Start a business','slugs':['team-nafiew-janun-biz-tl-001','team-nafiew-janun-tax-001','trade-licence','e-tin']},
 'identity-update':{'terms':['identity','nid','correction','সংশোধন'],'title':'Update identity information','slugs':['team-sami-janun-id-002','team-sami-janun-cr-002','nid-correction','birth-correction']},
}

TITLES_BN={'study-abroad':'বিদেশে পড়াশোনার প্রস্তুতি','new-baby':'জন্ম নিবন্ধনের প্রস্তুতি',
    'start-business':'ব্যবসা শুরুর প্রস্তুতি','identity-update':'পরিচয়ের তথ্য সংশোধনের প্রস্তুতি'}

def plan_journey(db,goal,language):
    bn=language=='bn'
    normalized=normalize_query(goal)
    selected=max(TEMPLATES.items(),key=lambda pair:sum(t in normalized for t in pair[1]['terms']))
    if not any(t in normalized for t in selected[1]['terms']):
        return {'title':'আপনার লক্ষ্য সম্পর্কে আরও বলুন' if bn else 'Tell us more about your goal','steps':[],'gaps':['পড়াশোনা, জন্ম নিবন্ধন, ব্যবসা বা পরিচয় সংশোধন বেছে নিন।' if bn else 'Try studying abroad, welcoming a baby, starting a business, or updating identity information.'],'needs_clarification':True,'notice':'কোনো শর্ত অনুমান করা হয়নি।' if bn else 'No requirements have been inferred.'}
    template=selected[1];steps=[];gaps=[];research=False;seen=set()
    for slug in template['slugs']:
        from .document_release import resolve_slug
        service=db.scalar(public_services().where(Service.slug==slug))
        if not service:service=db.scalar(public_services().where(Service.slug==resolve_slug(slug)))
        if not service:
            gaps.append('প্রাসঙ্গিক সেবার কিছু রেকর্ড বা পর্যালোচিত নির্দেশনা পাওয়া যায়নি।' if bn else f'{slug.replace("-"," ").title()}: reviewed guidance is not available yet.')
            continue
        if service.id in seen:continue
        seen.add(service.id)
        detail=public_detail(db,service)
        if detail.get('review_status')=='supplied_research' or (detail['sources'] and not any(s.get('verified_at') for s in detail['sources'])):
            research=True
            name=service.name_bn if bn else service.name_en
            steps.append({'id':f'research-{service.slug}','label':name+(' — মূল উৎস ও প্রযোজ্য নথি দেখুন; পর্যালোচনা বাকি।' if bn else ' — review the source and applicable documents; independent review pending.'),
                'service':name,'slug':service.slug,'sources':detail['sources'],'depends_on':[]})
            continue
        if not detail['sources']:gaps.append((service.name_bn+': বর্তমান উৎস পর্যালোচনা প্রয়োজন।') if bn else f'{service.name_en}: current source review is needed.');continue
        for i,label in enumerate(detail['steps']):
            steps.append({'id':f'{slug}-{i}','label':label,'service':service.name_bn if language=='bn' else service.name_en,'slug':slug,'sources':detail['sources'],'depends_on':[]})
        if not detail['steps']:gaps.append(service.name_bn+': পর্যালোচক আবেদনের ধাপ সাজাননি।' if bn else f'{service.name_en}: steps have not yet been structured by a reviewer.')
    notice=('এটি প্রস্তুতির শুরু; যোগ্যতা, অনুমোদন বা সম্পূর্ণ পরিকল্পনার নিশ্চয়তা নয়। প্রদর্শনের ক্রম আইনি নির্ভরতা নয়।' if bn else 'Preparation starting points only, not confirmation of eligibility, approval or a complete plan. Display order is not a legal dependency.')
    if research:notice=('গবেষণাভিত্তিক তথ্য; স্বাধীন পর্যালোচনা বাকি। ' if bn else 'Supplied research; independent review pending. ')+notice
    return {'title':TITLES_BN[selected[0]] if bn else template['title'],'steps':steps,'gaps':list(dict.fromkeys(gaps)),'needs_clarification':False,'notice':notice}
