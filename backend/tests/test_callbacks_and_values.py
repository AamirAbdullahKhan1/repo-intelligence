from app.analysis.pipeline import analyze


def write(root, name, text):
    p = root / name
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding='utf-8')


def test_stream_deferred_timer_event_callbacks_and_shadowing(tmp_path):
    write(tmp_path, 'package.json', '{"dependencies":{"next":"15"}}')
    write(tmp_path, 'main.ts', '''import {after as deferred} from 'next/server';
function processData(){}
export function entry(){
 new ReadableStream({start(controller){processData();}});
 new Promise(resolve=>processData());
 deferred(()=>processData());
 setTimeout(()=>processData(),1);
 const controller=new AbortController();
 controller.signal.addEventListener('abort',()=>processData());
 function unused(){processData();}
}
function shadowed(ReadableStream,setTimeout){
 new ReadableStream({start(){processData();}});setTimeout(()=>processData(),1);
}''')
    g=analyze(tmp_path)
    callbacks=[e for e in g['edges'] if e['kind']=='MAY_INVOKE_CALLBACK']
    assert {e['api'] for e in callbacks} == {'ReadableStream.start','Promise.executor','next.after','setTimeout','EventTarget.addEventListener'}
    assert len(callbacks)==5
    assert all(e['resolution']=='conditional' and len(e['evidence_ids'])>=2 for e in callbacks)
    nodes={n['id']:n for n in g['entities']}
    assert all(nodes[e['source']]['label']=='entry' for e in callbacks)
    from app.graph.exploration import Index
    entry=next(n['id'] for n in g['entities'] if n['label']=='entry')
    view=Index(g).workflow(entry=entry,depth=4,limit=80)
    assert any(n['label']=='processData' for n in view['nodes'])
    assert not any(n['label']=='unused' for n in view['nodes'])
    assert analyze(tmp_path)==g


def test_helper_objects_destructured_clients_and_config_literals(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"openai":"1"}}')
    write(tmp_path,'config.ts', '''export function config(){const host='https://api.example.com';return {host};}''')
    write(tmp_path,'main.ts', '''import OpenAI from 'openai';import {config} from './config';
function clients(){const client=new OpenAI();return {client};}
function url(value){return value;}
export function run(){const {client:ai}=clients();ai.responses.create({});fetch(url(config().host));}
function branches(flag){if(flag)return 'https://wrong.example';return 'https://other.example';}
export function unknown(flag){fetch(branches(flag));}
''')
    g=analyze(tmp_path)
    assert any(e['kind']=='SDK_API_CALL' for e in g['edges'])
    assert any(n['kind']=='external_service' and n['label']=='api.example.com' for n in g['entities'])
    assert not any(n['label'] in ('wrong.example','other.example') for n in g['entities'])
    assert any(u['kind']=='http' for u in g['unknowns'])


def test_mutated_return_object_is_not_a_confirmed_destination(tmp_path):
    write(tmp_path,'package.json','{}')
    write(tmp_path,'main.ts', '''const settings={host:'https://wrong.example'};
settings.host=runtimeValue;export function run(){fetch(settings.host);}''')
    g=analyze(tmp_path)
    assert not any(n['kind']=='external_service' for n in g['entities'])


def test_returned_resource_client_and_parameterized_configuration(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"pg":"1"}}')
    write(tmp_path,'main.ts', '''import {Pool} from 'pg';
function options(host){return {connectionString:host};}
function clients(){const db=new Pool(options('postgres://localhost/app'));return {db};}
export function run(){const {db}=clients();db.query('select 1');}
''')
    g=analyze(tmp_path)
    assert len([e for e in g['edges'] if e['kind']=='USES_RESOURCE'])==1


def test_local_callback_arguments_do_not_mix_callers_or_unused_properties(tmp_path):
    write(tmp_path,'package.json','{}')
    write(tmp_path,'main.ts','''function retry(params){if(flag)return params.run();return params.run();}
function first(){} function second(){} function unused(){}
export function a(){retry({run:first,unused});}
export function b(){retry({run:second});}
function ignores(params){} export function c(){ignores({run:unused});}
''')
    g=analyze(tmp_path)
    nodes={n['id']:n for n in g['entities']}
    links={(nodes[e['source']]['label'],nodes[e['target']]['label']) for e in g['edges'] if e['kind']=='MAY_INVOKE_CALLBACK'}
    assert links=={('a','first'),('b','second')}
