"""Deterministic, provenance-preserving role groups; never deployment inference."""
from collections import defaultdict
import hashlib


def interpret(graph):
    nodes = {n['id']: n for n in graph['entities']}
    facts = list(graph['edges'])
    fact_by_id = {e['id']: e for e in facts}
    roles = defaultdict(set)
    supports = defaultdict(set)

    def assign(identifier, role, edge=None):
        if nodes[identifier]['kind'] not in ('symbol', 'file', 'endpoint'):
            return
        roles[identifier].add(role)
        if edge:
            supports[identifier].add(edge['id'])

    for n in nodes.values():
        if n['kind'] == 'endpoint':
            assign(n['id'], 'API handling')
    for e in facts:
        if e['kind'] == 'HANDLED_BY':
            assign(e['target'], 'API handling', e)
        elif e['kind'] == 'USES_RESOURCE':
            tech = nodes[e['target']].get('technology', '')
            assign(e['source'], 'Database access' if tech == 'PostgreSQL' else
                   'Cache and messaging' if tech == 'Redis' else 'Object storage access', e)
        elif e['kind'] == 'SDK_API_CALL':
            label = nodes[e['target']]['label']
            role = ('AI integration' if label.startswith(('openai ', '@anthropic-ai/sdk ')) else
                    'Payment integration' if label.startswith('stripe ') else
                    'Email integration' if label.startswith('resend ') else 'Library integration')
            assign(e['source'], role, e)
        elif e['kind'] == 'CALLS_HTTP':
            assign(e['source'], 'Client-side requests' if e.get('target_scope') == 'internal' else 'Outbound HTTP', e)

    # A symbol can have multiple responsibilities. One explicit primary role is
    # used for diagram partitioning; all observed role claims remain on the node.
    priority = ['Database access', 'Object storage access', 'Cache and messaging',
                'AI integration', 'Payment integration', 'Email integration',
                'Client-side requests', 'API handling', 'Outbound HTTP', 'Library integration']
    groups = defaultdict(list)
    for n in nodes.values():
        if n['kind'] not in ('symbol', 'file', 'endpoint') or not n.get('application_id'):
            continue
        observed = roles[n['id']]
        if observed:
            role = min(observed, key=priority.index)
            n['responsibilities'] = sorted(observed)
            n['responsibility_support_edge_ids'] = sorted(supports[n['id']])
        else:
            role = 'Other analyzed source'
        groups[(n['application_id'], role)].append(n['id'])

    def stable(kind, value):
        return kind + ':' + hashlib.sha256(value.encode()).hexdigest()[:20]

    group_for = {}
    group_ids = []
    multiple_apps = len({application for application, _ in groups}) > 1
    for (application, role), members in sorted(groups.items()):
        gid = stable('responsibility', application + '|' + role)
        group_ids.append(gid)
        evidence = {i for m in members for i in nodes[m].get('evidence_ids', [])}
        support_edges = sorted({i for m in members for i in supports[m]})
        for identifier in support_edges:
            evidence.update(fact_by_id[identifier]['evidence_ids'])
        graph['entities'].append(dict(id=gid, kind='component', label=role+' · '+nodes[application]['label'] if multiple_apps else role, application_id=application,
            group=role, projection_rule='responsibility-v1', members=sorted(members),
            evidence_ids=sorted(evidence), support_edge_ids=support_edges, resolution='conditional',
            responsibility=role, boundary='Derived logical role group; not a deployable service',
            limitation='Broad technical responsibility, not an inferred business/domain component'))
        for member in members:
            group_for[member] = gid

    aggregates = {}
    allowed = {'CALLS', 'HANDLED_BY', 'CALLS_HTTP', 'SDK_API_CALL', 'USES_RESOURCE'}
    for e in facts:
        if e['kind'] not in allowed:
            continue
        a = group_for.get(e['source'])
        target = nodes[e['target']]
        b = group_for.get(e['target']) or (e['target'] if target['kind'] in ('storage', 'sdk', 'external_service') else None)
        if not a or not b or a == b:
            continue
        kind = {'CALLS': 'MODULE_REFERENCE', 'HANDLED_BY': 'HANDLER_REFERENCE',
                'CALLS_HTTP': 'HTTP_INTEGRATION', 'SDK_API_CALL': 'USES_SDK', 'USES_RESOURCE': 'RESOURCE_USAGE'}[e['kind']]
        key = (a, b, kind, e.get('resolution', 'resolved'), e.get('profile', 'source'))
        v = aggregates.setdefault(key, dict(id=stable('architecture-edge', '|'.join(key)), source=a, target=b,
            kind=kind, resolution=e.get('resolution') if e.get('resolution') in ('ambiguous','unresolved') else 'conditional', source_resolution=e.get('resolution', 'resolved'),
            profile=e.get('profile', 'source'), evidence_ids=[], support_edge_ids=[], count=0,
            derivation='responsibility-v1: aggregate source relationships through explicit member identities; static only'))
        v['evidence_ids'].extend(e['evidence_ids'])
        v['support_edge_ids'].append(e['id'])
        v['count'] += 1
    derived = sorted(aggregates.values(), key=lambda e: e['id'])
    for e in derived:
        e['evidence_ids'] = sorted(set(e['evidence_ids']))
    graph['edges'].extend(derived)
    graph['entities'].sort(key=lambda n: n['id'])
    graph['edges'].sort(key=lambda e: e['id'])
    graph['architecture'] = dict(version='responsibility-v1', component_ids=group_ids,
        edge_ids=[e['id'] for e in derived], limitation='Technical responsibility groups; domain meaning and runtime deployment not established')
