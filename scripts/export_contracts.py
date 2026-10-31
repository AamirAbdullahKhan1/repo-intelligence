"""Generate reviewable API/worker JSON schemas from backend-owned models."""
from pathlib import Path
import json
import sys
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from app.contracts import Analysis, Edge, Entity, Evidence, EvidenceResponse, Graph, Job, View
from app.main import app
from app.api.presentation_models import EntityPage, RepositoryOverview, ToolReport

def export(check=False):
    destination=ROOT/'shared/schemas'
    destination.mkdir(parents=True,exist_ok=True)
    values={model.__name__+'.schema.json':model.model_json_schema() for model in (Analysis,Edge,Entity,Evidence,EvidenceResponse,Graph,Job,View,EntityPage,RepositoryOverview,ToolReport)}
    values['openapi.json']=app.openapi()
    for name,value in values.items():
        text=json.dumps(value,indent=2,sort_keys=True)+'\n'
        path=destination/name
        if check:
            if not path.exists() or path.read_text(encoding='utf-8')!=text:
                raise ValueError('Stale contract: '+name)
        else:
            path.write_text(text,encoding='utf-8')

if __name__=='__main__':
    export('--check' in sys.argv)
