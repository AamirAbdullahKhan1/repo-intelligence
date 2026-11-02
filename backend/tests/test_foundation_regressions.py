"""Previously demonstrated false/missing findings, through the real static pipeline."""
import json

from app.analysis.pipeline import analyze


def write_sources(root, sources):
    for name, text in sources.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')


def test_http_literals_reject_all_supported_write_forms_and_keep_evidence(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"value-regression"}',
        'src/stable.ts': '''
const origin = 'https://stable.example.test';
const endpoint = origin + '/v1';
export function send() { return fetch(endpoint); }
''',
        'src/reassigned.ts': '''
let endpoint = 'https://stale.example.test';
endpoint = 'https://replacement.example.test';
export function send() { return fetch(endpoint); }
''',
        'src/writes.ts': '''
let compound = 'https://compound.example.test'; compound += suffix;
let conditional = 'https://conditional.example.test'; if (flag) conditional = other;
let logical = 'https://logical.example.test'; logical ||= other;
let array = 'https://array.example.test'; [array] = values;
let object = 'https://object.example.test'; ({value: object} = values);
let shorthand = 'https://shorthand.example.test'; ({shorthand} = values);
let update = 'https://update.example.test'; update++;
let iteration = 'https://iteration.example.test'; for (iteration of values) {}
let captured = 'https://captured.example.test'; function mutate() { captured = other; }
export function send() {
  fetch(compound); fetch(conditional); fetch(logical); fetch(array);
  fetch(object); fetch(shorthand); fetch(update); fetch(iteration); fetch(captured);
}
''',
        'src/alias.ts': '''
let source = 'https://alias-stale.example.test'; const alias = source; source = other;
export function send() { return fetch(alias); }
''',
        'src/shadow.ts': '''
const endpoint = 'https://shadow-safe.example.test';
export function send() { return fetch(endpoint); }
function unrelated() { let endpoint = ''; endpoint = other; }
''',
        'src/eval.ts': '''
let endpoint = 'https://eval-stale.example.test'; eval(expression);
export function send() { return fetch(endpoint); }
''',
        'src/redeclared.ts': '''
var endpoint = 'https://redeclared-stale.example.test'; var endpoint = other;
export function send() { return fetch(endpoint); }
''',
    })
    graph = analyze(tmp_path)
    hosts = {n['label'] for n in graph['entities'] if n['kind'] == 'external_service'}
    assert hosts == {'stable.example.test', 'shadow-safe.example.test'}
    unknown = [u for u in graph['unknowns'] if u['kind'] == 'http']
    assert len(unknown) == 13
    evidence = {e['id']: e for e in graph['evidence']}
    stable = next(n for n in graph['entities'] if n['label'] == 'stable.example.test')
    edge = next(e for e in graph['edges'] if e['kind'] == 'CALLS_HTTP' and e['target'] == stable['id'])
    rules = [evidence[i]['rule'] for i in edge['evidence_ids']]
    assert rules.count('literal-value-definition') == 2
    assert 'callsite' in rules
    assert analyze(tmp_path) == graph


def test_production_source_in_asset_script_and_plugin_directories_is_connected(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"source-regression"}',
        'src/shared.ts': 'export function shared() { return 1; }',
        'public/runtime.js': '''import {shared} from '../src/shared';
export function play() { shared(); return fetch('https://runtime.example.test'); }
''',
        'scripts/server.ts': "import {shared} from '../src/shared'; export function start() { return shared(); }",
        'plugins/handler.ts': "import {shared} from '../src/shared'; export function handle() { return shared(); }",
        'public/runtime.test.js': "fetch('https://excluded.example.test');",
        'node_modules/vendor/index.js': "fetch('https://vendor.example.test');",
        'public/assets/vendor/library.js': "fetch('https://vendored-asset.example.test');",
        'dist/generated.js': "fetch('https://generated.example.test');",
        'plugins/untrusted.config.js': (
            "require('node:fs').writeFileSync("
            + json.dumps(str(tmp_path / 'TARGET_EXECUTED')) + ", 'unsafe');"
        ),
    })
    graph = analyze(tmp_path)
    nodes = {n['id']: n for n in graph['entities']}
    callers = {
        nodes[e['source']].get('file')
        for e in graph['edges']
        if e['kind'] == 'CALLS' and nodes[e['target']]['label'] == 'shared'
    }
    assert callers == {'public/runtime.js', 'scripts/server.ts', 'plugins/handler.ts'}
    hosts = {n['label'] for n in graph['entities'] if n['kind'] == 'external_service'}
    assert hosts == {'runtime.example.test'}
    assert graph['coverage']['parsed_source_files'] == 5
    assert not (tmp_path / 'TARGET_EXECUTED').exists()
    assert graph['scope']['client_code_executed'] is False
    assert any(s['file'] == 'public/runtime.test.js' for s in graph['coverage']['skipped'])


def test_next_root_and_nested_routes_use_the_owning_package_root(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"root","dependencies":{"next":"fixture"}}',
        'src/app/route.ts': 'export function GET() { return load(); } function load() { return 1; }',
        'src/app/(site)/users/[id]/route.ts': 'export const POST = () => 1;',
        'src/app/not-route.ts': 'export function DELETE() { return 1; }',
        'src/app/route.test.ts': 'export function PATCH() { return 1; }',
        'src/examples/app/route.ts': 'export function OPTIONS() { return 1; }',
        'packages/web/package.json': '{"name":"web","dependencies":{"next":"fixture"}}',
        'packages/web/app/route.js': 'export const HEAD = () => 1;',
        'packages/web/app/api/status/route.js': 'export function GET() { return 1; }',
    })
    graph = analyze(tmp_path)
    assert {(r['file'], r['method'], r['path']) for r in graph['routes']} == {
        ('src/app/route.ts', 'GET', '/'),
        ('src/app/(site)/users/[id]/route.ts', 'POST', '/users/[id]'),
        ('packages/web/app/route.js', 'HEAD', '/'),
        ('packages/web/app/api/status/route.js', 'GET', '/api/status'),
    }
    route_ids = {r['id'] for r in graph['routes']}
    assert {e['source'] for e in graph['edges'] if e['kind'] == 'HANDLED_BY'} == route_ids
    assert {e['target'] for e in graph['edges'] if e['kind'] == 'REGISTERS_ROUTE'} == route_ids
