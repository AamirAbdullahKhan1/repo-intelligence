"""Static-only callback comparison on the pinned GitDiagram archive."""
import json
from pathlib import Path
import sys
import time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.analysis.pipeline import analyze
from app.ingestion.archive import extract_archive
from app.persistence.store import Store
from app.graph.exploration import Index

out=ROOT/'output/callback-values-review'
out.mkdir(parents=True,exist_ok=True)
source=out/'source'
if source.exists() and not any(source.iterdir()):
    source.rmdir()
if not source.exists():
    extracted=extract_archive(ROOT/'tmp/gitdiagram-verification.zip',source)
else:
    children=list(source.iterdir())
    extracted=children[0] if len(children)==1 and children[0].is_dir() else source
start=time.monotonic()
g=analyze(extracted)
(out/'gitdiagram-analysis.json').write_text(json.dumps(g),encoding='utf-8')
store=Store(out/'analysis.sqlite')
summary=store.save(g,{'kind':'pinned-static-callback-verification'})
(out/'gitdiagram-summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
route=next(n for n in g['entities'] if n.get('file')=='src/app/api/generate/stream/route.ts' and n['kind']=='endpoint')
allowed={'HANDLED_BY','CALLS','CONSTRUCTS','CALLS_HTTP','SDK_API_CALL','USES_RESOURCE','MAY_INVOKE_CALLBACK'}
active={route['id']}
for _ in range(12):
    active|={e['target'] for e in g['edges'] if e['source'] in active and e['kind'] in allowed}
names=['admitGenerationRequest','getGithubData','prepareRepositoryContext','fetchSourceContext','estimateGenerationCost','admitComplimentaryQuota','streamCompletion','generateValidatedGraph','compileDiagramGraph','finalizeGenerationStream','createGenerationSseWriter','createGenerationSessionAudit']
checks={name:any(n['label']==name and n['id'] in active for n in g['entities']) for name in names}
view=Index(g).workflow(entry=route['id'],depth=6,limit=80)
(out/'workflow.json').write_text(json.dumps(view,indent=2),encoding='utf-8')
result={'snapshot_id':g['snapshot_id'],'seconds':round(time.monotonic()-start,3),'coverage':g['coverage'],
        'callback_edges':len([e for e in g['edges'] if e['kind']=='MAY_INVOKE_CALLBACK']),
        'sdk_edges':len([e for e in g['edges'] if e['kind']=='SDK_API_CALL' and e.get('derivation_version')!='capability-1']),
        'resource_edges':len([e for e in g['edges'] if e['kind']=='USES_RESOURCE' and e.get('derivation_version')!='capability-1']),
        'capability_groups':len(g.get('capability_architecture',{}).get('component_ids',[])),
        'capability_resource_edges':len([e for e in g['edges'] if e['kind']=='USES_RESOURCE' and e.get('derivation_version')=='capability-1']),
        'generation_reachable':checks,'workflow_nodes':len(view['nodes']),'workflow_truncated':view['metadata']['truncated']}
(out/'verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='coverage'},indent=2))
assert all(checks.values()), 'A required generation-stage static path is missing'
