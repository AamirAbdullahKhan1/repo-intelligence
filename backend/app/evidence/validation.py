import hashlib
import re
from pathlib import Path

def validate(graph: dict, root: Path) -> None:
    entities = {x['id']: x for x in graph['entities']}
    evidence = {x['id']: x for x in graph['evidence']}
    if len(entities) != len(graph['entities']): raise ValueError('Duplicate entities')
    if len(evidence) != len(graph['evidence']): raise ValueError('Duplicate evidence')
    if len({e['id'] for e in graph['edges']}) != len(graph['edges']):
        raise ValueError('Duplicate edges')
    cache = {}
    for ev in evidence.values():
        path = (root / ev['file']).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError(f"Invalid citation: {ev['file']}")
        if path not in cache:
            text = path.read_bytes().decode('utf-8')
            cache[path] = (text, text.encode('utf-16-le'), hashlib.sha256(text.encode()).hexdigest())
        text, units, digest = cache[path]
        if digest != ev['sha256'] or not 0 <= ev['start'] <= ev['end'] <= len(units)//2:
            raise ValueError(f"Invalid source identity/range: {ev['file']}")
        for position, line_key, column_key in ((ev['start'],'line','column'),(ev['end'],'end_line','end_column')):
            if line_key not in ev: continue
            prefix = units[:position*2].decode('utf-16-le')
            breaks=list(re.finditer(r'\r\n|[\r\n\u2028\u2029]',prefix))
            tail=prefix[breaks[-1].end():] if breaks else prefix
            if ev[line_key]!=len(breaks)+1 or ev[column_key]!=len(tail.encode('utf-16-le'))//2+1:
                raise ValueError(f"Invalid source line/column: {ev['file']}")
    for node in entities.values():
        if any(i not in evidence for i in node.get('evidence_ids', [])):
            raise ValueError('Dangling node evidence')
    for edge in graph['edges']:
        if edge['source'] not in entities or edge['target'] not in entities:
            raise ValueError('Dangling graph endpoint')
        if not edge['evidence_ids'] or any(i not in evidence for i in edge['evidence_ids']):
            raise ValueError('Missing graph support')
        if edge['kind'] == 'CALLS' and not entities[edge['target']].get('has_body'):
            raise ValueError('A signature is not an implementation')
    # Semantic support is supplied by the narrow worker rules, not proven by line validity alone.

