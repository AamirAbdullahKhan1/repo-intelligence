import hashlib
from collections import defaultdict, deque


def responsibility_view(graph, scope=None, limit=24):
    model = graph['architecture']
    nodes = {n['id']: n for n in graph['entities']}
    groups = [nodes[i] for i in model['component_ids'] if not scope or nodes[i].get('application_id') == scope or i == scope]
    order = {role:i for i,role in enumerate(['Client-side requests','API handling','Database access','Object storage access','Cache and messaging','AI integration','Payment integration','Email integration','Outbound HTTP','Library integration','Other analyzed source'])}
    groups.sort(key=lambda n: (order.get(n.get('responsibility'),99), n['label'], n['id']))
    group_total = len(groups)
    # Preserve room for concrete destinations, never show every function.
    budget = min(12, max(1, limit - 4))
    groups = groups[:budget]
    active = {n['id'] for n in groups}
    edge_ids = set(model['edge_ids'])
    links = [e for e in graph['edges'] if e['id'] in edge_ids and e['source'] in active]
    destinations = sorted({e['target'] for e in links if e['target'] not in active and nodes[e['target']]['kind'] != 'component'},
                          key=lambda i: (nodes[i]['kind'] != 'storage', nodes[i]['label'], i))
    selected = groups + [nodes[i] for i in destinations[:max(0, limit-len(groups))]]
    visible = {n['id'] for n in selected}
    edges = [e for e in links if e['target'] in visible]
    total = len(edges)
    # Full membership/provenance stays in the saved canonical graph. The landing
    # response is bounded; selecting the canonical ID retrieves its evidence.
    def compact(record):
        value=dict(record)
        if 'members' in value:
            value['member_count']=len(value.pop('members'))
        for key in ('evidence_ids','support_edge_ids'):
            if key in value and len(value[key])>20:
                value[key+'_total']=len(value[key])
                value[key]=value[key][:20]
                value['details_truncated']=True
        return value
    return dict(snapshot_id=graph['snapshot_id'], kind='system', nodes=[compact(n) for n in selected], edges=[compact(e) for e in edges[:60]],
        metadata=dict(static_only=True, scope_id=scope, abstraction='technical responsibilities',
            truncated=len(groups)<group_total or len(destinations)>limit-len(groups) or total>60,
            omitted_groups=group_total-len(groups),
            note='Derived technical role groups, not deployable services. Select a group for original code and static workflow evidence.',
            warning=model['limitation']))

def project(graph: dict) -> dict:
    nodes = {e['id']: e for e in graph['entities']}

    def endpoint(eid, detail):
        node = nodes[eid]
        if node['kind'] in ('file', 'symbol', 'endpoint'):
            return node.get('component_id' if detail else 'application_id')
        return eid if node['kind'] in ('application','component','external_service','sdk') else None

    def view(detail):
        groups = {}
        kinds = {'CALLS','CALLS_HTTP','SDK_API_CALL','CONSTRUCTS_CLIENT'}
        if detail:
            kinds |= {'IMPORTS','REEXPORTS'}
        for edge in graph['edges']:
            if edge['kind'] not in kinds:
                continue
            a, b = endpoint(edge['source'],detail), endpoint(edge['target'],detail)
            if not a or not b or a == b:
                continue
            display_kind='SDK_USAGE' if edge['kind'] in ('SDK_API_CALL','CONSTRUCTS_CLIENT') else edge['kind']
            resolution = edge.get('resolution', 'resolved')
            key = (a,b,display_kind,resolution)
            group = groups.setdefault(key, {'id': 'projection:'+hashlib.sha256('|'.join(key).encode()).hexdigest()[:20],
                'source':a,'target':b,'kind':display_kind,'resolution':resolution,'support_edge_ids':[], 'evidence_ids':[],'count':0})
            group['support_edge_ids'].append(edge['id'])
            group['evidence_ids'] += edge['evidence_ids']
            group['count'] += 1
        values = sorted(groups.values(), key=lambda x:x['id'])
        for item in values:
            item['evidence_ids'] = sorted(set(item['evidence_ids']))
        active = {i for e in values for i in (e['source'],e['target'])}
        if detail:
            selected = [n for n in nodes.values() if n['id'] in active]
        else:
            selected = [n for n in nodes.values() if n['id'] in active or n['kind']=='application']
        return {'nodes': sorted(selected,key=lambda x:x['id']), 'edges': values}

    deploy_kinds={'BINDS_RESOURCE','BINDS_SERVICE','DECLARES_CONTAINER','CONFIGURES_LOG_SINK','STARTS_AFTER'}
    deploy_edges=[e for e in graph['edges'] if e['kind'] in deploy_kinds]
    active={i for e in deploy_edges for i in (e['source'],e['target'])} | {e['id'] for e in nodes.values() if e['kind']=='deployable'}
    return {'overview':view(False),'components':view(True),
            'deployment':{'nodes':[nodes[i] for i in sorted(active)],'edges':deploy_edges}}


def entries(graph):
    routes = [e for e in graph['entities'] if e['kind'] == 'endpoint']
    if routes:
        adjacency = defaultdict(list)
        for e in graph['edges']:
            if e['kind'] in ('HANDLED_BY','CALLS','CONTAINS_SYMBOL','SDK_API_CALL','CALLS_HTTP'):
                adjacency[e['source']].append(e['target'])
        def richness(n):
            seen, pending = set(), deque([(n['id'],0)])
            while pending and len(seen)<100:
                i,d = pending.popleft()
                if i in seen: continue
                seen.add(i)
                if d<3: pending.extend((t,d+1) for t in adjacency[i])
            return -len(seen), n.get('file',''), n['label']
        return sorted(routes, key=richness)[:500]
    return [e for e in graph['entities'] if e['kind'] == 'symbol' and e.get('has_body')][:500]


