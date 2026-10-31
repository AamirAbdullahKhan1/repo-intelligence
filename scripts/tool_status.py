"""Inspect the invoking interpreter using the same inventory function as the API."""
from pathlib import Path
import json
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from app.tooling import inspect
if __name__=='__main__':
    print(json.dumps(inspect(),indent=2))
