"""Check frontend rendering, the Vercel API proxy, and database readiness."""
import json
import os
import time
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def check(url, kind):
    parsed = urlsplit(url)
    if parsed.scheme != 'https' and not (
        parsed.scheme == 'http' and parsed.hostname in {'localhost', '127.0.0.1'}
    ):
        raise ValueError('Monitoring URLs must use HTTPS (except local validation).')
    for attempt in range(3):
        try:
            request = Request(url, headers={'User-Agent': 'Janun-Uptime/1.0'})
            with urlopen(request, timeout=90) as response:
                if response.status != 200:
                    raise ValueError('Expected HTTP 200')
                body = response.read(8_000_001)
                if len(body) > 8_000_000:
                    raise ValueError('Monitoring response exceeds size limit')
                if kind == 'ready' and json.loads(body).get('status') != 'ready':
                    raise ValueError('Database readiness check failed')
                if kind == 'categories' and not json.loads(body):
                    raise ValueError('No categories returned through frontend proxy')
                if kind == 'page' and 'জানুন' not in body.decode('utf-8'):
                    raise ValueError('Expected Janun homepage content')
                if kind == 'demo':
                    data = json.loads(body)
                    if not data.get('services') or not data.get('categories'):
                        raise ValueError('Demo catalogue is empty')
            print(f'{kind}: healthy')
            return
        except Exception:
            if attempt == 2:
                # Avoid echoing URLs, credentials, or HTTP response bodies in logs.
                raise SystemExit(f'{kind}: failed after three attempts') from None
            time.sleep(10)


def main():
    site = os.environ.get('JANUN_SITE_URL', '').rstrip('/')
    api = os.environ.get('JANUN_API_URL', '').rstrip('/')
    if not site:
        raise SystemExit('Set JANUN_SITE_URL before monitoring.')
    if api:
        check(api + '/ready', 'ready')
    check(site + '/', 'page')
    if api:
        check(site + '/api/categories', 'categories')
    else:
        check(site + '/demo-data.json', 'demo')


if __name__ == '__main__':
    main()
