from pathlib import Path
from app.analysis.pipeline import WORKER, analyze
from app.evidence.redaction import redact
from app.graph.projections import architecture_view

def test_express_bound_receivers_and_imported_handler(tmp_path):
    sources={
        'package.json':'{"name":"express-fixture","dependencies":{"express":"fixture"}}',
        'handler.ts':'export function handler(){return save()} function save(){return 1}',
        'main.ts':'''import express from 'express'; import {handler} from './handler';
        const app=express(); app.get('/users',handler);
        const unrelated={get(a,b){}}; unrelated.get('/fake',handler);
        const router=express.Router(); router.post('/local',()=>handler());
        app.get(dynamicPath, handler);
        ''',
    }
    for name,text in sources.items():(tmp_path/name).write_text(text)
    graph=analyze(tmp_path)
    assert {(r['method'],r['path']) for r in graph['routes']}=={('GET','/users'),('POST','/local')}
    assert any(u['kind']=='route' for u in graph['unknowns'])
    assert sum(e['kind']=='HANDLED_BY' for e in graph['edges'])==2
    get=next(r for r in graph['routes'] if r['method']=='GET')
    view=architecture_view(graph,'workflow',entry_id=get['id'])
    assert {'handler','save'} <= {n['label'] for n in view['nodes']}
    dependencies=architecture_view(graph,'workflow',entry_id=get['id'],dependencies=True,depth=5)
    assert any(e['kind']=='DEFINED_IN' for e in dependencies['edges'])

def test_unused_config_yaml_alias_and_secret_redaction(tmp_path):
    (tmp_path/'package.json').write_text('{"name":"fixture"}')
    (tmp_path/'main.ts').write_text("const unused='https://unused.example';")
    (tmp_path/'compose.yaml').write_bytes(b'services:\r\n  app:\r\n    depends_on: [database]\r\n  database:\r\n    image: postgres\r\n')
    graph=analyze(tmp_path)
    assert any(e['kind']=='STARTS_AFTER' for e in graph['edges'])
    assert not any(e['kind']=='CALLS_HTTP' for e in graph['edges'])
    assert not any(n['kind']=='storage' for n in graph['entities'])
    assert redact({'label':'ghp_'+'x'*30,'endpoint':'https://user:password@example.test'})=={'label':'[REDACTED]','endpoint':'[REDACTED]example.test'}

def test_yaml_alias_does_not_infer_deployment(tmp_path):
    (tmp_path/'compose.yaml').write_text('services: &services\n  unsafe: *services\n')
    graph=analyze(tmp_path)
    assert any(d['kind']=='configuration' for d in graph['diagnostics'])
    assert not any(n['kind']=='deployable' for n in graph['entities'])
