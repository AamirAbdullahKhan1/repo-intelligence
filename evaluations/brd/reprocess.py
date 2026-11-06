"""Revalidate a saved 2.1 interpretation without model calls or source changes."""
import hashlib
import json
import re
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from intelligence import VERSION, combine, validate, diagrams, markdown
from architecture import audit


def reprocess(root, parent_id):
    if not isinstance(parent_id, str) or not re.fullmatch(r'[0-9a-f]{32}', parent_id):
        raise ValueError('Provide a valid saved analysis ID.')
    root = Path(root)
    parent = root / 'results' / parent_id
    try:
        prior = json.loads((parent / 'result.json').read_text(encoding='utf-8'))
        source = json.loads((parent / 'source-ledger.json').read_text(encoding='utf-8'))
        inventory = json.loads((parent / 'inventory-proposal.txt').read_text(encoding='utf-8'))
    except (OSError, ValueError):
        raise ValueError('The completed source snapshot and original inventory are required.') from None
    if (prior.get('status') != 'completed' or inventory.get('schema_version') != VERSION or
            source.get('input_sha256') != prior.get('input_sha256')):
        raise ValueError('Only a completed current-contract interpretation with a matching source snapshot can be revalidated. Older contracts need a new analysis.')
    path = parent / 'relationships-proposal.txt'
    paths = json.loads(path.read_text(encoding='utf-8')) if path.exists() else {
        'schema_version': VERSION, 'entities': [], 'relationships': [], 'workflows': [], 'findings': [], 'dispositions': []}
    started = time.monotonic()
    model = validate(combine(inventory, paths), source)
    views = diagrams(model)
    report = markdown(model, source, prior['skill'], views)
    identity = uuid.uuid4().hex
    result = {**prior, 'id': identity, 'created_at': datetime.now(timezone.utc).isoformat(),
        'filename': prior['filename'].replace(' [revalidated]', '') + ' [revalidated]',
        'reprocess_of': parent_id, 'reprocess_kind': 'local_validation_and_compilation_only',
        'original_analysis_seconds': prior.get('original_analysis_seconds', prior['duration_seconds']),
        'original_analysis_usage': prior.get('original_analysis_usage', prior['usage']),
        'original_compiler_sha256': prior.get('original_compiler_sha256', prior.get('compiler_sha256')),
        'original_stage_reported_models': prior.get('original_stage_reported_models', prior.get('stage_reported_models', [])),
        'runner_version': VERSION, 'duration_seconds': round(time.monotonic() - started, 3),
        'usage': {'prompt_tokens': 0, 'completion_tokens': 0, 'total_tokens': 0},
        'stage_usage': [], 'stage_reported_models': [], 'planned_stages_executed': 0,
        'compiler_sha256': hashlib.sha256(b''.join((Path(__file__).parent / name).read_bytes() for name in ('intelligence.py', 'architecture.py'))).hexdigest(),
        'intelligence_model': model, 'views': views, 'report': report, 'audit_available': True,
        'validation': {'scope': 'Local revalidation of the same saved model proposals. No new model reasoning; semantic correctness is unverified.',
            'diagrams': [v['source'] for v in views], 'diagram_count': len(views),
            'citation_count': len(re.findall(r'\[L\d+-L\d+\]', report)), 'invalid_line_ranges': [], 'partial': False,
            'quality_issue_count': len(model['quality_issues']),
            'warnings': [f"{len(model['quality_issues'])} architecture/process review findings remain; inspect the report."] if model['quality_issues'] else []}}
    folder = root / 'results' / identity
    folder.mkdir(parents=True)
    files = {'result.json': json.dumps(result, indent=2), 'source-ledger.json': json.dumps(source, indent=2),
             'inventory-proposal.txt': json.dumps(inventory), 'relationships-proposal.txt': json.dumps(paths),
             'intelligence-model.json': json.dumps(model, indent=2), 'report.md': report,
             'audit-report.md': audit(model, source, views)}
    for name, content in files.items():
        (folder / name).write_text(content, encoding='utf-8')
    if (parent / 'skill-used.md').exists():
        (folder / 'skill-used.md').write_bytes((parent / 'skill-used.md').read_bytes())
    for index, view in enumerate(views, 1):
        (folder / f'diagram-{index}.mmd').write_text(view['source'], encoding='utf-8')
    return result


if __name__ == '__main__':
    import sys
    if len(sys.argv) != 2:
        raise SystemExit('Usage: python evaluations/brd/reprocess.py <saved-analysis-id>')
    result = reprocess(Path(__file__).parent, sys.argv[1])
    print(json.dumps({'id': result['id'], 'reprocess_of': result['reprocess_of'], 'model_calls': 0, 'duration_seconds': result['duration_seconds']}))
