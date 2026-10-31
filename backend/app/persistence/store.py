"""SQLite transactions persist job state and canonical graph payloads."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path
import sqlite3
import uuid

def now():
    return datetime.now(timezone.utc).isoformat()

class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        with self.connect() as db:
            db.executescript('''
            CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, payload TEXT NOT NULL);
            CREATE TABLE IF NOT EXISTS analyses(id TEXT PRIMARY KEY, summary TEXT NOT NULL, graph TEXT NOT NULL);
            ''')

    def connect(self):
        return sqlite3.connect(self.path, timeout=15)

    def create_job(self):
        job = dict(id=uuid.uuid4().hex, status='queued', phase='queued', progress=0,
                   created_at=now(), snapshot_id=None, error=None)
        with self.connect() as db:
            db.execute('INSERT INTO jobs VALUES (?,?)', (job['id'], json.dumps(job)))
        return job

    def job(self, identifier):
        with self.connect() as db:
            row = db.execute('SELECT payload FROM jobs WHERE id=?', (identifier,)).fetchone()
        return json.loads(row[0]) if row else None

    def update(self, identifier, **values):
        # One writer per job, except startup recovery before the executor starts.
        job = self.job(identifier)
        job.update(values)
        with self.connect() as db:
            db.execute('UPDATE jobs SET payload=? WHERE id=?', (json.dumps(job), identifier))
        return job

    def recover(self):
        with self.connect() as db:
            rows = db.execute('SELECT id,payload FROM jobs').fetchall()
        for identifier, payload in rows:
            if json.loads(payload)['status'] in ('queued', 'running'):
                self.update(identifier, status='failed', phase='interrupted', error='Server restarted during analysis')

    def save(self, graph, provenance):
        summary = dict(snapshot_id=graph['snapshot_id'], repository=graph['repository'], created_at=now(),
                       provenance=provenance, coverage=graph['coverage'], scope=graph['scope'],
                       counts={key: len(graph[key]) for key in ('entities', 'edges', 'evidence')},
                       unknown_counts=dict(Counter(x['kind'] for x in graph['unknowns'])),
                       inventory={'packages': graph.get('packages', []), 'languages': graph.get('languages', {})},
                       diagnostics=graph.get('diagnostics', []),
                       tools={'typescript': graph['typescript_version'], 'pyyaml': graph.get('configuration_parser'),
                              'syft': 'deferred; package manifests inventoried, not a complete SBOM'})
        with self.connect() as db:
            db.execute('INSERT OR IGNORE INTO analyses VALUES (?,?,?)',
                       (graph['snapshot_id'], json.dumps(summary), json.dumps(graph)))
        return summary

    def history(self):
        with self.connect() as db:
            rows = db.execute('SELECT summary FROM analyses ORDER BY rowid DESC LIMIT 50').fetchall()
        return [json.loads(x[0]) for x in rows]

    def analysis(self, identifier, graph=False):
        with self.connect() as db:
            row = db.execute('SELECT summary,graph FROM analyses WHERE id=?', (identifier,)).fetchone()
        return json.loads(row[1 if graph else 0]) if row else None
