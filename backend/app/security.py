import hashlib
import secrets
from datetime import timedelta
from collections import defaultdict, deque
from threading import Lock
from time import monotonic
from argon2 import PasswordHasher
from argon2.exceptions import VerificationError
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session as DBSession
from .database import get_db
from .models import Admin, Session, now
from .config import settings
from .domain import is_fresh

hasher=PasswordHasher()
def password_hash(value): return hasher.hash(value)
def verify_password(encoded,value):
    try: return hasher.verify(encoded,value)
    except VerificationError: return False

def digest(token): return hashlib.sha256(token.encode()).hexdigest()
def create_session(db,admin):
    token=secrets.token_urlsafe(48)
    db.add(Session(token_hash=digest(token),admin_id=admin.id,expires_at=now()+timedelta(hours=settings.session_hours)))
    db.commit();return token

def require_origin(request:Request):
    if request.headers.get('origin') not in settings.origins or request.headers.get('x-janun-request')!='1':
        raise HTTPException(403,'Request origin could not be verified')

def require_admin(request:Request,db:DBSession=Depends(get_db)):
    token=request.cookies.get('janun_session','')
    session=db.get(Session,digest(token)) if token else None
    if not session or not is_fresh(session.expires_at): raise HTTPException(401,'Please sign in')
    admin=db.get(Admin,session.admin_id)
    if not admin: raise HTTPException(401,'Please sign in')
    if request.method not in ('GET','HEAD','OPTIONS'): require_origin(request)
    return admin

class RateLimiter:
    """Bounded single-process limiter; deploy one worker or replace with Redis."""
    def __init__(self): self.buckets=defaultdict(deque);self.lock=Lock()
    def check(self,key,limit=30,window=60):
        t=monotonic()
        with self.lock:
            if len(self.buckets)>10000:
                self.buckets={k:v for k,v in self.buckets.items() if v and v[-1]>t-window}
                self.buckets=defaultdict(deque,self.buckets)
            q=self.buckets[key]
            while q and q[0]<=t-window:q.popleft()
            if len(q)>=limit:raise HTTPException(429,'Too many requests. Please try again shortly.',headers={'Retry-After':str(window)})
            q.append(t)
limiter=RateLimiter()
