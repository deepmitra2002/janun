from datetime import timedelta
from fastapi import APIRouter,Depends,HTTPException,Request,Response,UploadFile,File
from sqlalchemy import select,func
from sqlalchemy.orm import Session as DBSession
from .database import get_db
from .models import Admin,Session,Category,Service,Source,SourceVersion,Chunk,Audit,Feedback,now
from .schemas import LoginInput,ServiceInput,SourceInput,ReviewInput
from .security import require_admin,require_origin,verify_password,create_session,digest,limiter
from .config import settings
from .domain import can_transition,safe_url,is_fresh
from .ingestion import fetch_source,register_version,extract_content
from .ai import index_version

router=APIRouter(prefix='/api/admin',tags=['admin'])
def audit(db,admin,action,target,note=''):
    db.add(Audit(admin_id=admin.id,action=action,target=target,note=note))
def find(db,model,id):
    obj=db.get(model,id)
    if not obj:raise HTTPException(404,'Record not found')
    return obj

def service_json(s):return {k:getattr(s,k) for k in ['id','slug','name_en','name_bn','category','description_en','description_bn','official_url','status']}
def version_json(v):return {'id':v.id,'source_id':v.source_id,'status':v.status,'content':v.content,'claims':v.claims,'retrieved_at':v.retrieved_at,'verified_at':v.verified_at,'review_due':v.review_due}

@router.post('/login')
def login(data:LoginInput,request:Request,response:Response,db:DBSession=Depends(get_db)):
    require_origin(request);limiter.check('login:'+request.client.host,10,300)
    admin=db.scalar(select(Admin).where(Admin.username==data.username))
    if not admin or not verify_password(admin.password_hash,data.password):raise HTTPException(401,'Invalid username or password')
    token=create_session(db,admin)
    response.set_cookie('janun_session',token,httponly=True,secure=settings.environment=='production',samesite='strict',max_age=settings.session_hours*3600,path='/api/admin')
    return {'username':admin.username}

