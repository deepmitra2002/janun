from sqlalchemy import select, func
from .models import Service, Source, SourceVersion, Chunk, now
from .domain import normalize_query
from .config import settings

def evidence_query():
    return select(Chunk,SourceVersion,Source,Service).join(SourceVersion,Chunk.version_id==SourceVersion.id).join(Source,SourceVersion.source_id==Source.id).join(Service,Source.service_id==Service.id).where(SourceVersion.id==Source.current_version,SourceVersion.status=='published',SourceVersion.review_due>now(),Service.status=='published')

def source_record(chunk,version,source,service):
    return {'id':chunk.id,'title':source.title,'url':source.url,'agency':source.agency,'last_checked':version.retrieved_at.isoformat(),'verified_at':version.verified_at.isoformat() if version.verified_at else None,'review_due':version.review_due.isoformat() if version.review_due else None,'verification_status':'published','service_slug':service.slug,'excerpt':chunk.text[:500]}

def retrieve(db,query,embedding=None):
    normalized=normalize_query(query)
    base=evidence_query()
    ranked=[]
    if db.bind.dialect.name=='postgresql':
        terms=' | '.join(t for t in normalized.split() if t)
        tsq=func.websearch_to_tsquery('simple',terms.replace(' | ',' OR '))
        vec=func.to_tsvector('simple',Chunk.text)
        ranked.append(list(db.execute(base.where(vec.op('@@')(tsq)).order_by(func.ts_rank_cd(vec,tsq).desc()).limit(30))))
        if embedding is not None:
            ranked.append(list(db.execute(base.where(Chunk.embedding.is_not(None),Chunk.embedding_model==settings.embedding_model).order_by(Chunk.embedding.cosine_distance(embedding)).limit(30))))
    else:
        # SQLite is only used in tests. Production always runs PostgreSQL FTS.
        terms=set(normalized.split())
        matches=[]
        for row in db.execute(base):
            score=sum(t in (row[0].text+' '+row[3].name_en+' '+row[3].name_bn).lower() for t in terms)
            if score:matches.append((score,row))
        ranked.append([r for _,r in sorted(matches,key=lambda x:x[0],reverse=True)])
    scores={};rows={}
    for result in ranked:
        for i,row in enumerate(result):
            key=row[0].id;scores[key]=scores.get(key,0)+1/(60+i+1);rows[key]=row
    return [rows[k] for k in sorted(scores,key=scores.get,reverse=True)[:settings.retrieval_limit]]

def service_detail(db,service):
    versions=list(db.execute(select(SourceVersion,Source).join(Source,SourceVersion.source_id==Source.id).where(Source.service_id==service.id,Source.current_version==SourceVersion.id,SourceVersion.status=='published',SourceVersion.review_due>now())))
    result={'id':service.id,'slug':service.slug,'name_en':service.name_en,'name_bn':service.name_bn,'category':service.category,'description_en':service.description_en,'description_bn':service.description_bn,'official_url':service.official_url,'steps':[],'documents':[],'eligibility':[],'fees':None,'processing_time':None,'deadline':None,'sources':[],'conflicts':[]}
    for version,source in versions:
        for field in ('steps','documents','eligibility'):
            result[field]=list(dict.fromkeys(result[field]+version.claims.get(field,[])))
        for field in ('fees','processing_time','deadline'):
            value=version.claims.get(field)
            if value is not None:
                if result[field] is not None and result[field]!=value:result['conflicts'].append(field)
                result[field]=value
        result['sources'].append({'id':version.id,'title':source.title,'url':source.url,'agency':source.agency,'verified_at':version.verified_at.isoformat() if version.verified_at else None,'last_checked':version.retrieved_at.isoformat(),'review_due':version.review_due.isoformat()})
    for field in result['conflicts']:result[field]=None
    return result
