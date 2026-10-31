"""Presentation regressions over known canonical facts, including negative cases."""
import copy
import hashlib
import json
import sqlite3
import sys
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
from app.graph.exploration import Index
from app import tooling

@pytest.fixture
def graph():
    nodes=[dict(id='app',kind='application',label='sample',root='.',technology='Next.js package',evidence_ids=['ev'])]
    ev=[dict(id='ev',file='src/server/orders/main.ts',start=0,end=100,line=1,column=1,sha256='a'*64,rule='symbol-declaration')]
    for key,group in [('orders','src/server/orders'),('view','src/components'),('store','src/server/store')]:
        nodes.append(dict(id=key,kind='component',label=key,group=group,application_id='app',evidence_ids=['ev']))
        nodes.append(dict(id=key+'file',kind='file',label=key+'.ts',file='src/server/'+key+'/main.ts',component_id=key,application_id='app',evidence_ids=['ev']))
    nodes += [dict(id='entry',kind='endpoint',label='GET /orders',file='src/server/orders/main.ts',component_id='orders',application_id='app',evidence_ids=['ev'])]
    for i,(owner,label) in enumerate([('orders','handleOrders'),('orders','helper'),('store','save'),('view','Page')]):
        eid='ev'+str(i);ev.append(dict(ev[0],id=eid,start=i*10,end=i*10+8))
        nodes.append(dict(id=label,kind='symbol',label=label,file='src/server/'+owner+'/main.ts',component_id=owner,application_id='app',has_body=True,evidence_ids=[eid],declaration_kind='FunctionDeclaration'))
    nodes += [dict(id='klass',kind='symbol',label='Orders',file='src/server/orders/main.ts',component_id='orders',application_id='app',has_body=False,declaration_kind='ClassDeclaration',evidence_ids=['ev']),
              dict(id='sdk',kind='sdk',label='pg (SDK)',evidence_ids=['ev'])]
    def edge(key,source,target,kind='CALLS',resolution='resolved'):
        return dict(id=key,source=source,target=target,kind=kind,resolution=resolution,evidence_ids=['ev'])
    edges=[edge('registration','entry','handleOrders','HANDLED_BY'),edge('save1','handleOrders','save'),edge('save2','handleOrders','save'),
           edge('conditional','handleOrders','helper','CONTAINS_SYMBOL','conditional'),edge('ambiguous','helper','save','CALLS','ambiguous'),
           edge('sdkcall','save','sdk','SDK_API_CALL'),edge('import','ordersfile','storefile','IMPORTS')]
    unknown_ev=dict(ev[0],id='unknown-ev',start=2,end=3,rule='callsite');ev.append(unknown_ev)
    return dict(schema_version='repo-intelligence-1',snapshot_id='a'*64,repository='sample',typescript_version='5.9.3',
                entities=nodes,edges=edges,evidence=ev,unknowns=[dict(kind='call',file='src/server/orders/main.ts',line=1,reason='compiler target unavailable',evidence_ids=['unknown-ev'])],
                coverage={'inventoried_files':3,'parsed_source_files':3,'skipped':[]},scope={},packages=[],languages={'.ts':3})

def test_overview_is_bounded_and_preserves_canonical_graph(graph):
    before=copy.deepcopy(graph);index=Index(graph);view=index.system(limit=14)
    assert len(view['nodes'])<=14 and len(view['edges'])<=24
    assert not any(n['kind'] in ('file','symbol','endpoint') for n in view['nodes'])
    assert not any(e['kind'] in ('CALLS','IMPORTS') for e in view['edges'])
    assert 'orders' in {n['id'] for n in view['nodes']}
    canonical_edges={e['id'] for e in graph['edges']}
    assert all(set(e.get('support_edge_ids',[]))<=canonical_edges for e in view['edges'])
    assert graph==before

def test_hierarchy_paginates_original_ids_and_classes(graph):
    index=Index(graph)
    assert index.hierarchy()['items'][0]['id']=='app'
    first=index.hierarchy('app',limit=2);second=index.hierarchy('app',offset=2,limit=2)
    assert first['total']==3 and len(first['items'])==2 and len(second['items'])==1
    assert not ({n['id'] for n in first['items']}&{n['id'] for n in second['items']})
    children=index.hierarchy('orders')['items']
    assert {'entry','handleOrders','helper','klass'}=={n['id'] for n in children}
    assert index.hierarchy('orders',query='handleOrders')['total']==1

