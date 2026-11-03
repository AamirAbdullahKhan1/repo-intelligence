from pathlib import Path

from fastapi.testclient import TestClient

from app.analysis.pipeline import analyze
from app.config import Settings
from app.main import create_app


def write(root, name, text):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def test_trusted_libraries_load_without_promoting_signatures_to_bodies(tmp_path):
    write(tmp_path, 'package.json', '{}')
    write(tmp_path, 'main.ts', '''export function run(){
Math.max(1,2); JSON.stringify({}); String(1); [1,2].map(x=>x+1); Promise.resolve(1);
unknownClient.send();
}''')
    g = analyze(tmp_path)
    assert g['coverage']['standard_library_files'] > 0
    assert g['coverage']['known_library_calls'] == 5
    assert len(g['library_references']) == 5
    assert len([u for u in g['unknowns'] if u['kind']=='call']) == 1
    assert not [e for e in g['edges'] if e['kind']=='CALLS']
    assert all(r['evidence_ids'] and r['implementation'].startswith('trusted standard-library') for r in g['library_references'])
    assert analyze(tmp_path) == g


def test_shadowed_global_binds_to_client_source_not_library(tmp_path):
    write(tmp_path, 'package.json', '{}')
    write(tmp_path, 'main.ts', '''const Math={max(a,b){return a;}};
export function run(){return Math.max(1,2);}''')
    g = analyze(tmp_path)
    assert not g['library_references']
    assert len([e for e in g['edges'] if e['kind']=='CALLS']) == 1


def test_delete_one_scan_preserves_others_and_removes_job_pointer(tmp_path):
    for name in ('first','second'):
        write(tmp_path/name,'package.json','{"name":"'+name+'"}')
        write(tmp_path/name,'main.ts','export function run(){return 1;}')
    first,second=(analyze(tmp_path/name) for name in ('first','second'))
    settings=Settings(data_dir=tmp_path/'data',_env_file=None)
    app=create_app(settings)
    with TestClient(app) as client:
        for g in (first,second):app.state.store.save(g,{'kind':'fixture'})
        job=app.state.store.create_job()
        app.state.store.update(job['id'],status='complete',snapshot_id=first['snapshot_id'])
        base='/api/v1/analyses/'+first['snapshot_id']
        assert client.delete(base).json()=={'deleted':first['snapshot_id']}
        for suffix in ('','/view','/overview','/unknowns'):
            assert client.get(base+suffix).status_code==404
        assert client.get('/api/v1/jobs/'+job['id']).status_code==404
        assert client.get('/api/v1/analyses/'+second['snapshot_id']).status_code==200
        assert [s['snapshot_id'] for s in client.get('/api/v1/analyses').json()]==[second['snapshot_id']]
        assert client.delete(base).status_code==404
        assert client.options(base,headers={'Origin':'http://127.0.0.1:5173','Access-Control-Request-Method':'DELETE'}).status_code==200
    with TestClient(create_app(settings)) as reopened:
        assert reopened.get(base).status_code==404
        assert reopened.get('/api/v1/analyses/'+second['snapshot_id']).status_code==200
