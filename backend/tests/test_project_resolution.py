"""Project-context resolution must agree with compiler call binding."""
import json

from app.analysis.pipeline import analyze

def write_sources(root, sources):
    for name, text in sources.items():
        target = root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding='utf-8')


def links(graph, kind):
    nodes = {n['id']: n for n in graph['entities']}
    return [(nodes[e['source']], nodes[e['target']], e) for e in graph['edges'] if e['kind'] == kind]


def test_nested_configs_inherit_paths_relative_to_defining_config(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"root"}',
        'config/base.json': json.dumps({'compilerOptions': {'baseUrl': '..', 'paths': {'@shared/*': ['shared/*']}}}),
        'apps/a/tsconfig.json': '{"extends":"../../config/base.json"}',
        'apps/a/main.ts': 'import { run } from "@shared/run"; export function start(){ return run(); }',
        'shared/run.ts': 'export function run(){return 1;}',
        'apps/b/jsconfig.json': '{"compilerOptions":{"baseUrl":".","paths":{"@shared/*":["local/*"]}}}',
        'apps/b/main.js': 'import { run } from "@shared/run"; export function start(){return run();}',
        'apps/b/local/run.js': 'export function run(){return 2;}',
    })
    graph = analyze(tmp_path)
    imports = {(a['file'], b['file']) for a, b, _ in links(graph, 'IMPORTS')}
    assert ('apps/a/main.ts', 'shared/run.ts') in imports
    assert ('apps/b/main.js', 'apps/b/local/run.js') in imports
    calls = {(a['file'], b['file']) for a, b, _ in links(graph, 'CALLS')}
    assert ('apps/a/main.ts', 'shared/run.ts') in calls
    assert ('apps/b/main.js', 'apps/b/local/run.js') in calls
    assert not graph['diagnostics']
    assert analyze(tmp_path) == graph


def test_workspace_exports_resolve_without_installing_and_do_not_guess_dist(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"root","workspaces":["packages/*"]}',
        'packages/web/package.json': '{"name":"web","dependencies":{"@local/core":"workspace:*"}}',
        'packages/web/main.ts': '''import {run} from '@local/core/run';
import {missing} from '@local/core/private';
import {built} from '@local/built';
export function start(){run();missing();built();}''',
        'packages/core/package.json': '{"name":"@local/core","exports":{"./run":"./src/run.ts"}}',
        'packages/core/src/run.ts': 'export function run(){return 1;}',
        'packages/core/private.ts': 'export function missing(){return 2;}',
        'packages/built/package.json': '{"name":"@local/built","main":"./dist/index.js"}',
        'packages/built/src/index.ts': 'export function built(){return 3;}',
    })
    graph = analyze(tmp_path)
    imports = {(a['file'], b.get('file')) for a, b, _ in links(graph, 'IMPORTS')}
    assert ('packages/web/main.ts', 'packages/core/src/run.ts') in imports
    calls = [(a, b) for a, b, _ in links(graph, 'CALLS') if a['file'] == 'packages/web/main.ts']
    assert [b['file'] for _, b in calls] == ['packages/core/src/run.ts']
    assert not any(b.get('file') == 'packages/core/private.ts' for _, b, _ in links(graph, 'IMPORTS'))
    unknown_imports = {u['specifier'] for u in graph['unknowns'] if u['kind'] == 'import'}
    assert {'@local/core/private', '@local/built'} <= unknown_imports


def test_internal_package_named_like_sdk_does_not_create_remote_sdk_claim(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"workspaces":["packages/*"]}',
        'packages/web/package.json': '{"name":"web","dependencies":{"openai":"workspace:*"}}',
        'packages/web/main.ts': 'import {send} from "openai"; export function start(){send();}',
        'packages/core/package.json': '{"name":"openai","exports":"./index.ts"}',
        'packages/core/index.ts': 'export function send(){return 1;}',
    })
    graph = analyze(tmp_path)
    assert len(links(graph, 'CALLS')) == 1
    assert not links(graph, 'SDK_API_CALL')


def test_unavailable_config_never_reads_outside_snapshot(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"root"}',
        'tsconfig.json': '{"extends":"../not-supplied.json","compilerOptions":{"paths":{"@x/*":["src/*"]}}}',
        'main.ts': 'import {run} from "@x/run"; run();',
        'src/run.ts': 'export function run(){return 1;}',
    })
    graph = analyze(tmp_path)
    assert any(d['kind'] == 'project-configuration' for d in graph['diagnostics'])
    assert not links(graph, 'CALLS')
    assert any(u['kind'] == 'import' for u in graph['unknowns'])


def test_imported_values_templates_and_reexports_keep_evidence_and_reject_writes(tmp_path):
    write_sources(tmp_path, {
        'package.json': '{"name":"values"}',
        'config.ts': '''export const base = "https://imported.example.test";
export let stale = "https://stale.example.test"; stale = other;
export const dynamic = process.env.API_URL;''',
        'barrel.ts': 'export {base,stale,dynamic} from "./config";',
        'main.ts': '''import {base as origin, stale, dynamic} from "./barrel";
export function send(){fetch(`${origin}/users`);fetch(stale);fetch(dynamic);}''',
    })
    graph = analyze(tmp_path)
    assert {n['label'] for n in graph['entities'] if n['kind'] == 'external_service'} == {'imported.example.test'}
    assert len([u for u in graph['unknowns'] if u['kind'] == 'http']) == 2
    evidence = {e['id']: e for e in graph['evidence']}
    http = next(e for e in graph['edges'] if e['kind'] == 'CALLS_HTTP')
    assert {evidence[i]['file'] for i in http['evidence_ids']} >= {'main.ts', 'config.ts'}
