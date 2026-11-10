"""Explicit, repeatable synchronization of the already supplied public catalogue.

Only untouched pending imports are replaced. Human edits and review decisions
win. The previous source version is retained, and no record is verified or
published by this command.
"""
import hashlib
import json
from copy import deepcopy
from functools import lru_cache
from pathlib import Path
from sqlalchemy import select
from .models import Category, Service, Source, SourceVersion, Chunk, uid
from .ingestion import chunk_text

FIELDS=('slug','name_en','name_bn','category','description_en','description_bn','official_url')
TITLE='Public catalogue: '
AGENCY='Owner-supplied public catalogue'


@lru_cache(maxsize=1)
def snapshot():
    return json.loads((Path(__file__).resolve().parents[1]/'data/public-catalogue.json').read_text())


def metadata(service):
    return {key:getattr(service,key) for key in FIELDS}


def original_imports():
    from .team_data import catalogue, prepare
    result={}
    for row in catalogue()['records']:
        if row['kind']!='service' or not row['import_enabled']:continue
        item=prepare(row)
        if item:
            spec,url,content=item
            result[spec['slug']]=(spec,'Team research: '+row['owner']+' / '+row['original_id'],content,url,'Uploaded team research — '+row['owner'])
    return result


def content_hash(content):
    return hashlib.sha256(content.encode()).hexdigest()


def source_url(row):
    return next((value for value in [row.get('official_url','')]+[s.get('url','') for s in row.get('sources',[])] if value.startswith('https://')),'')


def untouched(service,sources,versions,originals):
    if service.status!='draft' or len(sources)!=1:return False
    source=sources[0];version=versions.get(source.current_version)
    if not version or version.status!='pending' or version.verified_at or version.review_due:return False
    if version.content_hash!=content_hash(version.content):return False
    saved=version.claims.get('catalogue_metadata')
    if source.title==TITLE+service.slug and source.agency==AGENCY:
        try:record=json.loads(version.content.split('\n',1)[1])
        except (ValueError,IndexError):return False
        return saved==metadata(service) and source.url==source_url(record) and version.claims=={'catalogue_record':record,'catalogue_metadata':saved}
    original=originals.get(service.slug)
    return bool(original and source.title==original[1] and source.agency==original[4] and source.url==original[3]
        and metadata(service)=={key:original[0][key] for key in FIELDS}
        and version.content==original[2] and not version.claims)


def sync_public_catalogue(db):
    data=snapshot();report={'created':0,'updated':0,'unchanged':0,'superseded':0,'protected':[]}
    originals=original_imports()
    services={service.slug:service for service in db.scalars(select(Service))}
    by_service={}
    for source in db.scalars(select(Source)):by_service.setdefault(source.service_id,[]).append(source)
    # Source markers retain import identity when an administrator renames a slug.
    origin_titles={value[1]:slug for slug,value in originals.items()}
    origins={}
    for service in services.values():
        for source in by_service.get(service.id,[]):
            origin=source.title[len(TITLE):] if source.title.startswith(TITLE) else origin_titles.get(source.title)
            if origin:origins.setdefault(origin,set()).add(service.id)
    versions={version.id:version for version in db.scalars(select(SourceVersion).join(Source,Source.current_version==SourceVersion.id))}
    ready=set()
    try:
        # Flush category parents once; the remaining mutations are batched.
        from .cli import CATEGORIES
        baseline={slug:(en,bn,icon) for slug,en,bn,icon in CATEGORIES}
        categories={category.slug:category for category in db.scalars(select(Category))}
        for row in data['categories']:
            category=categories.get(row['slug'])
            if not category:
                category=Category(slug=row['slug']);db.add(category)
            elif tuple(getattr(category,k) for k in ('name_en','name_bn','icon')) not in (baseline.get(row['slug']),tuple(row[k] for k in ('name_en','name_bn','icon'))):
                continue
            for key in ('name_en','name_bn','icon'):setattr(category,key,row[key])
        db.flush()
        with db.no_autoflush:
            for incoming in data['services']:
                row=deepcopy(incoming);slug=row['slug'];service=services.get(slug)
                if origins.get(slug,set())-({service.id} if service else set()):
                    report['protected'].append(slug);continue
                created=service is None
                sources=by_service.get(service.id,[]) if service else []
                if service and not untouched(service,sources,versions,originals):
                    report['protected'].append(slug);continue
                if created:
                    service=Service(id=uid(),status='draft',**{key:row[key] for key in FIELDS})
                    services[slug]=service;db.add(service)
                else:
                    for key in FIELDS:setattr(service,key,row[key])
                ready.add(slug)
                # Use a dedicated managed source marker, including records for
                # which the supplied catalogue explicitly has no source URL.
                url=source_url(row)
                source=sources[0] if sources else Source(id=uid(),service_id=service.id)
                old=versions.get(source.current_version)
                content='OWNER-SUPPLIED PUBLIC CATALOGUE; INDEPENDENT REVIEW PENDING.\n'+json.dumps(row,ensure_ascii=False,sort_keys=True)
                digest=content_hash(content)
                if old and old.content_hash==digest:
                    report['unchanged']+=1;continue
                source.title=TITLE+slug;source.agency=AGENCY;source.url=url
                if not sources:db.add(source)
                if old:old.status='archived'
                version=SourceVersion(id=uid(),source_id=source.id,content=content,content_hash=digest,
                    status='pending',claims={'catalogue_record':row,'catalogue_metadata':metadata(service)},
                    verified_at=None,review_due=None)
                db.add(version);source.current_version=version.id
                for i,text in enumerate(chunk_text(content)):
                    db.add(Chunk(id=uid(),version_id=version.id,text=text,ordinal=i))
                report['created' if created else 'updated']+=1
            for alias,canonical in data.get('aliases',{}).items():
                service=services.get(alias)
                if not service or service.status=='superseded':continue
                if canonical in ready and untouched(service,by_service.get(service.id,[]),versions,originals):
                    service.status='superseded';report['superseded']+=1
                else:report['protected'].append(alias)
        db.commit()
    except Exception:
        db.rollback();raise
    return report
