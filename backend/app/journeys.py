from sqlalchemy import select
from .models import Service
from .knowledge import service_detail
from .domain import normalize_query

TEMPLATES={
 'study-abroad':{'terms':['study','abroad','বিদেশ','পড়তে','bidesh'],'title':'Prepare to study abroad','slugs':['e-passport','certificate-attestation','police-clearance']},
 'new-baby':{'terms':['baby','birth','newborn','শিশু','জন্ম','jonmo'],'title':'Welcome a new family member','slugs':['birth-registration']},
 'start-business':{'terms':['business','restaurant','trade','ব্যবসা','bebsha'],'title':'Start a business','slugs':['trade-licence','e-tin']},
 'identity-update':{'terms':['identity','nid','correction','সংশোধন'],'title':'Update identity information','slugs':['nid-correction','birth-correction']},
}

def plan_journey(db,goal,language):
    normalized=normalize_query(goal)
    selected=max(TEMPLATES.items(),key=lambda pair:sum(t in normalized for t in pair[1]['terms']))
    if not any(t in normalized for t in selected[1]['terms']):
        return {'title':'Tell us more about your goal','steps':[],'gaps':['Try studying abroad, welcoming a baby, starting a business, or updating identity information.'],'needs_clarification':True,'notice':'No requirements have been inferred.'}
    template=selected[1];steps=[];gaps=[]
    for slug in template['slugs']:
        service=db.scalar(select(Service).where(Service.slug==slug,Service.status=='published'))
        if not service:gaps.append(f'{slug.replace("-"," ").title()}: reviewed guidance is not available yet.');continue
        detail=service_detail(db,service)
        if not detail['sources']:gaps.append(f'{service.name_en}: current source review is needed.');continue
        for i,label in enumerate(detail['steps']):
            steps.append({'id':f'{slug}-{i}','label':label,'service':service.name_bn if language=='bn' else service.name_en,'slug':slug,'sources':detail['sources'],'depends_on':[f'{slug}-{i-1}'] if i else []})
        if not detail['steps']:gaps.append(f'{service.name_en}: steps have not yet been structured by a reviewer.')
    return {'title':template['title'],'steps':steps,'gaps':gaps,'needs_clarification':False,'notice':'These are potentially relevant services. Applicability depends on your circumstances. This is a preparation checklist, not confirmation of eligibility or a submitted application. Cross-service dependencies have not been assumed.'}
