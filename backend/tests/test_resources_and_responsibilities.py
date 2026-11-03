import json

from app.analysis.pipeline import analyze
from app.graph.exploration import Index
from app.persistence.store import Store


def write(root, sources):
    for name, text in sources.items():
        p = root / name
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text, encoding='utf-8')


def resource_edges(g):
    return [e for e in g['edges'] if e['kind'] == 'USES_RESOURCE']


def test_worker_r2_use_requires_entry_environment_and_matching_binding(tmp_path):
    write(tmp_path, {
        'package.json': '{"name":"worker"}',
        'wrangler.json': json.dumps({'name':'app','main':'worker.ts','r2_buckets':[{'binding':'DATA','bucket_name':'documents'}]}),
        'worker.ts': '''export default {async fetch(request, env){
 await env.DATA.put('key','value'); return env.DATA.get('key');
}};''',
        'unrelated.ts': 'export function other(env){return env.DATA.get("key");}',
    })
    g = analyze(tmp_path)
    links = resource_edges(g)
    assert len(links) == 2
    assert {e['operation'] for e in links} == {'put','get'}
    assert all(e['resolution'] == 'conditional' and e['profile'] == 'wrangler.json' for e in links)
    evidence = {e['id']:e for e in g['evidence']}
    assert all({evidence[i]['file'] for i in e['evidence_ids']} == {'worker.ts','wrangler.json'} for e in links)
    groups = [n for n in g['entities'] if n.get('projection_rule') == 'responsibility-v1']
    storage = next(n for n in groups if n['responsibility'] == 'Object storage access')
    index = Index(g)
    assert index.candidates(storage['id'])['items']
    workflow = index.workflow(storage['id'])
    assert any(e['kind'] == 'USES_RESOURCE' for e in workflow['edges'])
    overview = index.system()
    assert any(n['label'] == 'documents' for n in overview['nodes'])
    assert any(e['kind'] == 'RESOURCE_USAGE' for e in overview['edges'])
    store = Store(tmp_path.parent / (tmp_path.name + '.sqlite'))
    store.save(g, {'kind':'fixture'})
    reopened = store.analysis(g['snapshot_id'], graph=True)
    assert Index(reopened).system() == overview
    assert all('members' not in n for n in overview['nodes'])
    assert analyze(tmp_path) == g


def test_declared_unused_and_mutated_bindings_are_not_source_usage(tmp_path):
    write(tmp_path, {
        'package.json': '{}',
        'wrangler.json': '{"name":"app","main":"worker.ts","r2_buckets":[{"binding":"DATA","bucket_name":"documents"}]}',
        'worker.ts': '''export default {fetch(request,env){env['DATA']=other;return env.DATA.get('key');}};''',
    })
    g = analyze(tmp_path)
    assert any(e['kind'] == 'BINDS_RESOURCE' for e in g['edges'])
    assert not resource_edges(g)


def test_bound_postgres_redis_clients_link_without_serializing_credentials(tmp_path):
    write(tmp_path, {
        'package.json': '{"dependencies":{"pg":"*","redis":"*"}}',
        'features/operations.ts': '''import {Pool} from 'pg'; import {createClient} from 'redis';
const db=new Pool({connectionString:'postgres://alice:secret@database.internal:5432/app'});
const cache=createClient({url:'redis://bob:secret@cache.internal:6379/0'});
export function read(){return db.query('select 1');}
export function remember(){return cache.set('key','value');}''',
    })
    g = analyze(tmp_path)
    assert len(resource_edges(g)) == 2
    assert 'alice:secret' not in json.dumps(g) and 'bob:secret' not in json.dumps(g)
    groups = [n for n in g['entities'] if n.get('projection_rule') == 'responsibility-v1']
    assert {'Database access','Cache and messaging'} <= {n['responsibility'] for n in groups}
    source = next(n for n in g['entities'] if n['kind']=='symbol' and n['label']=='read')
    assert source['file'] == 'features/operations.ts'
    assert source['component_id'] != next(n['id'] for n in groups if n['responsibility']=='Database access')


def test_unknown_and_replaced_clients_are_not_invented_resources(tmp_path):
    write(tmp_path, {
        'package.json': '{"dependencies":{"pg":"*"}}',
        'main.ts': '''import {Pool} from 'pg';
const unknown = new Pool({connectionString:process.env.DATABASE_URL});
const replaced=new Pool({connectionString:'postgres://db/app'});replaced.query=custom;
export function send(){unknown.query('select 1');replaced.query('select 2');}
class Fake {query(x){return x;}} const fake=new Fake();fake.query('select 3');''',
    })
    g = analyze(tmp_path)
    assert not resource_edges(g)
    assert len([u for u in g['unknowns'] if u['kind']=='resource']) == 1


def test_folder_names_do_not_create_business_or_ui_responsibilities(tmp_path):
    write(tmp_path, {'package.json':'{}','features/payments.ts':'export function run(){return 1;}'})
    g = analyze(tmp_path)
    groups = [n for n in g['entities'] if n.get('projection_rule') == 'responsibility-v1']
    assert {n['responsibility'] for n in groups} == {'Other analyzed source'}
    assert all(n['boundary'] == 'Derived logical role group; not a deployable service' for n in groups)


def test_duplicate_r2_binding_targets_are_ambiguous(tmp_path):
    write(tmp_path, {
        'package.json':'{}',
        'wrangler.json':json.dumps({'name':'app','main':'worker.ts','r2_buckets':[
            {'binding':'DATA','bucket_name':'first'},{'binding':'DATA','bucket_name':'second'}]}),
        'worker.ts':"export default {fetch(request,env){return env.DATA.get('key');}};",
    })
    g = analyze(tmp_path)
    assert not resource_edges(g)
    issue = next(u for u in g['unknowns'] if u['kind']=='resource')
    assert issue['resolution']=='ambiguous' and len(issue['candidate_ids'])==2
