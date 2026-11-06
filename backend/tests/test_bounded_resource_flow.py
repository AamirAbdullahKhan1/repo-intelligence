import json
from app.analysis.pipeline import analyze


def write(root,name,text):
    p=root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')


def test_async_cached_s3_client_and_symbolic_bucket(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'config.ts', '''export function config(name){const value=process.env[name]?.trim();if(!value)throw Error('missing');return value;}''')
    write(tmp_path,'storage.ts','''import {config} from './config';
let sdkPromise=null;let client=null;
async function factory(){sdkPromise ??= import('@aws-sdk/client-s3');const sdk=await sdkPromise;client ??=new sdk.S3Client({});return {client,sdk};}
export async function save(bucket){const {client:store,sdk}=await factory();return store.send(new sdk.PutObjectCommand({Bucket:bucket,Key:'x'}));}
export async function run(){return save(config('BUCKET_NAME'));}
''')
    g=analyze(tmp_path)
    uses=[e for e in g['edges'] if e['kind']=='USES_RESOURCE']
    assert len(uses)==1
    target=next(n for n in g['entities'] if n['id']==uses[0]['target'])
    assert target['configuration']=={'kind':'environment','name':'BUCKET_NAME'}
    assert uses[0]['operation']=='write' and uses[0]['flow_step_ids']
    assert not g['flow_analysis']['partial']
    assert analyze(tmp_path)==g


def test_s3_same_named_local_client_is_not_sdk(tmp_path):
    write(tmp_path,'package.json','{}')
    write(tmp_path,'main.ts','''class S3Client{send(x){}}class PutObjectCommand{}
const client=new S3Client();client.send(new PutObjectCommand({Bucket:'wrong'}));''')
    g=analyze(tmp_path)
    assert not [e for e in g['edges'] if e['kind']=='USES_RESOURCE']


def test_mutated_receiver_does_not_prove_resource(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
let client=new S3Client({});client=other;client.send(new PutObjectCommand({Bucket:'wrong'}));''')
    assert not [e for e in analyze(tmp_path)['edges'] if e['kind']=='USES_RESOURCE']


def test_factory_calls_keep_separate_bucket_arguments(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
function command(bucket){return new PutObjectCommand({Bucket:bucket});}
const client=new S3Client({});
export function one(){return client.send(command('one'));}
export function two(){return client.send(command('two'));}
''')
    g=analyze(tmp_path);nodes={n['id']:n for n in g['entities']}
    assert {(nodes[e['source']]['label'],nodes[e['target']]['configuration']['value']) for e in g['edges'] if e['kind']=='USES_RESOURCE'}=={('one','one'),('two','two')}


def test_alias_mutation_invalidates_original_client(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
const client=new S3Client({});const alias=client;alias.send=other;
client.send(new PutObjectCommand({Bucket:'wrong'}));''')
    assert not [e for e in analyze(tmp_path)['edges'] if e['kind']=='USES_RESOURCE']


def test_capability_resource_paths_and_corrupt_proof_rejected(tmp_path):
    from copy import deepcopy
    import pytest
    from app.evidence.validation import validate
    from app.graph.exploration import Index
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1","next":"15"}}')
    write(tmp_path,'src/app/api/files/route.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
const client=new S3Client({});
function save(){return client.send(new PutObjectCommand({Bucket:'files'}));}
export function POST(){return save();}''')
    g=analyze(tmp_path)
    capability=next(n for n in g['entities'] if n.get('projection_rule')=='capability-1')
    assert capability['entry_ids'] and capability['member_paths']
    edge=next(e for e in g['edges'] if e.get('derivation_version')=='capability-1' and e['kind']=='USES_RESOURCE')
    assert edge['supporting_paths'] and len(edge['supporting_paths'][0])==3
    assert Index(g).system()['metadata']['abstraction']=='entry-point capabilities'
    assert Index(g).flow_evidence(edge['id'])['total']>0
    first=Index(g).flow_evidence(edge['id'],0,2)
    second=Index(g).flow_evidence(edge['id'],2,2)
    assert not {s['id'] for s in first['items']} & {s['id'] for s in second['items']}
    broken=deepcopy(g)
    next(e for e in broken['edges'] if e['id']==edge['id'])['supporting_paths'][0].pop(1)
    with pytest.raises(ValueError,match='Disconnected capability'):validate(broken,tmp_path.resolve())
    broken=deepcopy(g)
    next(e for e in broken['edges'] if e.get('provider')=='trusted-ts-flow')['flow_step_ids'].append('missing')
    with pytest.raises(ValueError,match='Incomplete flow'):validate(broken,tmp_path.resolve())


def test_recursive_bucket_analysis_reports_partial_without_guessing(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
function bucket(){return bucket();}const client=new S3Client({});
export function run(){return client.send(new PutObjectCommand({Bucket:bucket()}));}''')
    g=analyze(tmp_path)
    assert g['flow_analysis']['partial'] and g['flow_analysis']['reasons']
    assert not [e for e in g['edges'] if e['kind']=='USES_RESOURCE']


def test_local_process_is_not_environment_configuration(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
const process={env:{BUCKET:'local-literal'}};const client=new S3Client({});
export function run(){return client.send(new PutObjectCommand({Bucket:process.env.BUCKET}));}''')
    g=analyze(tmp_path)
    resources=[n for n in g['entities'] if n['kind']=='storage']
    assert resources and all(n['configuration']['kind']=='literal' for n in resources)


def test_eval_prevents_initializer_based_resource_claims(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1"}}')
    write(tmp_path,'main.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
const client=new S3Client({});eval(dynamicSource);
client.send(new PutObjectCommand({Bucket:'wrong'}));''')
    assert not [e for e in analyze(tmp_path)['edges'] if e['kind']=='USES_RESOURCE']


def test_capabilities_do_not_inherit_other_callers_buckets(tmp_path):
    write(tmp_path,'package.json','{"dependencies":{"@aws-sdk/client-s3":"1","next":"15"}}')
    write(tmp_path,'storage.ts','''import {S3Client,PutObjectCommand} from '@aws-sdk/client-s3';
const client=new S3Client({});export function save(bucket){return client.send(new PutObjectCommand({Bucket:bucket}));}''')
    write(tmp_path,'src/app/api/first/route.ts',"import {save} from '../../../../storage';export function POST(){return save('first');}")
    write(tmp_path,'src/app/api/second/route.ts',"import {save} from '../../../../storage';export function POST(){return save('second');}")
    g=analyze(tmp_path);nodes={n['id']:n for n in g['entities']}
    links={(nodes[e['source']]['label'],nodes[e['target']]['configuration']['value']) for e in g['edges'] if e.get('derivation_version')=='capability-1' and e['kind']=='USES_RESOURCE'}
    assert links=={('Requests: /api/first','first'),('Requests: /api/second','second')}