@router.post('/logout')
def logout(request:Request,response:Response,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    obj=db.get(Session,digest(request.cookies.get('janun_session','')))
    if obj:db.delete(obj);db.commit()
    response.delete_cookie('janun_session',path='/api/admin');return {'ok':True}

@router.get('/overview')
def overview(admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    return {'username':admin.username,'services':db.scalar(select(func.count()).select_from(Service)),'sources':db.scalar(select(func.count()).select_from(Source)),'pending':db.scalar(select(func.count()).select_from(SourceVersion).where(SourceVersion.status.in_(['pending','review']))),'ai_configured':settings.ai_configured,'embedding_configured':bool(settings.openai_api_key and settings.embedding_model)}

@router.get('/services')
def services(admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    return [service_json(s) for s in db.scalars(select(Service).order_by(Service.name_en))]

@router.post('/services',status_code=201)
def create_service(data:ServiceInput,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    if not db.get(Category,data.category):raise HTTPException(422,'Choose a valid category')
    if data.official_url and not safe_url(data.official_url,settings.hosts):raise HTTPException(422,'Use an allowlisted official HTTPS URL')
    if db.scalar(select(Service).where(Service.slug==data.slug)):raise HTTPException(409,'Service slug already exists')
    obj=Service(**data.model_dump());db.add(obj);db.flush();audit(db,admin,'service.create',obj.id);db.commit();return service_json(obj)

@router.put('/services/{id}')
def edit_service(id:str,data:ServiceInput,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    obj=find(db,Service,id)
    if not db.get(Category,data.category):raise HTTPException(422,'Invalid category')
    if data.official_url and not safe_url(data.official_url,settings.hosts):raise HTTPException(422,'Invalid official URL')
    if db.scalar(select(Service).where(Service.slug==data.slug,Service.id!=id)):raise HTTPException(409,'Slug already exists')
    for k,v in data.model_dump().items():setattr(obj,k,v)
    obj.status='draft';audit(db,admin,'service.edit',id,'Publication reset after edit');db.commit();return service_json(obj)

@router.post('/services/{id}/publish')
def publish_service(id:str,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    obj=find(db,Service,id)
    approved=db.scalar(select(SourceVersion).join(Source,SourceVersion.source_id==Source.id).where(Source.service_id==id,Source.current_version==SourceVersion.id,SourceVersion.status=='published',SourceVersion.review_due>now()))
    if not approved:raise HTTPException(409,'Publish a current reviewed source first')
    obj.status='published';audit(db,admin,'service.publish',id);db.commit();return service_json(obj)

@router.post('/services/{id}/archive')
def archive_service(id:str,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    obj=find(db,Service,id);obj.status='archived';audit(db,admin,'service.archive',id);db.commit();return service_json(obj)

@router.get('/sources')
def sources(admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    result=[]
    for src in db.scalars(select(Source)):
        versions=list(db.scalars(select(SourceVersion).where(SourceVersion.source_id==src.id).order_by(SourceVersion.retrieved_at.desc()).limit(10)))
        result.append({'id':src.id,'service_id':src.service_id,'url':src.url,'title':src.title,'agency':src.agency,'current_version':src.current_version,'versions':[version_json(v) for v in versions]})
    return result

@router.post('/sources',status_code=201)
def create_source(data:SourceInput,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    find(db,Service,data.service_id)
    if not safe_url(data.url,settings.hosts):raise HTTPException(422,'Use an allowlisted official HTTPS source')
    obj=Source(**data.model_dump());db.add(obj);db.flush();audit(db,admin,'source.create',obj.id);db.commit();return {'id':obj.id}

@router.post('/sources/{id}/fetch')
def fetch(id:str,request:Request,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    limiter.check('ingest:'+admin.id,5,60);src=find(db,Source,id)
    try:version=register_version(db,src,fetch_source(src.url))
    except Exception:raise HTTPException(422,'Could not safely retrieve this source. Check the canonical URL, permissions and document format, or upload an authorized copy.')
    audit(db,admin,'source.fetch',src.id);db.commit();return version_json(version)

@router.post('/sources/{id}/upload')
def upload(id:str,file:UploadFile=File(...),admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    limiter.check('ingest:'+admin.id,5,60);src=find(db,Source,id)
    data=file.file.read(settings.max_source_bytes+1)
    try:version=register_version(db,src,extract_content(data,file.content_type or ''))
    except Exception:raise HTTPException(422,'Use a readable HTML, text or PDF document under 5 MB and 200 pages')
    audit(db,admin,'source.upload',src.id,'Reviewer must verify provenance against the registered official URL');db.commit();return version_json(version)

@router.post('/versions/{id}/review')
def review(id:str,data:ReviewInput,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    v=find(db,SourceVersion,id);src=find(db,Source,v.source_id)
    if src.current_version!=v.id:raise HTTPException(409,'Review the current source version')
    if not can_transition(v.status,data.status):raise HTTPException(409,'Invalid review transition')
    if data.claims is not None and data.status!='verified':raise HTTPException(422,'Edit structured claims when verifying the source')
    if data.status=='verified':
        v.verified_at=now();v.review_due=now()+timedelta(days=data.review_days)
        if data.claims is not None:v.claims=data.claims.model_dump()
    if data.status=='published' and not is_fresh(v.review_due):raise HTTPException(409,'Re-review expired information')
    v.status=data.status;audit(db,admin,'source.'+data.status,id,data.note);db.commit();return version_json(v)

@router.post('/versions/{id}/index')
def index(id:str,admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    try:count=index_version(db,id)
    except ValueError as exc:raise HTTPException(422,str(exc))
    except Exception:raise HTTPException(503,'Embedding provider unavailable; no changes were committed')
    audit(db,admin,'source.index',id);db.commit();return {'chunks':count}

@router.get('/feedback')
def feedback(admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    return [{'id':f.id,'message':f.message,'service_slug':f.service_slug,'created_at':f.created_at} for f in db.scalars(select(Feedback).order_by(Feedback.created_at.desc()).limit(100))]

@router.get('/audit')
def audits(admin=Depends(require_admin),db:DBSession=Depends(get_db)):
    return [{'action':a.action,'target':a.target,'note':a.note,'created_at':a.created_at} for a in db.scalars(select(Audit).order_by(Audit.created_at.desc()).limit(100))]

# Uploaded team data remain authenticated research; no source is auto-published.
from fastapi import Query
from .team_data import catalogue as team_catalogue, search as search_team_data

@router.get('/team-data')
def team_data(q:str=Query('',max_length=200),owner:str=Query('',max_length=30),table:str=Query('',max_length=100),kind:str=Query('',max_length=30),page:int=Query(1,ge=1),page_size:int=Query(25,ge=1,le=100),admin=Depends(require_admin)):
    return search_team_data(q,owner,table,kind,page,page_size)

@router.get('/team-data/record')
def team_record(record_id:str=Query(...,max_length=300),admin=Depends(require_admin)):
    row=next((r for r in team_catalogue()['records'] if r['id']==record_id),None)
    if row is None:raise HTTPException(404,'Team record not found')
    return row
