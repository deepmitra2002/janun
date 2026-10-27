from uuid import uuid4
import asyncio
from fastapi import FastAPI,Depends,HTTPException,Query,Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import select,or_,func,text,false
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session as DBSession
from .config import settings
from .database import get_db
from .models import Category,Service,Feedback,Source,SourceVersion,now
from .schemas import ChatInput,FeedbackInput,JourneyInput
from .knowledge import service_detail
from .domain import normalize_query
from .security import limiter
from .admin import router as admin_router,service_json
from .ai import chat
from .journeys import plan_journey

app=FastAPI(title='Janun API',version='0.1.0',docs_url='/docs' if settings.environment!='production' else None,redoc_url=None)
app.add_middleware(CORSMiddleware,allow_origins=settings.origins,allow_credentials=True,allow_methods=['GET','POST','PUT'],allow_headers=['Content-Type','X-Janun-Request'])
app.include_router(admin_router)
from .speech import router as speech_router
app.include_router(speech_router)

@app.middleware('http')
async def security_headers(request:Request,call_next):
    limit=settings.max_source_bytes+100_000
    try:
        length=int(request.headers.get('content-length','0') or 0)
        if length<0:raise ValueError()
    except ValueError:return JSONResponse({'detail':'Invalid content length'},status_code=400)
    if length>limit:return JSONResponse({'detail':'Request too large'},status_code=413)
    if request.method in ('POST','PUT','PATCH'):
        body=bytearray()
        try:
            async with asyncio.timeout(20):
                async for block in request.stream():
                    body.extend(block)
                    if len(body)>limit:return JSONResponse({'detail':'Request too large'},status_code=413)
        except TimeoutError:return JSONResponse({'detail':'Request timed out'},status_code=408)
        # Starlette's cached request replays the bounded body to the downstream parser.
        request._body=bytes(body)
    response=await call_next(request)
    response.headers['X-Content-Type-Options']='nosniff'
    response.headers['X-Frame-Options']='DENY'
    response.headers['Referrer-Policy']='strict-origin-when-cross-origin'
    if request.url.path.startswith('/api/admin') or request.url.path in ('/api/chat','/api/check') or request.url.path.startswith('/api/speech'):response.headers['Cache-Control']='no-store'
    return response

@app.exception_handler(SQLAlchemyError)
async def db_error(request,exc):return JSONResponse({'detail':'Database temporarily unavailable. Please try again.'},status_code=503)

@app.get('/health')
def health():return {'status':'ok','service':'janun'}

@app.get('/ready')
def ready(db:DBSession=Depends(get_db)):
    db.execute(text('SELECT 1'));return {'status':'ready'}

@app.get('/api/categories')
def categories(db:DBSession=Depends(get_db)):
    return [{'slug':c.slug,'name_en':c.name_en,'name_bn':c.name_bn,'icon':c.icon} for c in db.scalars(select(Category).order_by(Category.name_en))]

@app.get('/api/services')
def services(q:str=Query(default='',max_length=200),category:str=Query(default='',max_length=80),page:int=Query(default=1,ge=1),page_size:int=Query(default=12,ge=1,le=50),db:DBSession=Depends(get_db),sort:str=Query(default='name',pattern='^(name|name_desc)$')):
    stmt=select(Service).where(Service.status=='published')
    if category:
        if not db.get(Category,category):raise HTTPException(404,'Category not found')
        stmt=stmt.where(Service.category==category)
    q=q.strip()
    if q:
        terms=[t.replace('%','').replace('_','') for t in normalize_query(q).split()]
        terms=[t for t in terms if t]
        columns=(Service.name_en,Service.name_bn,Service.description_en,Service.description_bn)
        stmt=stmt.where(or_(*[column.ilike('%'+t+'%') for t in terms for column in columns]) if terms else false())
    total=db.scalar(select(func.count()).select_from(stmt.subquery()))
    records=list(db.scalars(stmt.order_by(Service.name_en.desc() if sort=='name_desc' else Service.name_en,Service.id).offset((page-1)*page_size).limit(page_size)))
    evidence={s.id:[] for s in records}
    if records:
        rows=db.execute(select(Source,SourceVersion).join(SourceVersion,Source.current_version==SourceVersion.id).where(Source.service_id.in_(evidence),SourceVersion.status=='published',SourceVersion.review_due>now()))
        for source,version in rows:evidence[source.service_id].append((source,version))
    items=[]
    for service in records:
        sources=evidence[service.id]
        dates=[v.verified_at for _,v in sources if v.verified_at]
        items.append({**service_json(service),'status':'source_confirmed_document' if any(v.claims.get('document_update') for _,v in sources) else service.status,'verification_status':'current' if dates else 'needs_review','source_count':len(sources),'last_verified_at':max(dates).isoformat() if dates else None,'authorities':sorted({s.agency for s,_ in sources if s.agency})})
    return {'items':items,'total':total,'page':page,'page_size':page_size}

@app.get('/api/categories/{slug}/services')
def category_services(slug:str,db:DBSession=Depends(get_db)):
    if not db.get(Category,slug):raise HTTPException(404,'Category not found')
    return services('',slug,1,50,db)

@app.get('/api/services/{slug}')
def detail(slug:str,db:DBSession=Depends(get_db)):
    from .document_release import resolve_slug
    slug=resolve_slug(slug)
    obj=db.scalar(select(Service).where(Service.slug==slug,Service.status=='published'))
    if not obj:raise HTTPException(404,'This service is not published yet')
    return service_detail(db,obj)

@app.post('/api/chat')
def ask(data:ChatInput,request:Request,db:DBSession=Depends(get_db)):
    limiter.check('chat:'+request.client.host,20,60)
    return {**chat(db,data.question,data.language,[x.model_dump() for x in data.history]),'request_id':str(uuid4())}

@app.post('/api/journeys')
def journey(data:JourneyInput,request:Request,db:DBSession=Depends(get_db)):
    limiter.check('journey:'+request.client.host,30,60)
    return plan_journey(db,data.goal,data.language)

@app.post('/api/feedback',status_code=201)
def feedback(data:FeedbackInput,request:Request,db:DBSession=Depends(get_db)):
    limiter.check('feedback:'+request.client.host,5,60)
    db.add(Feedback(**data.model_dump()));db.commit();return {'message':'Thank you. Your feedback has been recorded.'}

from .schemas import CheckInput
from .checking import check_claims

@app.post('/api/check')
def information_check(data:CheckInput,request:Request,db:DBSession=Depends(get_db)):
    limiter.check('check:'+request.client.host,20,60)
    service=db.scalar(select(Service).where(Service.slug==data.service_slug,Service.status=='published'))
    if not service:raise HTTPException(404,'This service is not published yet')
    return {'claims':check_claims(data.text,service_detail(db,service),data.language),
        'notice':'Information comparison only. This does not authenticate documents.',
        'request_id':str(uuid4())}

@app.get('/api/capabilities')
def capabilities():
    return {'ai':settings.ai_configured,'speech_transcription':bool(settings.openai_api_key and settings.speech_transcription_model),'speech_synthesis':bool(settings.openai_api_key and settings.speech_synthesis_model),'chat_uses_team_research':settings.chat_use_team_research,'review_policy':'Reviewed sources preferred; existing source-linked team imports may be explained with review-pending labels. Withdrawn records are excluded.'}
