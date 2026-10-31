"""Trusted local CLI using exactly the API's static analysis engine."""
import argparse
import json
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.analysis.pipeline import analyze
from app.graph.projections import architecture_view
from app.persistence.store import Store

if __name__=='__main__':
    parser=argparse.ArgumentParser(description='Analyze a disposable source snapshot (files become read-only)')
    parser.add_argument('snapshot',type=Path)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    source=args.snapshot.resolve(strict=True)
    output=args.output.resolve()
    if output.is_relative_to(source):raise ValueError('Output must be outside the source snapshot')
    graph=analyze(source)
    output.mkdir(parents=True,exist_ok=True)
    store=Store(output/'analysis.sqlite')
    store.save(graph,{'kind':'local-disposable-snapshot'})
    for kind in ('system','workflow'):
        (output/(kind+'.json')).write_text(json.dumps(architecture_view(graph,kind),indent=2),encoding='utf-8')
    print(json.dumps({'snapshot_id':graph['snapshot_id'],'coverage':graph['coverage'],'output':str(output)},indent=2))
