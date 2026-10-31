"""Bounded local job queue; both input types enter the same pipeline."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import shutil
import tempfile
import threading
import httpx
from app.analysis.pipeline import analyze
from app.ingestion.archive import extract_archive
from app.ingestion.github import retrieve
from app.ingestion.snapshot import cleanup_error
from app.evidence.redaction import redact

class Jobs:
    def __init__(self, store, data: Path):
        self.store, self.data = store, data
        self.executor = ThreadPoolExecutor(max_workers=2, thread_name_prefix='analysis')
        self.capacity = threading.BoundedSemaphore(4)
        self.events = {}
        self.lock = threading.Lock()

    def submit(self, kind, source, label):
        if not self.capacity.acquire(blocking=False):
            raise ValueError('Analysis queue is full; try again after a job completes')
        job = self.store.create_job()
        event = threading.Event()
        with self.lock:
            self.events[job['id']] = event
        self.executor.submit(self.run, job['id'], event, kind, source, label)
        return job

    def cancel(self, identifier):
        with self.lock:
            event = self.events.get(identifier)
        if event:
            event.set()
        return self.store.job(identifier)

    def run(self, identifier, event, kind, source, label):
        # Keep untrusted source outside application/reloader trees and persistent storage.
        temporary = Path(tempfile.mkdtemp(prefix='repo-intelligence-snapshot-')).resolve()
        temporary_parent = Path(tempfile.gettempdir()).resolve()
        try:
            if event.is_set():
                raise InterruptedError()
            self.store.update(identifier, status='running', phase='retrieving' if kind == 'github' else 'validating archive', progress=10)
            if kind == 'github':
                archive = temporary / 'input.zip'
                provenance = retrieve(source, archive, event.is_set)
            else:
                archive = source
                provenance = {'kind': 'zip', 'filename': label}
            root = extract_archive(archive, temporary / 'source')
            if event.is_set():
                raise InterruptedError()
            self.store.update(identifier, phase='static analysis and resolution', progress=35)
            graph = analyze(root, event.is_set)
            # Preserve manifest names, otherwise use a neutral source name, not a random temp path.
            root_package = next((p for p in graph.get('packages', []) if p['root'] == '.'), {})
            graph['repository'] = root_package.get('name') or label.removesuffix('.zip') or 'Repository'
            if event.is_set():
                raise InterruptedError()
            self.store.update(identifier, phase='persisting validated graph', progress=90)
            self.store.save(redact(graph), redact(provenance))
            self.store.update(identifier, status='complete', phase='complete', progress=100, snapshot_id=graph['snapshot_id'])
        except InterruptedError:
            self.store.update(identifier, status='cancelled', phase='cancelled', error=None)
        except (ValueError, httpx.HTTPError) as exc:
            message = str(exc) if isinstance(exc, ValueError) else 'GitHub network access failed'
            self.store.update(identifier, status='failed', phase='failed', error=message[:300])
        except Exception:
            # Never return subprocess stderr, file contents or environment values to the UI.
            self.store.update(identifier, status='failed', phase='failed', error='Analysis failed; no result was published')
        finally:
            if temporary.parent != temporary_parent or not temporary.name.startswith('repo-intelligence-snapshot-'):
                raise RuntimeError('Refusing cleanup outside the allocated snapshot directory')
            shutil.rmtree(temporary, onerror=cleanup_error)
            if kind == 'zip':
                source.unlink(missing_ok=True)
            with self.lock:
                self.events.pop(identifier, None)
            self.capacity.release()

    def shutdown(self):
        with self.lock:
            for event in self.events.values():
                event.set()
        self.executor.shutdown(wait=True, cancel_futures=False)
