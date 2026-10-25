"""Bounded extraction. Nothing is automatically approved or published."""
import hashlib, ipaddress, socket, re, time
from urllib.parse import urlsplit
import httpx
from bs4 import BeautifulSoup
import fitz
from sqlalchemy import select
from .config import settings
from .domain import safe_url
from .models import SourceVersion, Chunk

def validate_public_url(url):
    if not safe_url(url,settings.hosts): raise ValueError('Use an allowed official HTTPS source without redirects or credentials')
    host=urlsplit(url).hostname
    addresses=socket.getaddrinfo(host,443,type=socket.SOCK_STREAM)
    if not addresses or any(not ipaddress.ip_address(a[4][0]).is_global for a in addresses):
        raise ValueError('Private or reserved source addresses are not allowed')
    return addresses[0][4][0]

def extract_content(data:bytes,content_type:str) -> str:
    if len(data)>settings.max_source_bytes:raise ValueError('Source exceeds size limit')
    if 'pdf' in content_type:
        with fitz.open(stream=data,filetype='pdf') as doc:
            if doc.page_count>200:raise ValueError('PDF exceeds 200 page limit')
            text='\n\n'.join(page.get_text() for page in doc)
    elif 'html' in content_type:
        soup=BeautifulSoup(data,'html.parser')
        for node in soup(['script','style','nav','footer','header','noscript']):node.decompose()
        text=soup.get_text('\n',strip=True)
    elif 'text/plain' in content_type:text=data.decode('utf-8',errors='replace')
    else:raise ValueError('Only HTML, text and text-based PDF sources are supported')
    text=re.sub(r'\n{3,}','\n\n',text).strip()
    if len(text)<40:raise ValueError('Too little readable text. Scanned PDFs need OCR before import.')
    if len(text)>500_000:raise ValueError('Extracted source exceeds text limit')
    return text

def fetch_source(url:str) -> str:
    ip=validate_public_url(url)
    from urllib.robotparser import RobotFileParser
    parts=urlsplit(url);host=parts.hostname
    authority=f'[{ip}]' if ':' in ip else ip
    deadline=time.monotonic()+35
    def bounded_get(client,path,limit):
        # Pin the validated public address to prevent DNS rebinding. Preserve TLS SNI and Host.
        target=f'https://{authority}{path}'
        with client.stream('GET',target,headers={'Host':host},extensions={'sni_hostname':host}) as response:
            data=bytearray()
            for block in response.iter_bytes():
                if time.monotonic()>deadline:raise ValueError('Source deadline exceeded')
                data.extend(block)
                if len(data)>limit:raise ValueError('Source exceeds size limit')
            return response.status_code,bytes(data),response.headers.get('content-type','')
    with httpx.Client(timeout=10,follow_redirects=False,trust_env=False,headers={'User-Agent':'JanunSourceReview/0.1'}) as client:
        status,robots,_=bounded_get(client,'/robots.txt',128_000)
        if status==200:
            parser=RobotFileParser();parser.parse(robots.decode('utf-8',errors='replace').splitlines())
            if not parser.can_fetch('JanunSourceReview',url):raise ValueError('robots.txt disallows this source')
        elif status not in (404,410):raise ValueError('Could not establish source crawling policy; use an authorized document upload')
        path=parts.path or '/'
        if parts.query:path+='?'+parts.query
        status,data,kind=bounded_get(client,path,settings.max_source_bytes)
        if status!=200:raise ValueError('Source unavailable or redirects; register its canonical URL')
        return extract_content(data,kind)

def chunk_text(text,limit=1400,overlap=180):
    return [text[i:i+limit] for i in range(0,len(text),limit-overlap) if text[i:i+limit].strip()]

def register_version(db,source,content):
    content_hash=hashlib.sha256(content.encode()).hexdigest()
    old=db.get(SourceVersion,source.current_version) if source.current_version else None
    if old and old.content_hash==content_hash:return old
    if old and old.status=='published':old.status='stale'
    version=SourceVersion(source_id=source.id,content=content,content_hash=content_hash)
    db.add(version);db.flush();source.current_version=version.id
    for i,text in enumerate(chunk_text(content)):db.add(Chunk(version_id=version.id,text=text,ordinal=i))
    db.flush();return version
