from datetime import timedelta
from sqlalchemy import event
from app.admin import sources
from app.models import Source, SourceVersion, now
from test_api import env


def test_source_history_keeps_ten_latest_versions_without_per_source_queries(env):
    _, db, service, _ = env
    timestamp = now()
    for index in range(24):
        source = Source(service_id=service.id, url='https://bdris.gov.bd/', title=f'Source {index}')
        db.add(source)
        db.flush()
        if index == 0:
            history_id = source.id
            for version in range(12):
                db.add(SourceVersion(source_id=source.id, content=f'Content {version}',
                    content_hash=f'hash-{version}', claims={'steps': [f'Step {version}']},
                    retrieved_at=timestamp + timedelta(seconds=version)))
    db.commit()
    statements = []
    def record(connection, cursor, statement, parameters, context, executemany):
        statements.append(statement)
    engine = db.get_bind()
    event.listen(engine, 'before_cursor_execute', record)
    try:
        rows = sources(admin=object(), db=db)
    finally:
        event.remove(engine, 'before_cursor_execute', record)
    assert len(rows) == 25
    history = next(row['versions'] for row in rows if row['id'] == history_id)
    assert [version['content'] for version in history] == [
        'Content 11', 'Content 10', 'Content 9', 'Content 8', 'Content 7',
        'Content 6', 'Content 5', 'Content 4', 'Content 3', 'Content 2']
    assert history[0]['claims'] == {'steps': ['Step 11']}
    assert any(row['versions'] == [] for row in rows)
    assert len(statements) <= 2, f'Source listing made {len(statements)} database queries'


def test_empty_source_listing(env):
    _, db, _, _ = env
    db.query(SourceVersion).delete()
    db.query(Source).delete()
    db.commit()
    assert sources(admin=object(), db=db) == []