def test_workflow_scope_and_distinct_resolution(graph):
    index=Index(graph)
    view=index.workflow('orders','entry',depth=3,nested=True)
    assert view['metadata']['scope_id']=='orders'
    links=[e for e in view['edges'] if e['source']=='handleOrders' and e['target']=='save']
    assert len(links)==1 and links[0]['count']==2
    assert set(links[0]['support_edge_ids'])=={'save1','save2'}
    record=index.evidence_record(links[0]['id'],'orders')
    assert record['source_label']=='handleOrders' and record['target_label']=='save'
    assert len(record['supporting_relationships'])==2
    assert {'conditional','ambiguous','confirmed'} <= {e['resolution'] for e in view['edges']}
    assert not any(e['kind']=='IMPORTS' for e in view['edges'])
    with pytest.raises(ValueError):index.workflow('view','entry')
    assert not index.workflow('group:sdk')['nodes']

def test_unresolved_marker_is_not_an_inferred_target(graph):
    index=Index(graph)
    assert not any(n['kind']=='unresolved' for n in index.workflow('orders','entry')['nodes'])
    view=index.workflow('orders','entry',show_unknown=True,limit=14)
    markers=[n for n in view['nodes'] if n['kind']=='unresolved']
    assert len(markers)==1
    link=next(e for e in view['edges'] if e['kind']=='UNRESOLVED_REFERENCE')
    assert link['source']=='handleOrders' and link['target']==markers[0]['id']
    assert link['resolution']=='unresolved' and link['evidence_ids']==['unknown-ev']
    assert 'no target' in link['limitation']
    assert index.evidence_record(markers[0]['id'])['reason']=='compiler target unavailable'
    assert index.issues('view')['total']==0 and index.issues('orders')['total']==1
    assert len(view['nodes'])<=14 and len(view['edges'])<=100

def test_api_saved_graph_stays_unchanged_and_limits_are_enforced(graph,tmp_path):
    settings=Settings(data_dir=tmp_path,_env_file=None)
    with TestClient(create_app(settings)) as client:
        client.app.state.store.save(graph,{'kind':'fixture'})
        base='/api/v1/analyses/'+graph['snapshot_id']
        with sqlite3.connect(tmp_path/'analysis.sqlite') as db:before=db.execute('select graph from analyses').fetchone()[0]
        assert client.get(base+'/overview').json()['module_count']==3
        assert client.get(base+'/hierarchy?parent_id=orders&limit=2').json()['total']==4
        assert client.get(base+'/explore/entries?scope_id=orders&query=helper').json()['items'][0]['id']=='helper'
        assert client.get(base+'/hierarchy?limit=61').status_code==422
        assert client.get(base+'/hierarchy?parent_id=absent').status_code==422
        assert client.get(base+'/view?scope_id=orders&kind=workflow').status_code==200
        assert client.get(base+'/unknowns?scope_id=view').json()['total']==0
        tools=client.get('/api/v1/tools').json()
        assert tools['interpreter']==sys.executable
        assert tools['tools']['pyyaml']['metadata_matches_loaded']
        with sqlite3.connect(tmp_path/'analysis.sqlite') as db:after=db.execute('select graph from analyses').fetchone()[0]
        assert before==after
    with TestClient(create_app(settings)) as client:
        assert client.get(base+'/hierarchy?parent_id=orders').json()['total']==4

def test_tool_audit_distinguishes_presence_from_integration(monkeypatch):
    original=tooling.python_package
    monkeypatch.setattr(tooling,'python_package',lambda name:'99.0' if name=='networkx' else original(name))
    values=tooling.inspect()['tools']
    assert values['networkx']['installed'] and values['networkx']['integration_status']=='installed_unused'
    monkeypatch.setattr(tooling,'package',lambda *args:None)
    assert tooling.inspect()['tools']['typescript']['integration_status']=='missing_required'

def test_many_packages_never_bypass_view_or_summary_limits(graph):
    graph['entities'] += [dict(id=f'package-{i}',kind='application',label=f'package-{i}',root=f'packages/{i}',evidence_ids=['ev']) for i in range(70)]
    index=Index(graph)
    view=index.system(limit=5)
    assert len(view['nodes'])<=5 and view['metadata']['truncated']
    assert view['metadata']['omitted_packages']>0
    assert index.hierarchy(limit=5)['total']>70
    summary=index.summary()
    assert summary['package_count']==71 and len(summary['packages'])==20 and summary['packages_truncated']
    expanded=index.system(limit=80)
    assert len(expanded['nodes'])<=80
    assert sum(n['kind']=='application' for n in expanded['nodes'])==71

def test_selected_module_system_view_stays_at_component_level(graph):
    view=Index(graph).system('orders')
    assert {'orders','store'}<={n['id'] for n in view['nodes']}
    assert not any(n['kind'] in ('symbol','file','endpoint') for n in view['nodes'])
    assert any(e['kind']=='MODULE_REFERENCE' and e['source']=='orders' and e['target']=='store' for e in view['edges'])
