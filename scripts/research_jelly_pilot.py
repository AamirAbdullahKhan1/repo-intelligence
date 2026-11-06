"""Isolated static-only Jelly experiment on the public, pinned GitDiagram snapshot.
Not a production integration. No customer install, build, dynamic or approx mode.
"""
import json
from pathlib import Path
import subprocess
import time

root=Path(__file__).resolve().parents[1]
out=root/'output/research/tsjs-core-reset'
source=root/'output/callback-values-review/source/gitdiagram'
graph=json.loads((root/'output/callback-values-review/gitdiagram-analysis.json').read_text())
files=sorted({n['file'] for n in graph['entities'] if n['kind']=='file' and n.get('file','').endswith(('.js','.jsx','.ts','.tsx','.mts','.cts','.mjs','.cjs'))})
tool=out/'jelly-pilot/node_modules/@cs-au-dk/jelly/lib/main.js'
args=['node','--max-old-space-size=1536',str(tool),'-b',str(source),
      '--timeout','60','--max-indirections','2','--ignore-dependencies',
      '--no-callgraph-external','--no-patch-escaping','--no-print-progress',
      '--diagnostics-json',str(out/'jelly-diagnostics.json'),
      '-j',str(out/'jelly-callgraph.json'),'--',*files]
start=time.monotonic()
result={'tool':'@cs-au-dk/jelly@0.13.0','source_snapshot':graph['source_snapshot_id'],
        'input_files':len(files),'flags':args[3:args.index('--')],
        'customer_code_executed':False,'customer_dependencies_installed':False}
try:
    process=subprocess.run(args,cwd=source,capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=90)
    (out/'jelly-stdout.txt').write_text(process.stdout,encoding='utf-8')
    (out/'jelly-stderr.txt').write_text(process.stderr,encoding='utf-8')
    result['exit_code']=process.returncode
except subprocess.TimeoutExpired:
    result['outer_timeout']=True
result['seconds']=round(time.monotonic()-start,3)
if (out/'jelly-callgraph.json').exists():
    g=json.loads((out/'jelly-callgraph.json').read_text())
    result['output_counts']={k:len(v) for k,v in g.items() if isinstance(v,(dict,list))}
(out/'jelly-run.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
