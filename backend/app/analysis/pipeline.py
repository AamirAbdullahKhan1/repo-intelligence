"""Bounded worker IPC, contract checking, grounding, and snapshot integrity."""
import json
import hashlib
from importlib.metadata import version
from pydantic import ValidationError
import os
from pathlib import Path
import queue
import subprocess
import threading
import time
from app.contracts import Graph
from app.evidence.validation import validate
from app.evidence.redaction import redact
from app.ingestion.snapshot import freeze, fingerprint
from app.analysis.configuration import augment

WORKER = Path(__file__).resolve().parents[2] / 'workers/typescript/index.cjs'

def analyze(root: Path, cancelled=lambda: False, timeout=120) -> dict:
    before = freeze(root)
    environment = {k: v for k, v in os.environ.items() if k.upper() in
                   ('PATH', 'SYSTEMROOT', 'WINDIR', 'TEMP', 'TMP', 'PATHEXT')}
    events = queue.Queue(maxsize=16)
    process = subprocess.Popen(['node', '--max-old-space-size=1536', str(WORKER), str(root)],
                               cwd=WORKER.parent, env=environment, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    def reader():
        try:
            while chunk := process.stdout.read(65536):
                events.put(chunk)
        finally:
            events.put(None)
    thread = threading.Thread(target=reader, daemon=True)
    thread.start()
    chunks, size, start = [], 0, time.monotonic()
    try:
        while True:
            if cancelled():
                raise InterruptedError('Cancelled')
            if time.monotonic() - start > timeout:
                raise ValueError('Static worker exceeded its time limit')
            try:
                chunk = events.get(timeout=.1)
            except queue.Empty:
                continue
            if chunk is None:
                break
            size += len(chunk)
            if size > 64 * 1024 * 1024:
                raise ValueError('Static worker exceeded its output limit')
            chunks.append(chunk)
        process.wait(timeout=5)
        if process.returncode:
            raise ValueError('Static worker failed; check its installation and repository limits')
        try:
            graph = Graph.model_validate_json(b''.join(chunks)).model_dump()
            augment(graph, root)
            graph = Graph.model_validate(graph).model_dump()
        except ValidationError as exc:
            # Pydantic error strings can contain input values. Do not return them to API clients.
            raise ValueError('Static worker output failed the graph contract; no result published') from exc
        graph['input_snapshot_id'] = hashlib.sha256(json.dumps(before,sort_keys=True).encode()).hexdigest()
        # Include all input bytes and Python semantic adapter versions, not only parsed TS text.
        app_root=Path(__file__).resolve().parents[1]
        semantic_sources=sorted([*Path(__file__).parent.glob('*.py'),*app_root.joinpath('evidence').glob('*.py'),app_root/'contracts.py'])
        python_hash = hashlib.sha256(b''.join(p.relative_to(app_root).as_posix().encode()+p.read_bytes() for p in semantic_sources)
                                     +version('pydantic').encode()+version('PyYAML').encode()).hexdigest()
        graph['python_engine_sha256']=python_hash
        graph['snapshot_id'] = hashlib.sha256((graph['snapshot_id']+graph['input_snapshot_id']+python_hash).encode()).hexdigest()
        if fingerprint(root) != before:
            raise ValueError('Snapshot integrity changed during analysis')
        validate(graph, root.resolve())
        # Input/temp directory names must not change an otherwise identical snapshot.
        return redact(graph)
    finally:
        if process.poll() is None:
            process.kill()
        # Drain a bounded producer after killing, so cancellation cannot leave a blocked thread.
        while thread.is_alive():
            try:
                events.get(timeout=.1)
            except queue.Empty:
                pass
        thread.join(timeout=1)
        process.wait(timeout=5)
        process.stdout.close()
