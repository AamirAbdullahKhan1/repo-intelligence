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
        if node.get('projection_rule') in ('responsibility-v1','capability-1'):
            if any(i not in entities for i in node.get('members', [])):
                raise ValueError('Dangling responsibility member')
    edge_ids = {e['id'] for e in graph['edges']}
    edge_by_id = {e['id']: e for e in graph['edges']}
    def validate_path(path, starts, target):
        if not path:
            if target not in starts:
                raise ValueError('Missing capability path')
            return
        if any(i not in edge_by_id for i in path):
            raise ValueError('Missing capability path relationship')
        steps = [edge_by_id[i] for i in path]
        if steps[0]['source'] not in starts or steps[-1]['target'] != target or any(a['target'] != b['source'] for a,b in zip(steps,steps[1:])):
            raise ValueError('Disconnected capability path')
    for node in entities.values():
        if node.get('projection_rule') == 'capability-1':
            if set(node.get('member_paths', {})) != set(node['members']):
                raise ValueError('Incomplete capability membership paths')
            for member, path in node['member_paths'].items():
                validate_path(path,set(node['entry_ids']),member)
    for claim in graph['edges']:
        if claim.get('derivation_version') == 'capability-1':
            starts = set(entities[claim['source']]['entry_ids'])
            for path in claim['supporting_paths']:
                validate_path(path,starts,claim['target'])
            if set(claim['support_edge_ids']) != {i for p in claim['supporting_paths'] for i in p}:
                raise ValueError('Lost capability relationship support')
    for record in [*entities.values(), *graph['edges']]:
        if any(i not in edge_ids for i in record.get('support_edge_ids', [])):
            raise ValueError('Dangling supporting relationship')
    for edge in graph['edges']:
        if edge['source'] not in entities or edge['target'] not in entities:
            raise ValueError('Dangling graph endpoint')
        if not edge['evidence_ids'] or any(i not in evidence for i in edge['evidence_ids']):
            raise ValueError('Missing graph support')
        if edge['kind'] == 'CALLS' and not entities[edge['target']].get('has_body'):
            raise ValueError('A signature is not an implementation')
    # Semantic support is supplied by the narrow worker rules, not proven by line validity alone.
    for reference in graph.get('library_references', []):
        if reference.get('source') not in entities or not reference.get('evidence_ids') or any(i not in evidence for i in reference['evidence_ids']):
            raise ValueError('Invalid standard-library reference support')
    flow = graph.get('flow_analysis')
    if flow:
        flow_nodes = {n['id']: n for n in flow['nodes']}
        flow_steps = {s['id']: s for s in flow['steps']}
        if len(flow_nodes) != len(flow['nodes']) or len(flow_steps) != len(flow['steps']):
            raise ValueError('Duplicate flow provenance identity')
        for record in [*flow_nodes.values(), *flow_steps.values()]:
            if not record.get('evidence_ids') or any(i not in evidence for i in record['evidence_ids']):
                raise ValueError('Missing flow provenance evidence')
        for step in flow_steps.values():
            if step['source'] not in flow_nodes or step['target'] not in flow_nodes:
                raise ValueError('Dangling flow step endpoint')
        for claim in graph['edges']:
            if claim.get('provider') != 'trusted-ts-flow':
                continue
            roots = claim.get('flow_root_ids', [])
            support = claim.get('flow_step_ids', [])
            if not roots or not support or any(i not in flow_nodes for i in roots) or any(i not in flow_steps for i in support):
                raise ValueError('Incomplete flow claim provenance')
            selected = {i: flow_steps[i] for i in support}
            active = set(roots)
            changed = True
            while changed:
                previous = len(active)
                active.update(s['source'] for s in selected.values() if s['target'] in active)
                changed = len(active) != previous
            if any(s['source'] not in active or s['target'] not in active for s in selected.values()):
                raise ValueError('Disconnected flow claim provenance')

