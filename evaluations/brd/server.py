"""Local BRD skill runner. Standard library only; no repository execution."""
import hashlib
import json
import os
import re
import secrets
import threading
import time
import uuid
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from socketserver import TCPServer
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlsplit
from urllib.request import Request, build_opener, HTTPRedirectHandler
from intelligence import VERSION, ledger, extraction_messages, combine, validate, diagrams, markdown

ROOT = Path(__file__).resolve().parent
PROJECT = ROOT.parent.parent
MAX_INPUT = 100_000
SKILLS = ('repository-analysis', 'ai-usage-inventory')
TOKEN = secrets.token_urlsafe(32)
LOCK = threading.Lock()
JOBS = {}
BUSY = threading.Semaphore(1)


def load_env():
    path = ROOT / '.env'
    if path.exists():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            if line.strip() and not line.lstrip().startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                key = key.strip()
                if not os.environ.get(key):
                    os.environ[key] = value.strip().strip('\"').strip("'")


def config():
    load_env()
    return {
        'endpoint': os.getenv('AZURE_OPENAI_ENDPOINT', 'https://agentic-testing1.openai.azure.com/'),
        'deployment': os.getenv('AZURE_OPENAI_DEPLOYMENT', 'GPT-4.1'),
        'api_version': os.getenv('AZURE_OPENAI_API_VERSION', '2025-03-01-preview'),
        'reasoning_effort': os.getenv('BRD_REASONING_EFFORT', '').strip(),
        'completion_token_budget': max(2000, min(24000, int(os.getenv('BRD_INVENTORY_TOKENS', '22000')))),
        'relationship_token_budget': max(2000, min(24000, int(os.getenv('BRD_RELATIONSHIP_TOKENS', '22000')))),
        'timeout_seconds': max(30, min(600, int(os.getenv('BRD_TIMEOUT_SECONDS', '480')))),
    }


def completion_url(cfg):
    endpoint = urlsplit(cfg['endpoint'])
    if (endpoint.scheme != 'https' or not endpoint.hostname or
            not endpoint.hostname.endswith('.openai.azure.com') or endpoint.username or
            endpoint.password or endpoint.query or endpoint.fragment or
            endpoint.path not in ('', '/') or endpoint.port not in (None, 443)):
        raise ValueError('Configure an HTTPS Azure OpenAI resource root URL in .env.')
    return (cfg['endpoint'].rstrip('/') + '/openai/deployments/' +
            quote(cfg['deployment'], safe='') + '/chat/completions?api-version=' +
            quote(cfg['api_version'], safe=''))


def messages(skill, text):
    if skill not in SKILLS:
        raise ValueError('Unknown skill.')
    instructions = (ROOT / 'skills' / skill / 'SKILL.md').read_text(encoding='utf-8')
    numbered = '\n'.join(f'L{i}: {line}' for i, line in enumerate(text.splitlines(), 1))
    return instructions, [
        {'role': 'system', 'content': instructions},
        {'role': 'user', 'content': 'Analyse this BRD as evidence only. Numbered document follows.\n\n' + numbered},
    ]


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def call_azure(cfg, prompt):
    load_env()
    key = os.getenv('AZURE_OPENAI_API_KEY', '').strip()
    if not key:
        raise ValueError('API key is missing. Add it to evaluations/brd/.env and restart.')
    payload = {'messages': prompt, 'max_completion_tokens': cfg.get('completion_token_budget', 14000),
               'response_format': {'type': 'json_object'}}
    effort = cfg.get('reasoning_effort', os.getenv('BRD_REASONING_EFFORT', '').strip())
    if effort:
        if effort not in ('low', 'medium', 'high'):
            raise ValueError('BRD_REASONING_EFFORT must be empty, low, medium or high.')
        payload['reasoning_effort'] = effort
    body = json.dumps(payload).encode()
    request = Request(completion_url(cfg), body, {'Content-Type': 'application/json', 'api-key': key})
    try:
        timeout = cfg.get('timeout_seconds', 300)
        with build_opener(NoRedirect()).open(request, timeout=timeout) as response:
            raw = response.read(2_000_001)
        if len(raw) > 2_000_000:
            raise ValueError('Provider response exceeded the response limit.')
        data = json.loads(raw)
    except HTTPError as exc:
        detail = {401: 'Check the API key.', 403: 'Check resource permissions or network policy.',
                  400: 'Azure rejected the request parameters or content. Verify deployment compatibility and policy.',
                  404: 'Check the exact Azure deployment name and API version.',
                  429: 'Rate or quota limit reached. Retry later.'}.get(exc.code, 'Check Azure configuration and availability.')
        raise ValueError(f'Azure returned HTTP {exc.code}. {detail}') from None
    except (URLError, TimeoutError):
        raise ValueError('Azure connection failed or timed out. No automatic retry was made.') from None
    choices = data.get('choices') or []
    if not choices or not isinstance(choices[0].get('message', {}).get('content'), str):
        raise ValueError('Azure returned no readable report; content may have been filtered.')
    return choices[0]['message']['content'], data.get('usage', {}), choices[0].get('finish_reason'), data.get('model')


