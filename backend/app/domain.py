"""Pure policy functions shared by API, ingestion and evaluation."""
from datetime import datetime, timezone
from urllib.parse import urlsplit
import re

TRANSITIONS = {'pending': {'review','rejected'}, 'review': {'verified','rejected'}, 'verified': {'published','review','rejected'}, 'published': {'stale','archived'}, 'stale': {'review','archived'}, 'rejected': {'review','archived'}, 'archived': set()}
ALIASES = {'পাসপোর্ট':'passport', 'passport':'passport পাসপোর্ট', 'জন্ম':'birth', 'নিবন্ধন':'registration', 'jonmo':'birth', 'nibondhon':'registration', 'jonmonibondhon':'birth registration', 'nid':'identity এনআইডি', 'এনআইডি':'identity nid', 'police':'police পুলিশ', 'পুলিশ':'police', 'মৃত্যু':'death', 'licence':'license', 'license':'licence', 'লাইসেন্স':'licence', 'tin':'tax কর', 'কর':'tax', 'ব্যবসা':'business trade', 'bidesh':'abroad passport', 'বিদেশ':'abroad passport'}

def can_transition(current: str, target: str) -> bool:
    return target in TRANSITIONS.get(current, set())

def is_fresh(review_due: datetime | None) -> bool:
    if review_due is None: return False
    if review_due.tzinfo is None: review_due = review_due.replace(tzinfo=timezone.utc)
    return review_due > datetime.now(timezone.utc)

def normalize_query(query: str) -> str:
    query = re.sub(r'\s+', ' ', query.strip().lower())
    extra = [v for k,v in ALIASES.items() if k in query]
    return ' '.join([query, *extra])

def validate_citations(ids: list[str], allowed: set[str]) -> list[str]:
    return list(dict.fromkeys(x for x in ids if x in allowed))

def order_steps(steps: list[dict]) -> list[dict]:
    remaining = {s['id']: s for s in steps}
    if len(remaining) != len(steps): raise ValueError('Duplicate step identifiers')
    ordered = []; done = set()
    while remaining:
        ready = [s for s in remaining.values() if set(s.get('depends_on', [])) <= done]
        if not ready: raise ValueError('Cyclic or missing dependency')
        for step in ready:
            ordered.append(step); done.add(step['id']); del remaining[step['id']]
    return ordered

def safe_url(url: str, allowed_hosts: set[str]) -> bool:
    try:
        p=urlsplit(url)
        return p.scheme=='https' and p.hostname in allowed_hosts and p.port in (None,443) and not p.username and not p.password and not p.fragment
    except ValueError: return False
