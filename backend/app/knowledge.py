from sqlalchemy import select, func
from .models import Service, Source, SourceVersion, Chunk, now
from .domain import normalize_query
from .config import settings
import json


def record_metadata(version):
    """Keep original import controls with every chunk, not only its first page."""
    content=version.content
    start=content.find('{')
    if start<0:return {'record_context':content[:1200]}
    try:payload,_=json.JSONDecoder().raw_decode(content[start:])
    except (ValueError,TypeError):return {'record_context':content[:1200]}
    if not isinstance(payload,dict):return {'record_context':content[:1200]}
    keys=[key for key in payload if any(term in key.lower() for term in (
        'status','conflict','unverified','verified_fields','publication_rule',
        'cycle','session','scope','coverage','geo_','location','date','checked_on','notes','limitation'))]
    def priority(key):
        return (0 if any(term in key for term in ('publication_rule','conflict','unverified')) else
            1 if 'status' in key else 2 if any(term in key for term in ('cycle','scope','geo_','coverage')) else 3)
    result={};size=0
    for key in sorted(keys,key=priority):
        value=payload[key]
        encoded=json.dumps(value,ensure_ascii=False)
        if len(encoded)>1000:value=encoded[:1000]+' [truncated]'
        size+=len(key)+len(json.dumps(value,ensure_ascii=False))
        if size>6000:
            result['_metadata_truncated']=True
            break
        result[key]=value
    return result or {'record_context':content[:1200]}

def evidence_query():
    return select(Chunk,SourceVersion,Source,Service).join(SourceVersion,Chunk.version_id==SourceVersion.id).join(Source,SourceVersion.source_id==Source.id).join(Service,Source.service_id==Service.id).where(SourceVersion.id==Source.current_version,SourceVersion.status=='published',SourceVersion.review_due>now(),Service.status=='published')

def source_record(chunk,version,source,service):
    supplied=version.verified_at is None
    return {'id':chunk.id,'title':source.title,'url':source.url,'agency':source.agency,
        'last_checked':version.retrieved_at.isoformat(),
        'verified_at':version.verified_at.isoformat() if version.verified_at else None,
        'review_due':version.review_due.isoformat() if version.review_due else None,
        'verification_status':'supplied_research' if supplied else 'published',
        'review_status':'supplied_research' if supplied else 'reviewed',
        'service_slug':service.slug,'excerpt':chunk.text[:500]}


def retrieve(db,query,embedding=None):
    return rank_evidence(db,evidence_query(),query,embedding)


def retrieve_team_research(db,query):
    # Chat-only: imports already supplied for the public catalogue, never
    # arbitrary admin drafts, withdrawn services or previously reviewed records.
    base=select(Chunk,SourceVersion,Source,Service).join(
        SourceVersion,Chunk.version_id==SourceVersion.id).join(
        Source,SourceVersion.source_id==Source.id).join(Service,Source.service_id==Service.id).where(
        SourceVersion.id==Source.current_version,
        SourceVersion.status.in_(['pending','review']),
        SourceVersion.verified_at.is_(None),SourceVersion.review_due.is_(None),
        Service.status.in_(['draft','published']),
        Source.title.startswith('Team research: '),
        Source.agency.startswith('Uploaded team research'),Source.url.startswith('https://'))
    return rank_evidence(db,base,query)


def rank_evidence(db,base,query,embedding=None):
    normalized=normalize_query(query)
    ranked=[]
    if db.bind.dialect.name=='postgresql':
        terms=' OR '.join(t for t in normalized.split() if t)
        tsq=func.websearch_to_tsquery('simple',terms)
        # Service names make English/Bangla queries find the same imported record.
        text=Chunk.text+' '+Service.name_en+' '+Service.name_bn+' '+Source.title
        vec=func.to_tsvector('simple',text)
        ranked.append(list(db.execute(base.where(vec.op('@@')(tsq)).order_by(func.ts_rank_cd(vec,tsq).desc()).limit(30))))
        if embedding is not None:
            ranked.append(list(db.execute(base.where(Chunk.embedding.is_not(None),Chunk.embedding_model==settings.embedding_model).order_by(Chunk.embedding.cosine_distance(embedding)).limit(30))))
    else:
        # SQLite is only used in tests. Production always runs PostgreSQL FTS.
        terms=set(normalized.split())
        matches=[]
        for row in db.execute(base):
            score=sum(t in (row[0].text+' '+row[3].name_en+' '+row[3].name_bn+' '+row[2].title).lower() for t in terms)
            if score:matches.append((score,row))
        ranked.append([r for _,r in sorted(matches,key=lambda x:x[0],reverse=True)])
    scores={};rows={}
    for result in ranked:
        for i,row in enumerate(result):
            key=row[0].id;scores[key]=scores.get(key,0)+1/(60+i+1);rows[key]=row
    return [rows[k] for k in sorted(scores,key=scores.get,reverse=True)[:settings.retrieval_limit]]

def service_detail(db,service):
    versions=list(db.execute(select(SourceVersion,Source).join(Source,SourceVersion.source_id==Source.id).where(Source.service_id==service.id,Source.current_version==SourceVersion.id,SourceVersion.status=='published',SourceVersion.review_due>now())))
    # A replacement release is authoritative for this service's entire field set.
    # Do not merge omitted fields back in from older research.
    if any(v.claims.get('document_update') for v,_ in versions):
        from .document_release import release
        row=next((r for r in release()['services'] if r['slug']==service.slug),None)
        if row:return {**row,'id':service.id}
    result={'id':service.id,'slug':service.slug,'name_en':service.name_en,'name_bn':service.name_bn,'category':service.category,'description_en':service.description_en,'description_bn':service.description_bn,'official_url':service.official_url,'steps':[],'documents':[],'eligibility':[],'fees':None,'processing_time':None,'deadline':None,'sources':[],'conflicts':[],'readiness_questions':[]}
    for version,source in versions:
        questions=version.claims.get('readiness_questions',[])
        if questions:
            if result['readiness_questions'] and result['readiness_questions']!=questions:
                result['conflicts'].append('readiness_questions')
            else:result['readiness_questions']=questions
        for field in ('steps','documents','eligibility'):
            result[field]=list(dict.fromkeys(result[field]+version.claims.get(field,[])))
        for field in ('fees','processing_time','deadline'):
            value=version.claims.get(field)
            if value is not None:
                if result[field] is not None and result[field]!=value:result['conflicts'].append(field)
                result[field]=value
        result['sources'].append({'id':version.id,'title':source.title,'url':source.url,'agency':source.agency,'verified_at':version.verified_at.isoformat() if version.verified_at else None,'last_checked':version.retrieved_at.isoformat(),'review_due':version.review_due.isoformat()})
    for field in result['conflicts']:result[field]=[] if field=='readiness_questions' else None
    return result
