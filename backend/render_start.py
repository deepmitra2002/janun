"""Initialize and start the single-instance Render free web service."""
import os
from pathlib import Path
import subprocess
import sys


def main():
    os.chdir(Path(__file__).resolve().parent)
    url = os.environ.get('DATABASE_URL', '')
    if not url:
        raise SystemExit('Set DATABASE_URL to a PostgreSQL database with pgvector.')
    # Render/Neon supply a plain postgres URL; SQLAlchemy needs the psycopg driver.
    for prefix in ('postgres://', 'postgresql://'):
        if url.startswith(prefix):
            url = 'postgresql+psycopg://' + url[len(prefix):]
            break
    if not url.startswith('postgresql+psycopg://'):
        raise SystemExit('DATABASE_URL must be a PostgreSQL psycopg URL.')
    os.environ['DATABASE_URL'] = url
    port = int(os.environ.get('PORT', '8000'))
    if not 1 <= port <= 65535:
        raise SystemExit('PORT must be between 1 and 65535.')
    for arguments in [
        ['-m', 'alembic', 'upgrade', 'head'],
        ['-m', 'app.cli', 'seed'],
        ['-m', 'app.cli', 'import-team-data'],
    ]:
        subprocess.run([sys.executable, *arguments], check=True)
    os.execv(sys.executable, [
        sys.executable, '-m', 'uvicorn', 'app.main:app',
        '--host', '0.0.0.0', '--port', str(port),
        '--workers', '1', '--no-proxy-headers',
    ])


if __name__ == '__main__':
    main()
