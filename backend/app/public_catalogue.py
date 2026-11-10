"""Read-only visibility of source-linked imports. This never publishes evidence."""
import hashlib
import json
from sqlalchemy import select, or_
from .models import Service, Source, SourceVersion
from .knowledge import team_research_conditions, service_detail


def public_services():
    imported = select(Source.id).join(SourceVersion, SourceVersion.source_id == Source.id).where(
        Source.service_id == Service.id, *team_research_conditions()).correlate(Service).exists()
    return select(Service).where(or_(Service.status == 'published', imported))


def supplied_versions(db, service_ids):
    return db.execute(select(SourceVersion, Source).join(Source, SourceVersion.source_id == Source.id)
        .join(Service, Source.service_id == Service.id).where(
            Source.service_id.in_(service_ids), *team_research_conditions())
        .order_by(SourceVersion.retrieved_at.desc(), SourceVersion.id)).all()


def imported_payload(version, source):
    start = version.content.find('{')
    if start >= 0:
        try:
            value, _ = json.JSONDecoder().raw_decode(version.content[start:])
            if isinstance(value, dict): return value
        except ValueError:
            pass
    # Original Sachin imports used readable summaries instead of embedded JSON.
    # Only restore their supplied structured fields if the CURRENT text matches
    # the original exactly. Never resurrect fields after an administrator edits it.
    from .team_data import catalogue, prepare
    for record in catalogue()['records']:
        if record['owner'] != 'Sachin' or record['kind'] != 'service': continue
        if source.title != 'Team research: Sachin / ' + record['original_id']: continue
        original = prepare(record)
        if original and hashlib.sha256(original[2].encode()).digest() == hashlib.sha256(version.content.encode()).digest():
            return record['payload']
    return {'notes': version.content}


def field(payload, *keys):
    return next((payload[key] for key in keys if payload.get(key)), None)


def lines(value):
    if not value: return []
    if isinstance(value, list): return [str(item) for item in value if item]
    return [line.strip() for line in str(value).splitlines() if line.strip()]


def public_detail(db, service):
    result = service_detail(db, service)
    # Current published evidence is authoritative over the imported projection.
    if result['sources']: return result
    versions = supplied_versions(db, [service.id])
    if not versions: return result
    result.update(status='supplied_research', review_status='supplied_research', raw_fields={})
    for version, source in versions:
        payload = imported_payload(version, source)
        claims = payload.get('claims') if isinstance(payload.get('claims'), dict) else {}
        for target, keys in {
            'documents': ('required_documents', 'documents'),
            'eligibility': ('eligibility', 'eligible_who'),
            'steps': ('steps', 'application_procedure', 'application_method'),
        }.items():
            result[target] = list(dict.fromkeys(result[target] + lines(claims.get(target) or field(payload, *keys))))
        for target, keys in {
            'fees': ('fee_information', 'govt_fee', 'fee'),
            'processing_time': ('processing_time',), 'deadline': ('duration_deadline', 'apply_end'),
        }.items():
            value = claims.get(target) or field(payload, *keys)
            if value:
                value = str(value)
                if result[target] and result[target] != value:
                    result['conflicts'].append(target)
                else: result[target] = value
        scope = field(payload, 'scope', 'geographic_availability', 'geographic_scope', 'coverage_area')
        if isinstance(scope, dict): scope = field(scope, 'label_bn', 'label_en')
        if scope: result['scope'] = str(scope)
        result['conflicts'] += lines(field(payload, 'notes_bn', 'gaps_or_conflicts', 'missing_information_notes', 'conflicts_noted', 'notes'))
        result['raw_fields'][source.title] = payload
        result['sources'].append({
            'id': version.id, 'title': source.title, 'url': source.url, 'agency': source.agency,
            'verified_at': None, 'review_due': None, 'last_checked': version.retrieved_at.isoformat(),
            'review_status': 'supplied_research',
        })
    if len(result['raw_fields']) == 1: result['raw_fields'] = next(iter(result['raw_fields'].values()))
    for target in ('fees', 'processing_time', 'deadline'):
        if target in result['conflicts']: result[target] = None
    return result
