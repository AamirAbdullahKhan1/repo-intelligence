"""Bounded entry-point slices over canonical facts; source packages are not services."""
from collections import defaultdict, deque
import hashlib


def reconstruct(graph):
    nodes = {n['id']: n for n in graph['entities']}
    facts = [e for e in graph['edges'] if e.get('derivation_version') != 'capability-1']
    edges = {e['id']: e for e in facts}
    outgoing = defaultdict(list)
    incoming = defaultdict(list)
    for e in facts:
        outgoing[e['source']].append(e)
        incoming[e['target']].append(e)
    groups = defaultdict(list)
    for n in nodes.values():
        if n['kind'] != 'endpoint':
            continue
        # Label the public interface, without inventing a business-domain name.
        path = n.get('path') or n['label'].split(' ', 1)[-1]
        parts = path.strip('/').split('/')
        prefix = '/' + '/'.join(parts[:2] if parts[0] == 'api' else parts[:1])
        groups[(n.get('application_id'), prefix)].append(n['id'])
    if not groups:
        return
    stable = lambda kind, key: kind + ':' + hashlib.sha256(key.encode()).hexdigest()[:20]
    traversable = {'HANDLED_BY', 'CALLS', 'CONSTRUCTS', 'MAY_INVOKE_CALLBACK'}
    integrations = {'USES_RESOURCE', 'SDK_API_CALL', 'CALLS_HTTP'}
    component_ids, relation_ids = [], []
    for (application, prefix), entries in sorted(groups.items()):
        cid = stable('capability', str(application) + '|' + prefix)
        paths, pending, truncated = {}, deque((i, []) for i in sorted(entries)), False
        while pending:
            current, path = pending.popleft()
            if current in paths:
                continue
            if len(paths) >= 400:
                truncated = True
                break
            paths[current] = path
            if len(path) >= 10:
                truncated |= any(e['kind'] in traversable for e in outgoing[current])
                continue
            for e in sorted(outgoing[current], key=lambda x: x['id']):
                if e['kind'] in traversable and nodes[e['target']].get('application_id') == application:
                    pending.append((e['target'], path + [e['id']]))
        support = sorted({i for path in paths.values() for i in path})
        citations = sorted({i for member in paths for i in nodes[member].get('evidence_ids', [])})
        graph['entities'].append(dict(id=cid, kind='component', label='Requests: ' + prefix,
            application_id=application, projection_rule='capability-1', members=sorted(paths),
            entry_ids=sorted(entries), member_paths=paths, support_edge_ids=support,
            evidence_ids=citations, resolution='conditional', slice_truncated=truncated,
            boundary='Entry-point capability slice; shared helpers can belong to multiple slices',
            limitation='Route-derived technical capability; bounded possible reachability, not a deployed service or guaranteed execution order'))
        component_ids.append(cid)
        by_target = defaultdict(list)
        for member, path in sorted(paths.items()):
            for e in outgoing[member]:
                if e['kind'] in integrations and nodes[e['target']]['kind'] in ('storage', 'sdk', 'external_service', 'endpoint'):
                    if e.get('context_callsite'):
                        # Reuse only the resource context actually invoked by this slice.
                        for call in incoming[member]:
                            if call.get('callsite') == e['context_callsite'] and call['source'] in paths:
                                by_target[(e['target'],e['kind'])].append(paths[call['source']] + [call['id'],e['id']])
                    else:
                        by_target[(e['target'], e['kind'])].append(path + [e['id']])
        for (target, kind), derivations in sorted(by_target.items()):
            key = cid + '|' + target + '|' + kind
            rid = stable('capability-edge', key)
            supporting = sorted({i for path in derivations for i in path})
            graph['edges'].append(dict(id=rid, source=cid, target=target, kind=kind,
                resolution='ambiguous' if any(edges[i].get('resolution') == 'ambiguous' for i in supporting) else 'conditional',
                evidence_ids=sorted({i for eid in supporting for i in edges[eid]['evidence_ids']}),
                support_edge_ids=supporting, supporting_paths=derivations, derivation_version='capability-1',
                derivation='Entry-point paths through supported direct/callback relationships to a canonical operation',
                limitation='Paths are possible static relationships, not sequential execution; inspect the operation for destination and flow evidence'))
            relation_ids.append(rid)
    graph['capability_architecture'] = dict(version='capability-1', component_ids=component_ids, edge_ids=relation_ids,
        limitation='Route-anchored technical slices; shared membership and truncated traversal are explicit')
    graph['entities'].sort(key=lambda n: n['id'])
    graph['edges'].sort(key=lambda e: e['id'])
