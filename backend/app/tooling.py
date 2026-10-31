"""Runtime-local tool inventory. Package presence and active integration are distinct."""
import importlib.metadata
import json
from pathlib import Path
import shutil
import sqlite3
import sys
import yaml
ROOT=Path(__file__).resolve().parents[2]
def package(directory, name):
    path=directory/'node_modules'/name/'package.json'
    return json.loads(path.read_text(encoding='utf-8'))['version'] if path.exists() else None

def python_package(name):
    try:return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:return None

def _tools():
    return {
        'typescript':{'version':package(ROOT/'backend/workers/typescript','typescript'),'used_by':'backend/workers/typescript/index.cjs','status':'primary engine'},
        'reactflow':{'version':package(ROOT/'frontend','reactflow'),'used_by':'frontend/src/components/diagrams/ArchitectureCanvas.tsx','status':'interactive rendering'},
        'elkjs':{'version':package(ROOT/'frontend','elkjs'),'used_by':'frontend/src/components/diagrams/ArchitectureCanvas.tsx','status':'hierarchical layout in browser Web Worker'},
        'sqlite':{'version':sqlite3.sqlite_version,'used_by':'backend/app/persistence/store.py','status':'job and canonical graph persistence'},
        'pyyaml':{'version':python_package('PyYAML'),'used_by':'backend/app/analysis/configuration.py','status':'narrow Compose declarations'},
        'syft':{'path':shutil.which('syft'),'status':'deferred; package manifest inventory does not equal SBOM'},
        'networkx':{'version':python_package('networkx'),'status':'deferred; bounded traversal and projections use standard Python'},
        'tree_sitter':{'version':python_package('tree-sitter'),'status':'deferred; no second parser required in current TS/JS scope'},
        'ast_grep':{'path':shutil.which('ast-grep') or shutil.which('sg'),'status':'deferred; presence is not integration'},
        'semgrep':{'path':shutil.which('semgrep'),'version':python_package('semgrep'),'status':'deferred; security rules are outside this relationship MVP'},
        'gitleaks':{'path':shutil.which('gitleaks'),'status':'deferred; limited metadata redaction is not a Gitleaks scan'},
        'openai':{'version':python_package('openai'),'status':'removed from this backend environment and runtime'},
        'react-flow-renderer':{'version':package(ROOT/'frontend','react-flow-renderer'),'status':'removed duplicate'},
    }


def inspect():
    values=_tools()
    active={'typescript','reactflow','elkjs','sqlite','pyyaml'}
    for name,tool in values.items():
        installed=bool(tool.get('version') or tool.get('path'))
        tool['installed']=installed
        tool['integration_status']='active' if name in active and installed else 'missing_required' if name in active else 'installed_unused' if installed else 'deferred'
        if name in ('openai','react-flow-renderer') and not installed:tool['integration_status']='removed'
        tool['required']=name in active
    values['pyyaml']['loaded_version']=yaml.__version__
    values['pyyaml']['module_path']=yaml.__file__
    values['pyyaml']['metadata_matches_loaded']=values['pyyaml']['version']==yaml.__version__
    return {'interpreter':sys.executable,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'tools':values,
            'meaning':'This interpreter only. Other Python installations do not change this backend runtime.',
            'syft_role':'Future SBOM inventory only; not source relationship resolution.'}