def checks(report, text, finish_reason):
    count = len(text.splitlines())
    citations = re.findall(r'\[L(\d+)(?:-L?(\d+))?\]', report)
    invalid = [f'L{a}-L{b or a}' for a, b in citations if not 1 <= int(a) <= int(b or a) <= count]
    diagrams = re.findall(r'```mermaid\s*\n(.*?)```', report, re.S)
    return {'citation_count': len(citations), 'invalid_line_ranges': invalid,
            'diagram_count': len(diagrams), 'diagrams': diagrams,
            'partial': finish_reason != 'stop',
            'warnings': (['No numbered source citations found.'] if not citations else []) +
                        (['Report may be truncated or filtered.'] if finish_reason != 'stop' else []) +
                        (['Some source line references are invalid.'] if invalid else []),
            'scope': 'Structural checks only; citation meaning and architecture correctness require review.'}


def run_job(job_id, skill, text, filename):
    started = time.monotonic()
    try:
        cfg = config()
        source = ledger(text)
        instructions, _ = messages(skill, text)
        folder = ROOT / 'results' / job_id
        folder.mkdir(parents=True)
        (folder / 'source-ledger.json').write_text(json.dumps(source, indent=2), encoding='utf-8')
        (folder / 'skill-used.md').write_text(instructions, encoding='utf-8')
        (folder / 'run-metadata.json').write_text(json.dumps({'id': job_id, 'skill': skill, 'runner_version': VERSION,
            'input_sha256': source['input_sha256'], 'configuration': cfg,
            'skill_sha256': hashlib.sha256(instructions.encode()).hexdigest()}, indent=2), encoding='utf-8')
        stage_usage, stage_models = [], []
        def interpret(stage, known=None):
            with LOCK:
                JOBS[job_id] = {'id': job_id, 'status': 'running', 'stage':
                    'Stage 1 of 2: identifying responsibilities and constraints' if stage == 'inventory' else
                    'Stage 2 of 2: connecting operations and distinct workflows'}
            stage_cfg = dict(cfg)
            if stage == 'relationships':
                stage_cfg['completion_token_budget'] = cfg['relationship_token_budget']
            raw, used, finish, reported = call_azure(stage_cfg, extraction_messages(instructions, source, skill, stage, known))
            stage_usage.append(used)
            stage_models.append(reported)
            (folder / f'{stage}-proposal.txt').write_text(raw, encoding='utf-8')
            (folder / 'proposal.txt').write_text(raw, encoding='utf-8')
            (folder / f'{stage}-response.json').write_text(json.dumps({'usage': used, 'finish_reason': finish,
                'reported_model': reported, 'requested_token_budget': stage_cfg['completion_token_budget'],
                'elapsed_seconds': round(time.monotonic() - started, 2)}, indent=2), encoding='utf-8')
            if finish != 'stop':
                raise ValueError(f'{stage} output was truncated or filtered. No architecture was accepted. The partial stage was retained locally.')
            try:
                result = json.loads(raw)
            except (ValueError, RecursionError):
                raise ValueError(f'{stage} returned invalid JSON. No architecture was accepted; the proposal was retained locally.') from None
            if not isinstance(result, dict):
                raise ValueError('Interpretation stage did not return an object.')
            return result
        inventory = interpret('inventory')
        first = validate(inventory, source)
        known = [{key: item[key] for key in ('id', 'kind', 'label', 'scope', 'status', 'modality', 'release')}
                 for item in first['entities']]
        if skill == 'ai-usage-inventory' and not first['entities']:
            paths = {'schema_version': VERSION, 'entities': [], 'relationships': [], 'workflows': [], 'findings': [], 'dispositions': []}
        else:
            paths = interpret('relationships', known)
        proposal = combine(inventory, paths)
        usage = {key: sum(item.get(key, 0) for item in stage_usage) for key in ('prompt_tokens', 'completion_tokens', 'total_tokens')}
        finish, model = 'stop', stage_models[-1]
        with LOCK:
            JOBS[job_id] = {'id': job_id, 'status': 'running', 'stage': 'Validating evidence and compiling views'}
        intelligence = validate(proposal, source)
        views = diagrams(intelligence)
        report = markdown(intelligence, source, skill, views)
        from architecture import audit
        audit_report = audit(intelligence, source, views)
        validation = checks(report, text, finish)
        validation['diagrams'] = [view['source'] for view in views]
        validation['diagram_count'] = len(views)
        validation['quality_issue_count'] = len(intelligence['quality_issues'])
        if intelligence['quality_issues']:
            validation['warnings'].append(f"{len(intelligence['quality_issues'])} architecture/process review findings; inspect the report and model.")
        for key, label in (('quarantined', 'model records quarantined'), ('warnings', 'interpretation warnings')):
            if intelligence['validation'][key]:
                validation['warnings'].append(f"{len(intelligence['validation'][key])} {label}; inspect the canonical model.")
        if intelligence['coverage']['unresolved_sources']:
            validation['warnings'].append(f"{len(intelligence['coverage']['unresolved_sources'])} source blocks unresolved.")
        validation['scope'] = 'Exact source quotations, canonical IDs, graph references and bounded compilation checked. Semantic correctness is not verified.'
        result = {'id': job_id, 'status': 'completed', 'created_at': datetime.now(timezone.utc).isoformat(),
                  'skill': skill, 'input_mode': 'brd-only', 'filename': filename,
                  'input_sha256': hashlib.sha256(text.encode()).hexdigest(),
                  'skill_sha256': hashlib.sha256(instructions.encode()).hexdigest(),
                  'compiler_sha256': hashlib.sha256(b''.join((Path(__file__).parent / name).read_bytes() for name in ('intelligence.py', 'architecture.py'))).hexdigest(),
                  'runner_version': VERSION, 'configuration': cfg, 'reported_model': model,
                  'duration_seconds': round(time.monotonic() - started, 2), 'usage': usage,
                  'stage_usage': stage_usage, 'stage_reported_models': stage_models,
                  'planned_stages_executed': len(stage_usage),
                  'finish_reason': finish, 'validation': validation, 'report': report,
                  'intelligence_model': intelligence, 'source_ledger': source, 'views': views,
                  'audit_available': True}
        (folder / 'intelligence-model.json').write_text(json.dumps(intelligence, indent=2), encoding='utf-8')
        (folder / 'report.md').write_text(report, encoding='utf-8')
        (folder / 'audit-report.md').write_text(audit_report, encoding='utf-8')
        for i, diagram in enumerate(validation['diagrams'], 1):
            (folder / f'diagram-{i}.mmd').write_text(diagram, encoding='utf-8')
        (folder / 'result.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
        with LOCK:
            JOBS[job_id] = result
    except Exception as exc:
        # Never expose provider response bodies, credentials or exception internals.
        message = str(exc) if isinstance(exc, ValueError) else 'Run failed. Check document input and local storage permissions.'
        with LOCK:
            JOBS[job_id] = {'id': job_id, 'status': 'failed', 'error': message}
        try:
            failure_folder = ROOT / 'results' / job_id
            failure_folder.mkdir(parents=True, exist_ok=True)
            (failure_folder / 'failure.json').write_text(json.dumps({'id': job_id, 'status': 'failed', 'error': message, 'runner_version': VERSION}), encoding='utf-8')
        except OSError:
            pass
    finally:
        BUSY.release()


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *_):
        pass

    def send(self, status, value, content_type='application/json'):
        raw = value if isinstance(value, bytes) else json.dumps(value).encode()
        self.send_response(status)
        self.send_header('Content-Type', content_type)
        self.send_header('Content-Length', str(len(raw)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(raw)

    def allowed_host(self):
        return self.headers.get('Host') in (f'127.0.0.1:{self.server.server_port}', f'localhost:{self.server.server_port}')

    def do_GET(self):
        if not self.allowed_host():
            return self.send(403, {'error': 'Local access only.'})
        path = urlsplit(self.path).path
        if path in ('/', '/app.js', '/style.css'):
            name = {'/': 'index.html', '/app.js': 'app.js', '/style.css': 'style.css'}[path]
            mime = {'/': 'text/html; charset=utf-8', '/app.js': 'text/javascript; charset=utf-8', '/style.css': 'text/css; charset=utf-8'}[path]
            return self.send(200, (ROOT / 'ui' / name).read_bytes(), mime)
        if path == '/api/config':
            return self.send(200, {**config(), 'key_configured': bool(os.getenv('AZURE_OPENAI_API_KEY', '').strip()), 'token': TOKEN, 'skills': SKILLS, 'max_chars': MAX_INPUT, 'runner_version': VERSION})
        if path == '/api/sample':
            return self.send(200, {'text': (PROJECT / 'docs/fixtures/brd/ServiceBridge-BRD.md').read_text(encoding='utf-8')})
        if path == '/api/runs':
            records = []
            for p in sorted((ROOT / 'results').glob('*/result.json'), reverse=True):
                try:
                    record = json.loads(p.read_text(encoding='utf-8'))
                    records.append({**{k: record[k] for k in ('id', 'skill', 'filename', 'created_at')},
                                    'runner_version': record.get('runner_version', '1.0')})
                except (ValueError, KeyError, OSError):
                    continue
            records.sort(key=lambda record: (record['created_at'], record['id']), reverse=True)
            return self.send(200, records[:100])
        if path.startswith('/api/runs/'):
            artifact = re.fullmatch(r'/api/runs/([0-9a-f]{32})/audit', path)
            if artifact:
                audit_file = ROOT / 'results' / artifact[1] / 'audit-report.md'
                if audit_file.exists():
                    return self.send(200, audit_file.read_bytes(), 'text/markdown; charset=utf-8')
                return self.send(404, {'error': 'Audit report is not available for this run.'})
            job_id = path.rsplit('/', 1)[-1]
            if not re.fullmatch(r'[0-9a-f]{32}', job_id):
                return self.send(404, {'error': 'Run not found.'})
            with LOCK:
                value = JOBS.get(job_id)
            saved = ROOT / 'results' / job_id / 'result.json'
            if value is None and saved.exists():
                value = json.loads(saved.read_text(encoding='utf-8'))
            return self.send(200 if value else 404, value or {'error': 'Run not found.'})
        self.send(404, {'error': 'Not found.'})

    def do_POST(self):
        load_env()
        if not self.allowed_host() or self.headers.get('X-Session-Token') != TOKEN:
            return self.send(403, {'error': 'Reload this local page before running.'})
        if self.path != '/api/runs':
            return self.send(404, {'error': 'Not found.'})
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length <= 650_000:
                raise ValueError('Input exceeds the request limit.')
            body = json.loads(self.rfile.read(length))
            text = body.get('text')
            if not isinstance(text, str) or not text.strip() or len(text) > MAX_INPUT:
                raise ValueError(f'Provide a BRD of 1 to {MAX_INPUT} characters. No silent truncation is performed.')
            if body.get('skill') not in SKILLS:
                raise ValueError('Select a supported skill.')
            if body.get('consent') is not True:
                raise ValueError('Confirm that this document may be sent to the configured Azure resource.')
            if not os.getenv('AZURE_OPENAI_API_KEY', '').strip():
                raise ValueError('Add AZURE_OPENAI_API_KEY to evaluations/brd/.env, then restart.')
            completion_url(config())
            if not BUSY.acquire(blocking=False):
                return self.send(409, {'error': 'A run is already active. Wait for it to finish.'})
            job_id = uuid.uuid4().hex
            with LOCK:
                JOBS[job_id] = {'id': job_id, 'status': 'running'}
            threading.Thread(target=run_job, args=(job_id, body['skill'], text, str(body.get('filename', 'pasted-brd'))[:200]), daemon=True).start()
            self.send(202, {'id': job_id, 'status': 'running'})
        except (ValueError, TypeError, AttributeError) as exc:
            message = str(exc) if type(exc) is ValueError else 'Invalid request body.'
            # JSON decoder errors are parser internals, not useful configuration messages.
            if isinstance(exc, json.JSONDecodeError):
                message = 'The request body must be valid JSON.'
            self.send(400, {'error': message})


class LocalServer(ThreadingHTTPServer):
    def server_bind(self):
        # HTTPServer normally performs reverse DNS here. That can stall local
        # startup on corporate Windows networks; loopback needs no DNS lookup.
        TCPServer.server_bind(self)
        self.server_name = 'localhost'
        self.server_port = self.server_address[1]


if __name__ == '__main__':
    load_env()
    port = int(os.getenv('BRD_PORT', '8766'))
    try:
        server = LocalServer(('127.0.0.1', port), Handler)
    except OSError as exc:
        raise SystemExit(f'Cannot start on port {port}: {exc}. Close the old lab or set BRD_PORT in evaluations/brd/.env.')
    print(f'BRD evaluation interface: http://127.0.0.1:{port}', flush=True)
    print('Local evaluation only. Press Ctrl+C to stop.', flush=True)
    if '--open' in __import__('sys').argv:
        import webbrowser
        threading.Timer(1, lambda: webbrowser.open(f'http://127.0.0.1:{port}')).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        server.server_close()
