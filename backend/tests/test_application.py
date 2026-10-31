import io
import json
import subprocess
import time
import zipfile
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from app.config import Settings
from app.main import create_app
from app.analysis.pipeline import analyze, WORKER

SOURCES = {
    'package.json':'{"name":"known-system","dependencies":{"next":"test","pg":"test"},"scripts":{"postinstall":"NEVER EXECUTE"}}',
    'src/app/api/users/route.ts':'import {load} from "../../../store"; export function GET(){return load()}',
    'src/store.ts':'import {Pool} from "pg"; const pool=new Pool(); export function load(){return pool.query("select 1")}',
    'src/network.ts':'export function client(){return fetch("/api/users")}',
    'compose.yaml':'services:\n  app:\n    depends_on: [database]\n  database:\n    image: postgres\n',
    'evil.config.js':'require("fs").writeFileSync("SHOULD_NOT_EXIST","bad"); throw Error("executed")',
}
def zip_bytes():
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        for name,text in SOURCES.items():z.writestr('repo/'+name,text)
    return stream.getvalue()

def wait(client,job):
    for _ in range(200):
        value=client.get('/api/v1/jobs/'+job['id']).json()
        if value['status'] not in ('queued','running'):return value
        time.sleep(.05)
    pytest.fail('Job did not complete')

def test_both_inputs_persistence_views_evidence(tmp_path,monkeypatch):
    import app.jobs as jobs
    def retrieve(url,output,cancelled):
        output.write_bytes(zip_bytes())
        return {'kind':'github','commit':'a'*40,'url':url}
    monkeypatch.setattr(jobs,'retrieve',retrieve)
    settings=Settings(data_dir=tmp_path/'data',_env_file=None)
    with TestClient(create_app(settings)) as client:
        assert client.get('/api/v1/health').json()['engine']=='static-typescript'
        upload=client.post('/api/v1/analyze/upload',files={'file':('test.zip',zip_bytes(),'application/zip')})
        assert upload.status_code==202
        first=wait(client,upload.json());assert first['status']=='complete',first
        second=wait(client,client.post('/api/v1/analyze/github',json={'url':'https://github.com/owner/repo'}).json())
        assert second['status']=='complete',second
        assert first['snapshot_id']==second['snapshot_id']
        snapshot=first['snapshot_id'];base='/api/v1/analyses/'+snapshot
        system=client.get(base+'/view?layer=all').json();workflow=client.get(base+'/view?kind=workflow&depth=3').json()
        assert system['snapshot_id']==workflow['snapshot_id']==snapshot
        assert any(e['kind']=='HANDLED_BY' for e in workflow['edges'])
        assert any(e['kind']=='CALLS' for e in workflow['edges'])
        assert any(e['kind']=='SDK_API_CALL' for e in workflow['edges'])
        assert any(e['kind']=='STARTS_AFTER' for e in system['edges'])
        assert client.get(base+'/view?depth=99').status_code==422
        assert client.get(base+'/view?kind=workflow&entry_id=absent').status_code==422
        evidence=client.get(base+'/evidence',params={'record_id':workflow['edges'][0]['id']}).json()
        assert evidence['evidence'][0]['line']>=1
        assert client.get(base+'/unknowns').json()['total']>0
        assert len(client.get('/api/v1/analyses').json())==1
        assert not (WORKER.parent/'SHOULD_NOT_EXIST').exists()
        assert not list((tmp_path/'data').glob('snapshot-*'))
    with TestClient(create_app(settings)) as reopened:
        assert reopened.get(base).status_code==200
        assert reopened.get(base+'/view?layer=all').json()==system

def test_invalid_zip_fails_without_snapshot(tmp_path):
    with TestClient(create_app(Settings(data_dir=tmp_path,_env_file=None))) as client:
        response=client.post('/api/v1/analyze/upload',files={'file':('bad.zip',b'not a zip')})
        assert wait(client,response.json())['status']=='failed'
        assert client.get('/api/v1/analyses').json()==[]
        assert client.post('/api/v1/analyze/github',json={'url':'https://evil.test/a/b'}).status_code==422

def test_worker_network_guard():
    result=subprocess.run(['node','-e',"require('./guard.cjs');require('node:https')"],cwd=WORKER.parent,capture_output=True)
    assert result.returncode!=0
    assert b'prohibited' in result.stderr

def test_cancel_and_timeout(tmp_path):
    for name,text in SOURCES.items():
        p=tmp_path/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)
    with pytest.raises(InterruptedError):analyze(tmp_path,cancelled=lambda:True)
    with pytest.raises(ValueError,match='time limit'):analyze(tmp_path,timeout=0)

def test_config_no_provider_settings():
    assert not any('openai' in key or 'llm' in key for key in Settings.model_fields)
    import importlib.util
    assert importlib.util.find_spec('openai') is None

def test_invalid_manifest_values_do_not_leak_in_errors(tmp_path):
    stream=io.BytesIO()
    with zipfile.ZipFile(stream,'w') as z:
        z.writestr('package.json','{"name":{"secret":"must-not-appear-in-error"}}')
        z.writestr('main.ts','export function run(){return 1}')
    with TestClient(create_app(Settings(data_dir=tmp_path,_env_file=None))) as client:
        response=client.post('/api/v1/analyze/upload',files={'file':('bad.zip',stream.getvalue())})
        result=wait(client,response.json())
        assert result['status']=='failed'
        assert result['error']=='Static worker output failed the graph contract; no result published'
        assert 'must-not-appear' not in json.dumps(result)

def test_api_queue_capacity_and_cancellation(tmp_path,monkeypatch):
    import app.jobs as jobs
    seen_roots=[]
    def held_analysis(root,cancelled):
        seen_roots.append(root)
        while not cancelled():time.sleep(.01)
        raise InterruptedError('Cancelled')
    monkeypatch.setattr(jobs,'analyze',held_analysis)
    with TestClient(create_app(Settings(data_dir=tmp_path,_env_file=None))) as client:
        queued=[client.post('/api/v1/analyze/upload',files={'file':('fixture.zip',zip_bytes())}) for _ in range(4)]
        assert all(response.status_code==202 for response in queued)
        assert client.post('/api/v1/analyze/github',json={'url':'https://github.com/owner/repo'}).status_code==429
        identifier=queued[0].json()['id']
        assert client.post('/api/v1/jobs/'+identifier+'/cancel').status_code==200
        assert wait(client,queued[0].json())['status']=='cancelled'
    assert not list(tmp_path.glob('snapshot-*'))
    assert not list(tmp_path.glob('*.zip'))
    assert seen_roots
    assert all(not root.exists() and not root.is_relative_to(tmp_path) for root in seen_roots)
