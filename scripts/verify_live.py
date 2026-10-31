"""Exercise the running local API. Optional public GitHub retrieval; no target execution."""
import argparse
import json
from pathlib import Path
import time
import zipfile
import httpx

ROOT=Path(__file__).resolve().parents[1]

def wait(client, job):
    start=time.monotonic()
    while time.monotonic()-start<240:
        result=client.get('/api/v1/jobs/'+job['id']).raise_for_status().json()
        if result['status'] not in ('queued','running'):
            if result['status']!='complete':raise ValueError(result)
            return result
        time.sleep(.5)
    raise TimeoutError('Live analysis timed out')

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--source',type=Path)
    parser.add_argument('--github')
    parser.add_argument('--api',default='http://127.0.0.1:8000')
    args=parser.parse_args()
    output=ROOT/'output/integration'
    output.mkdir(parents=True,exist_ok=True)
    results={}
    with httpx.Client(base_url=args.api,timeout=60,trust_env=False) as client:
        results['health']=client.get('/api/v1/health').raise_for_status().json()
        if args.source:
            archive=ROOT/'tmp/gitdiagram-verification.zip'
            archive.parent.mkdir(exist_ok=True)
            with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED) as z:
                for p in sorted(args.source.rglob('*')):
                    if p.is_file() and not any(v in p.relative_to(args.source).parts for v in ('.git','node_modules','.next','.open-next')):
                        z.write(p,'gitdiagram/'+p.relative_to(args.source).as_posix())
            with archive.open('rb') as stream:
                job=client.post('/api/v1/analyze/upload',files={'file':('gitdiagram.zip',stream,'application/zip')}).raise_for_status().json()
            results['zip']=wait(client,job)
        if args.github:
            job=client.post('/api/v1/analyze/github',json={'url':args.github}).raise_for_status().json()
            results['github']=wait(client,job)
        for method in ('zip','github'):
            if method not in results:continue
            sid=results[method]['snapshot_id']
            summary=client.get('/api/v1/analyses/'+sid).raise_for_status().json()
            (output/(method+'-summary.json')).write_text(json.dumps(summary,indent=2),encoding='utf-8')
            for kind in ('system','workflow'):
                view=client.get('/api/v1/analyses/'+sid+'/view',params={'kind':kind}).raise_for_status().json()
                (output/(method+'-'+kind+'.json')).write_text(json.dumps(view,indent=2),encoding='utf-8')
            results[method]['repository']=summary['repository']
        results['history_count']=len(client.get('/api/v1/analyses').raise_for_status().json())
    (output/'live-verification.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
    print(json.dumps(results,indent=2))
