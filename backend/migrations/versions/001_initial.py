"""Initial frozen PostgreSQL schema."""
from pathlib import Path
from alembic import op
from app.config import settings
revision='001_initial'
down_revision=None
branch_labels=None
depends_on=None

def upgrade():
    if not 1<=settings.embedding_dimensions<=16000:raise ValueError('Invalid embedding dimension')
    sql=(Path(__file__).parents[1]/'001_initial.sql').read_text()
    sql=sql.replace('VECTOR(1536)',f'VECTOR({settings.embedding_dimensions})')
    for statement in sql.split(';'):
        if statement.strip():op.execute(statement)

def downgrade():
    # Explicitly destructive: back up first and never run during ordinary deployment.
    for table in ['admin_sessions','audit_logs','knowledge_chunks','source_versions','sources','services','service_categories','feedback','admin_users']:
        op.execute(f'DROP TABLE IF EXISTS {table}')