def architecture_view(graph, kind='system', entry_id=None, depth=2, limit=24, dependencies=False, layer='source', nested=False):
    if kind == 'system' and layer == 'source' and graph.get('architecture'):
        return responsibility_view(graph, limit=limit)
    by_id = {n['id']: n for n in graph['entities']}
    metadata = {'static_only': True, 'warning': 'Static relationships do not establish execution order or runtime reachability.'}
    if kind == 'system':
        views = project(graph)
        visible = [views['overview']] if layer=='source' else [views['deployment']] if layer=='infrastructure' else [views['overview'],views['deployment']]
        combined = {n['id']: n for view in visible for n in view['nodes']}
        all_edges = [e for view in visible for e in view['edges']]
        for edge in graph['edges']:
            if edge['kind'] != 'ENTRYPOINT':
                continue
            application = by_id[edge['target']].get('application_id')
            if application and application in combined and edge['source'] in combined:
                all_edges.append({**edge, 'target': application, 'kind': 'ENTRYPOINT_PACKAGE', 'support_edge_ids': [edge['id']]})
        # SDK aggregation is a projection, not a new service inferred from library names.
        sdks = [n for n in combined.values() if n['kind']=='sdk']
        if len(sdks)>=3:
            sdk_ids={n['id'] for n in sdks}
            group_id='projection:sdk-libraries'
            combined[group_id]=dict(id=group_id,kind='sdk_group',label=f'SDK libraries · {len(sdks)}',
                technology=', '.join(sorted(n['label'].replace(' (SDK)','') for n in sdks)),
                members=sorted(sdk_ids),evidence_ids=sorted({i for n in sdks for i in n.get('evidence_ids',[])}),
                identity='Aggregated library usage; no remote deployment or network endpoint established')
            for i in sdk_ids: combined.pop(i)
            regroup={}
            for e in all_edges:
                if e['target'] not in sdk_ids:
                    regroup[e['id']]=e
                    continue
                key=e['source']+'|'+e['kind']+'|'+e.get('resolution','resolved')
                group=regroup.setdefault(key,dict(id='projection:'+hashlib.sha256(key.encode()).hexdigest()[:20],
                    source=e['source'],target=group_id,kind=e['kind'],resolution=e.get('resolution','resolved'),evidence_ids=[],support_edge_ids=[],count=0))
                group['evidence_ids']=sorted(set(group['evidence_ids']+e['evidence_ids']))
                group['support_edge_ids']+=e.get('support_edge_ids',[e['id']])
                group['count']+=e.get('count',1)
            all_edges=list(regroup.values())
        ordered = sorted(combined.values(), key=lambda n: (n['kind'] not in ('application', 'deployable'), n['label']))
        nodes = ordered[:limit]
        active = {n['id'] for n in nodes}
        selected = [e for e in all_edges if e['source'] in active and e['target'] in active][:100]
        metadata.update(layer=layer,total_nodes=len(ordered), truncated=len(ordered)>limit or len(all_edges)>100,
                        note='Packages are source boundaries. Infrastructure arrows describe declarations. SDK nodes identify library usage.')
    else:
        candidates = entries(graph)
        entry_id = entry_id or (candidates[0]['id'] if candidates else None)
        if entry_id and entry_id not in by_id:
            raise ValueError('Unknown workflow entry')
        allowed = {'HANDLED_BY', 'CALLS', 'CONSTRUCTS', 'SDK_API_CALL', 'CONSTRUCTS_CLIENT', 'CALLS_HTTP', 'USES_RESOURCE'}
        if nested:
            allowed.add('CONTAINS_SYMBOL')
        if dependencies:
            allowed |= {'DEFINED_IN', 'IMPORTS', 'REEXPORTS', 'TYPE_REFERENCES'}
        adjacency = defaultdict(list)
        for edge in graph['edges']:
            if edge['kind'] in allowed:
                adjacency[edge['source']].append(edge)
        active, selected, seen_edges = set(), [], set()
        pending = deque([(entry_id, 0)] if entry_id else [])
        truncated = False
        while pending:
            identifier, level = pending.popleft()
            if identifier in active:
                continue
            if len(active) >= limit:
                truncated = True
                continue
            active.add(identifier)
            if level >= depth:
                truncated |= bool(adjacency[identifier])
                continue
            for edge in sorted(adjacency[identifier], key=lambda e: (e['kind'] == 'CONTAINS_SYMBOL', e['id'])):
                if len(seen_edges) >= 100:
                    truncated = True
                    break
                selected.append(edge)
                seen_edges.add(edge['id'])
                pending.append((edge['target'], level + 1))
        selected = [e for e in selected if e['source'] in active and e['target'] in active]
        nodes = [by_id[i] for i in sorted(active)]
        metadata.update(entry_id=entry_id, depth=depth, truncated=truncated,
                        nested_definitions=nested,
                        note='Solid arrows: resolved static calls. Optional dashed lexical definitions are not invocations. Select a function to explore from it.')
    return {'snapshot_id': graph['snapshot_id'], 'kind': kind, 'nodes': nodes, 'edges': selected, 'metadata': metadata}

