"""HTTP matching requires context and preserves uncertainty at both ends."""
from app.analysis.pipeline import analyze
from app.graph.projections import project
from app.graph.exploration import Index


def write(root, sources):
    for name, text in sources.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')


def test_next_client_method_route_link_is_conditional_with_both_ends(tmp_path):
    write(tmp_path, {
        'package.json': '{"name":"web","dependencies":{"next":"*"}}',
        'app/client.ts': ''''use client';
const method = 'POST';
export function send(){return fetch('/api/users/alice?active=1', {method: method});}''',
        'app/api/users/[id]/route.ts': 'export async function POST(){return 1;} export function GET(){return 2;}',
    })
    g = analyze(tmp_path)
    nodes = {n['id']: n for n in g['entities']}
    edges = [e for e in g['edges'] if e['kind'] == 'CALLS_HTTP']
    assert len(edges) == 1
    e = edges[0]
    assert e['resolution'] == 'conditional'
    assert e['method'] == 'POST'
    assert nodes[e['target']]['label'] == 'POST /api/users/[id]'
    evidence = {x['id']: x for x in g['evidence']}
    assert {evidence[i]['file'] for i in e['evidence_ids']} == {'app/client.ts', 'app/api/users/[id]/route.ts'}
    assert not [u for u in g['unknowns'] if u['kind'] == 'http']
    projected = [e for e in project(g)['components']['edges'] if e['kind'] == 'CALLS_HTTP']
    assert projected and all(e['resolution'] == 'conditional' for e in projected)
    assert analyze(tmp_path) == g


def test_unknown_methods_origins_and_cross_package_routes_are_not_guessed(tmp_path):
    write(tmp_path, {
        'package.json': '{"name":"web","dependencies":{"next":"*"}}',
        'app/client.ts': ''''use client';
export function send(){
 fetch('/api/x', {method: verb}); fetch('/api/x', {...options});
 fetch('//remote.test/api/x'); fetch('/api/other'); fetch('/api/x', {method:'POST'});
 fetch('/api/%78');
}''',
        'app/server.ts': 'export function send(){fetch("/api/x");}',
        'app/api/x/route.ts': 'export function GET(){}',
        'packages/other/package.json': '{"name":"other","dependencies":{"next":"*"}}',
        'packages/other/app/api/other/route.ts': 'export function GET(){}',
    })
    g = analyze(tmp_path)
    assert not [e for e in g['edges'] if e['kind'] == 'CALLS_HTTP']
    assert len([u for u in g['unknowns'] if u['kind'] == 'http']) == 7


def test_colliding_route_patterns_keep_candidates_without_a_verified_edge(tmp_path):
    write(tmp_path, {
        'package.json': '{"dependencies":{"next":"*"}}',
        'app/client.ts': "'use client'; export function send(){fetch('/api/alice');}",
        'app/api/[id]/route.ts': 'export function GET(){}',
        'app/(group)/api/[name]/route.ts': 'export function GET(){}',
    })
    g = analyze(tmp_path)
    assert not [e for e in g['edges'] if e['kind'] == 'CALLS_HTTP']
    u = next(u for u in g['unknowns'] if u['kind'] == 'http')
    assert u['resolution'] == 'ambiguous'
    assert len(u['candidate_ids']) == 2
    index = Index(g)
    i = next(i for i, u in enumerate(g['unknowns']) if u['kind'] == 'http')
    node, edge = index.uncertainty(i)
    assert node['resolution'] == edge['resolution'] == 'ambiguous'
    assert len(node['candidate_ids']) == 2
    assert next(x for x in index.issues()['items'] if x['unknown_index'] == i)['resolution'] == 'ambiguous'


def test_routing_configuration_is_reported_without_executing_it(tmp_path):
    sentinel = tmp_path / 'executed'
    write(tmp_path, {
        'package.json': '{"dependencies":{"next":"*"}}',
        'app/client.ts': "'use client'; export function send(){fetch('/api/x');}",
        'app/api/x/route.ts': 'export function GET(){}',
        'next.config.js': 'require("fs").writeFileSync("executed", "bad"); module.exports={};',
    })
    g = analyze(tmp_path)
    e = next(e for e in g['edges'] if e['kind'] == 'CALLS_HTTP')
    assert e['resolution'] == 'conditional'
    assert e['routing_config_files'] == ['next.config.js']
    assert not sentinel.exists()


def test_lookalike_client_directive_and_noncallable_exports_do_not_link(tmp_path):
    write(tmp_path, {
        'package.json': '{"dependencies":{"next":"*"}}',
        'app/notclient.ts': "const x=1; 'use client'; export function send(){fetch('/api/x');}",
        'app/client.ts': "'use client'; export function send(){fetch('/api/y');fetch('/api//x');}",
        'app/api/x/route.ts': 'export function GET(){}',
        'app/api/y/route.ts': 'export const GET=123;',
    })
    g = analyze(tmp_path)
    assert not [e for e in g['edges'] if e['kind'] == 'CALLS_HTTP']
    assert len([u for u in g['unknowns'] if u['kind'] == 'http']) == 3
