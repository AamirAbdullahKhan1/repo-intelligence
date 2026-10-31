"""Presentation-only indexing, bounded hierarchy and evidence-preserving abstraction.

Consumes saved canonical records. Does not parse source, resolve new calls, or mutate snapshots.
"""
from collections import Counter, defaultdict
import hashlib
import json
from .projections import architecture_view, entries

DECLARATIONS = {'BINDS_RESOURCE','BINDS_SERVICE','DECLARES_CONTAINER','CONFIGURES_LOG_SINK','STARTS_AFTER','ENTRYPOINT'}
CALLS = {'CALLS','CONSTRUCTS','HANDLED_BY','SDK_API_CALL','CONSTRUCTS_CLIENT','CALLS_HTTP'}
IMPORTS = {'IMPORTS','REEXPORTS','TYPE_REFERENCES','DEFINED_IN'}
GROUPS = {
    'group:sdk': ('SDK libraries', {'sdk'}),
    'group:http': ('External HTTP integrations', {'external_service'}),
    'group:infrastructure': ('Infrastructure declarations', {'deployable','storage','container'}),
}

def stable(prefix, key):
    return prefix + ':' + hashlib.sha256(key.encode()).hexdigest()[:20]

def status(record):
    value = record.get('resolution', 'resolved')
    if value in ('ambiguous','conditional','unresolved'): return value
    return 'confirmed'

class Index:
    def __init__(self, graph):
        self.graph = graph
        self.nodes = {n['id']:n for n in graph['entities']}
        self.evidence = {e['id']:e for e in graph['evidence']}
        self.children = defaultdict(list)
        self.files = {}
        self.outgoing = defaultdict(list)
        self.external_incoming = Counter()
        self.unknown_by_owner = defaultdict(list)
        self.symbols_by_file = defaultdict(list)
        for n in graph['entities']:
            if n['kind']=='component': self.children[n.get('application_id')].append(n)
            if n['kind'] in ('symbol','endpoint','file'): self.children[n.get('component_id')].append(n)
            if n['kind']=='file': self.files[n.get('file')] = n
            if n['kind']=='symbol' and n.get('has_body'):
                bounds=[self.evidence[i] for i in n.get('evidence_ids',[]) if i in self.evidence and self.evidence[i]['rule']=='symbol-declaration']
                if bounds: self.symbols_by_file[n.get('file')].append((bounds[0],n))
        for edge in graph['edges']:
            self.outgoing[edge['source']].append(edge)
            if edge['kind']=='CALLS' and self.nodes[edge['source']].get('component_id')!=self.nodes[edge['target']].get('component_id'):
                self.external_incoming[edge['target']]+=1
        for i,u in enumerate(graph['unknowns']):
            file=self.files.get(u.get('file'))
            if file:
                for owner in (file['id'],file.get('component_id'),file.get('application_id')):
                    if owner: self.unknown_by_owner[owner].append(i)
        self.unknown_sources = {}

    def unknown_source(self, i):
        if i in self.unknown_sources: return self.unknown_sources[i]
        u=self.graph['unknowns'][i]
        ev=next((self.evidence[e] for e in u.get('evidence_ids',[]) if e in self.evidence),None)
        candidates=[]
        if ev:
            candidates=[(bound['end']-bound['start'],n['id']) for bound,n in self.symbols_by_file[u.get('file')]
                        if bound['start']<=ev['start'] and ev['end']<=bound['end']]
        source=min(candidates)[1] if candidates else self.files.get(u.get('file'),{}).get('id')
        self.unknown_sources[i]=source
        return source

    def members(self, scope):
        if not scope: return set(self.nodes)
        if scope in GROUPS:
            return {n['id'] for n in self.nodes.values() if n['kind'] in GROUPS[scope][1]}
        n=self.nodes.get(scope)
        if n is None: raise ValueError('Unknown exploration scope')
        if n['kind']=='application':
            return {i for i,x in self.nodes.items() if x.get('application_id')==scope or i==scope}
        if n['kind']=='component':
            return {i for i,x in self.nodes.items() if x.get('component_id')==scope or i==scope}
        return {scope}

    def unknown_indices(self, scope):
        if not scope: return list(range(len(self.graph['unknowns'])))
        n=self.nodes.get(scope,{})
        if n.get('kind') in ('application','component','file'): return self.unknown_by_owner[scope]
        if n.get('kind')=='symbol':
            file=self.files.get(n.get('file'),{})
            return [i for i in self.unknown_by_owner[file.get('id')] if self.unknown_source(i)==scope]
        return []

    def decorate(self, n):
        result={**n,'canonical_id':n['id'],'display_label':n['label'],'resolution':status(n)}
        if n['kind'] in ('application','component'):
            contents=self.members(n['id'])
            counts=Counter(self.nodes[i]['kind'] for i in contents)
            result['stats']={'files':counts['file'],'symbols':counts['symbol'],'entry_points':counts['endpoint'],
                             'components':counts['component'],'unresolved':len(self.unknown_indices(n['id']))}
            result['can_expand']=True
        if n['kind']=='component':
            group=n.get('group','')
            result['role']=('Server source module' if group.startswith('src/server') else
                            'UI source module' if group.startswith(('src/components','src/features','src/hooks')) else
                            'Routes and pages (may contain server code)' if group in ('src/app','app') else 'Logical source module')
        elif n['kind']=='application': result['role']=n.get('boundary') or 'Package boundary; deployment not implied'
        return result

    def group(self, identifier):
        label,kinds=GROUPS[identifier]
        members=sorted(n['id'] for n in self.nodes.values() if n['kind'] in kinds)
        return {'id':identifier,'kind':'architecture_group','label':label,'display_label':label,
                'members':members,'can_expand':True,'resolution':'confirmed',
                'technology':f'{len(members)} recorded identities',
                'identity':'Presentation group of canonical records; no new service or communication inferred',
                'evidence_ids':sorted({e for i in members for e in self.nodes[i].get('evidence_ids',[])})}

    def hierarchy(self, parent=None, query='', offset=0, limit=30):
        if not parent:
            values=[n for n in self.nodes.values() if n['kind']=='application']
            values += [self.group(k) for k in GROUPS if self.group(k)['members']]
        elif parent in GROUPS:
            values=[self.nodes[i] for i in self.group(parent)['members']]
        else:
            node=self.nodes.get(parent)
            if not node: raise ValueError('Unknown hierarchy parent')
            values=self.children[parent]
            if node['kind']=='component': values=[n for n in values if n['kind'] in ('symbol','endpoint')]
            elif node['kind']!='application': values=[]
        values=[n for n in values if query.lower() in (n['label']+' '+n.get('file','')).lower()]
        values=sorted(values,key=lambda n:(n['kind']!='endpoint',n['label']=='<anonymous>',n['label'].lower(),n['id']))
        return {'snapshot_id':self.graph['snapshot_id'],'parent_id':parent,'total':len(values),'offset':offset,'limit':limit,
                'items':[self.decorate(n) if n['id'] in self.nodes else n for n in values[offset:offset+limit]]}

    def aggregate(self, edges, endpoint, kind_map=None, keep_self=False):
        groups={}
        for e in edges:
            a,b=endpoint(e['source']),endpoint(e['target'])
            if not a or not b or a==b and not keep_self: continue
            kind=kind_map(e) if kind_map else e['kind']
            resolution=status(e)
            key=(a,b,kind,resolution)
            value=groups.setdefault(key,{'id':stable('presentation-edge','|'.join(key)),'source':a,'target':b,'kind':kind,
                'resolution':resolution,'evidence_ids':[],'support_edge_ids':[],'count':0,
                'derivation':'Aggregated canonical source records. No runtime sequence or network delivery established.'})
            value['evidence_ids']+=e['evidence_ids'];value['support_edge_ids'].append(e['id']);value['count']+=1
        raw={e['id']:e for e in edges}
        for v in groups.values():
            v['evidence_ids']=sorted(set(v['evidence_ids']))
            if keep_self and v['count']==1:
                source=raw[v['support_edge_ids'][0]]
                v.update(source)
                v['resolution']=status(source)
        return sorted(groups.values(),key=lambda e:(-e['count'],e['id']))

    def system(self, scope=None, layer='source', limit=24, dependencies=False, connections=False):
        if layer in ('infrastructure','all') and not scope:
            old=architecture_view(self.graph,'system',limit=limit,layer=layer)
            old['nodes']=[self.decorate(n) if n['id'] in self.nodes else n for n in old['nodes']]
            return old
        if scope in GROUPS:
            values=[self.decorate(self.nodes[i]) for i in self.group(scope)['members']]
            ids={n['id'] for n in values}
            links=[{**e,'resolution':status(e)} for e in self.graph['edges'] if e['source'] in ids and e['target'] in ids and e['kind'] in DECLARATIONS]
            return self.view('system',values[:limit],links,scope,len(values)>limit)
        scope_node=self.nodes.get(scope,{})
        if scope and scope_node.get('kind') not in ('application','component'): raise ValueError('Select a package or component for system exploration')
        if scope_node.get('kind')=='component':
            eligible=[]
            grouped={i:g for g in ('group:sdk','group:http') for i in self.group(g)['members']}
            def endpoint(identifier):
                return grouped.get(identifier) or self.nodes[identifier].get('component_id')
            for edge in self.graph['edges']:
                if not (edge['kind'] in CALLS-{'HANDLED_BY'} or dependencies and edge['kind'] in IMPORTS-{'DEFINED_IN'}):continue
                if scope in (endpoint(edge['source']),endpoint(edge['target'])):eligible.append(edge)
            links=self.aggregate(eligible,endpoint,lambda e:'USES_SDK' if e['kind'] in ('SDK_API_CALL','CONSTRUCTS_CLIENT') else
                                 'HTTP_INTEGRATION' if e['kind']=='CALLS_HTTP' else 'IMPORT_DEPENDENCY' if e['kind'] in IMPORTS else 'MODULE_REFERENCE')
            peers=Counter()
            for edge in links:
                for identifier in (edge['source'],edge['target']):peers[identifier]+=edge['count']
            identifiers=[scope]+sorted((i for i in peers if i!=scope),key=lambda i:(-peers[i],i))
            values=[self.group(i) if i in GROUPS else self.decorate(self.nodes[i]) for i in identifiers[:limit]]
            result=self.view('system',values,links,scope,len(identifiers)>limit,edge_limit=60 if connections else 24)
            result['metadata']['note']='Logical module neighborhood. Function-level records belong to Core workflow.'
            return result
        applications=[n for n in self.nodes.values() if n['kind']=='application' and (not scope or n['id']==scope)]
        applications=sorted(applications,key=lambda n:(n.get('root')!='.',n['label'],n['id']))
        package_total=len(applications)
        applications=applications[:max(1,min(8 if limit<=24 else limit-3,limit-3))]
        package_ids={n['id'] for n in applications}
        components=[n for n in self.nodes.values() if n['kind']=='component' and n.get('application_id') in package_ids]
        degree=Counter()
        for e in self.graph['edges']:
            if e['kind'] in CALLS:
                for i in (e['source'],e['target']):
                    c=self.nodes[i].get('component_id')
                    if c:degree[c]+=1
        components=sorted(components,key=lambda n:(-int(n.get('group','').startswith('src/server/')),-degree[n['id']],n['label'],n['id']))
        if not scope:
            representatives=[]
            for prefixes in (('src/app','app'),('src/components','src/features','src/hooks')):
                match=next((n for n in components if n.get('group','').startswith(prefixes)),None)
                if match:representatives.append(match)
            components=representatives+[n for n in components if n not in representatives]
        # Keep the first screen small. All omitted canonical modules remain in paginated hierarchy.
        reserve=len(applications)+sum(bool(self.group(g)['members']) for g in GROUPS)
        component_budget=(7 if not scope else 14) if limit<=24 else limit-reserve
        selected=components[:max(0,min(component_budget,limit-reserve))]
        values=[self.decorate(n) for n in applications+selected]
        active={n['id'] for n in values}
        for g in GROUPS:
            node=self.group(g)
            if node['members'] and len(values)<limit: values.append(node)
        group_for={i:g for g in GROUPS for i in self.group(g)['members']}
        def endpoint(i):
            if i in group_for:return group_for[i] if group_for[i] in {n['id'] for n in values} else None
            n=self.nodes[i]
            if n['kind']=='application':return i if i in active else None
            component=n.get('component_id')
            if component in active:return component
            owner=n.get('application_id')
            return owner if owner in active else None
        eligible=[]
        for e in self.graph['edges']:
            if not (e['kind'] in (CALLS-{'HANDLED_BY'}) or dependencies and e['kind'] in IMPORTS-{'DEFINED_IN'}):continue
            a,b=self.nodes[e['source']],self.nodes[e['target']]
            same_owner=a.get('application_id') and a.get('application_id')==b.get('application_id')
            # Omitted helper modules must not appear as calls to their containing package.
            if same_owner and (a.get('component_id') not in active or b.get('component_id') not in active):continue
            eligible.append(e)
        links=self.aggregate(eligible,endpoint,lambda e:'USES_SDK' if e['kind'] in ('SDK_API_CALL','CONSTRUCTS_CLIENT') else
                             'HTTP_INTEGRATION' if e['kind']=='CALLS_HTTP' else 'IMPORT_DEPENDENCY' if e['kind'] in IMPORTS else 'MODULE_REFERENCE')
        total_links=len(links)
        if not connections:
            outbound=Counter();important=[]
            for link in sorted(links,key=lambda e:(e['kind'] not in ('USES_SDK','HTTP_INTEGRATION'),-e['count'],e['id'])):
                if outbound[link['source']]<2:
                    important.append(link);outbound[link['source']]+=1
            links=important
        for n in selected:
            if n.get('application_id') in active:
                links.append({'id':stable('ownership',n['id']),'source':n['application_id'],'target':n['id'],
                              'kind':'CONTAINS_COMPONENT','resolution':'confirmed','evidence_ids':n.get('evidence_ids',[]),
                              'support_entity_ids':[n['id']],'derivation':'Directory/package ownership, not deployment or a call','count':1})
        result=self.view('system',values[:limit],links,scope,len(selected)<len(components) or len(applications)<package_total,edge_limit=60 if connections else 24)
        result['metadata']['omitted_packages']=package_total-len(applications)
        result['metadata']['omitted_components']=len(components)-len(selected)
        result['metadata']['omitted_relationship_groups']=total_links-len([e for e in links if e['kind']!='CONTAINS_COMPONENT'])
        result['metadata']['note']='Selected logical modules and source boundaries. Ownership and source references do not establish deployable services.'
        return result

    def view(self, kind, nodes, edges, scope, truncated=False, edge_limit=100):
        ids={n['id'] for n in nodes}
        edges=[e for e in edges if e['source'] in ids and e['target'] in ids]
        return {'snapshot_id':self.graph['snapshot_id'],'kind':kind,'nodes':nodes,'edges':edges[:edge_limit],
                'metadata':{'scope_id':scope,'truncated':truncated or len(edges)>edge_limit,'static_only':True,
                            'warning':'Static support does not establish runtime order or reachability.'}}

    def candidates(self, scope=None, query='', offset=0, limit=30):
        ids=self.members(scope)
        values=[n for n in entries(self.graph) if n['id'] in ids]
        # Include implemented functions and classes: routes are not the only possible starting points.
        known={n['id'] for n in values}
        values += sorted((n for n in self.nodes.values() if n['id'] in ids and n['id'] not in known and n['kind']=='symbol'
                          and (n.get('has_body') or 'Class' in n.get('declaration_kind',''))),
                         key=lambda n:(n['label']=='<anonymous>',-self.external_incoming[n['id']],abs(len({e['target'] for e in self.outgoing[n['id']] if e['kind'] in CALLS})-6),n['label'],n['id']))
        values=[n for n in values if query.lower() in (n['label']+' '+n.get('file','')).lower()]
        return {'snapshot_id':self.graph['snapshot_id'],'total':len(values),'offset':offset,'limit':limit,
                'items':[self.decorate(n) for n in values[offset:offset+limit]]}

    def workflow(self, scope=None, entry=None, depth=2, limit=24, dependencies=False, nested=False, show_unknown=False):
        if scope in self.nodes and self.nodes[scope]['kind'] not in ('application','component'):
            entry=entry or scope
        entry=entry or next((n['id'] for n in self.candidates(scope,limit=1)['items']),None)
        if entry is None:
            result=self.view('workflow',[],[],scope)
            result['metadata']['note']='No implemented source entry in this selection. Choose a logical module or function.'
            return result
        if entry and entry not in self.nodes:raise ValueError('Unknown workflow entry')
        if scope and entry and entry not in self.members(scope):raise ValueError('Entry does not belong to the selected scope')
        result=architecture_view(self.graph,'workflow',entry,depth,limit,dependencies,'source',nested)
        result['nodes']=[self.decorate(n) for n in result['nodes']]
        result['edges']=self.aggregate(result['edges'],lambda i:i,keep_self=True)
        result['metadata']['scope_id']=scope
        if show_unknown:
            active={n['id'] for n in result['nodes']}
            relevant=[i for i in self.unknown_indices(scope) if self.unknown_source(i) in active]
            room=max(0,min(5,limit-len(active),100-len(result['edges'])))
            for i in relevant[:room]:
                node,edge=self.uncertainty(i)
                result['nodes'].append(node);result['edges'].append(edge)
            result['metadata']['unresolved_markers_omitted']=max(0,len(relevant)-room)
        return result

    def uncertainty(self, i):
        raw=self.graph['unknowns'][i]
        uid=stable('unresolved',json.dumps(raw,sort_keys=True))
        node={'id':uid,'kind':'unresolved','label':'Unknown '+raw['kind']+' target','resolution':'unresolved',
              'file':raw.get('file'),'source_id':self.unknown_source(i),'evidence_ids':raw.get('evidence_ids',[]),'reason':raw['reason'],'unknown_index':i}
        edge={'id':uid+':reference','source':self.unknown_source(i),'target':uid,'kind':'UNRESOLVED_REFERENCE',
              'resolution':'unresolved','evidence_ids':raw.get('evidence_ids',[]),'unknown_index':i,
              'derivation':raw['reason'],'limitation':'Placeholder records an unresolved reference; no target entity or communication is inferred.'}
        return node,edge

    def issues(self, scope=None, offset=0, limit=30):
        indices=self.unknown_indices(scope)
        return {'total':len(indices),'offset':offset,'limit':limit,'items':[
            {**self.graph['unknowns'][i],'id':stable('unresolved',json.dumps(self.graph['unknowns'][i],sort_keys=True)),
             'unknown_index':i,'resolution':'unresolved','source_id':self.unknown_source(i)} for i in indices[offset:offset+limit]]}

    def evidence_record(self, identifier, scope=None, layer='source', limit=24, dependencies=False):
        record=self.nodes.get(identifier) or next((e for e in self.graph['edges'] if e['id']==identifier),None)
        if record is None and identifier in GROUPS:record=self.group(identifier)
        if record is None and identifier.startswith('unresolved:'):
            for i,u in enumerate(self.graph['unknowns']):
                uid=stable('unresolved',json.dumps(u,sort_keys=True))
                if identifier in (uid,uid+':reference'):
                    node,edge=self.uncertainty(i);record=node if identifier==uid else edge;break
        if record is None:
            view=self.system(scope,layer,limit,dependencies,connections=True) if not scope or self.nodes.get(scope,{}).get('kind') in ('application','component') or scope in GROUPS else {'nodes':[],'edges':[]}
            record=next((r for key in ('nodes','edges') for r in view[key] if r['id']==identifier),None)
        if record is None and identifier.startswith('presentation-edge:'):
            record=next((e for e in self.aggregate(self.graph['edges'],lambda i:i,keep_self=True) if e['id']==identifier),None)
        if record is None:return None
        result={**record,'resolution':status(record)}
        if 'unknown_index' in record and record.get('source_id'):
            result['source']=record['source_id'];result['target']=record['id']
            result['limitation']='Source association uses enclosing declaration/citation ranges. The target remains unknown; no execution or communication is inferred.'
        if record.get('support_edge_ids'):
            supported=set(record['support_edge_ids'])
            result['supporting_relationships']=[{**e,'source_label':self.nodes[e['source']]['label'],
                'target_label':self.nodes[e['target']]['label'],'resolution':status(e)} for e in self.graph['edges'] if e['id'] in supported][:10]
        for side in ('source','target'):
            eid=result.get(side)
            if eid:result[side+'_label']=self.nodes.get(eid,{}).get('label') or (self.group(eid)['label'] if eid in GROUPS else 'Unknown target')
        if record.get('kind') in DECLARATIONS:result['limitation']='Configuration declaration; runtime invocation and communication are not established.'
        elif 'limitation' not in result:result['limitation']='Source-supported static relationship; runtime execution, order and reachability are not guaranteed.'
        return result

    def summary(self):
        kinds=Counter(n['kind'] for n in self.nodes.values())
        language_names={'.ts':'TypeScript','.tsx':'TypeScript','.js':'JavaScript','.jsx':'JavaScript','.mjs':'JavaScript','.cjs':'JavaScript','.py':'Python (inventory only)'}
        languages=Counter()
        for ext,count in self.graph.get('languages',{}).items():
            if ext in language_names:languages[language_names[ext]]+=count
        package_nodes=sorted((n for n in self.nodes.values() if n['kind']=='application'),key=lambda n:(n.get('root')!='.',n['label'],n['id']))
        packages=[self.decorate(n) for n in package_nodes[:20]]
        dependencies={name for p in self.graph.get('packages',[]) for name in p.get('dependencies',[])}
        frameworks=sorted({n['technology'].replace(' package','') for n in package_nodes if n.get('technology') and n['technology']!='JS/TS package'} |
                          {label for key,label in {'next':'Next.js','react':'React','express':'Express','@nestjs/core':'NestJS','hono':'Hono','fastify':'Fastify'}.items() if key in dependencies})
        return {'snapshot_id':self.graph['snapshot_id'],'languages':dict(languages),'frameworks':frameworks,
                'packages':packages,'package_count':len(package_nodes),'packages_truncated':len(package_nodes)>20,'module_count':kinds['component'],'entry_point_count':kinds['endpoint'],
                'integrations':[self.decorate(n) for n in self.nodes.values() if n['kind'] in ('sdk','external_service')][:30],
                'storage':[self.decorate(n) for n in self.nodes.values() if n['kind']=='storage'][:30],
                'integration_count':kinds['sdk']+kinds['external_service'],'storage_count':kinds['storage'],
                'infrastructure_count':sum(kinds[k] for k in ('storage','container','deployable')),
                'supported_relationships':len(self.graph['edges']),'unresolved_references':len(self.graph['unknowns']),
                'relationship_statuses':dict(Counter(status(e) for e in self.graph['edges'])),
                'coverage':{'inventoried_files':self.graph['coverage']['inventoried_files'],'parsed_files':self.graph['coverage']['parsed_source_files'],
                            'syntax_failures':self.graph['coverage'].get('syntax_failures',0),'skipped_files':len(self.graph['coverage'].get('skipped',[]))},
                'limitations':['Only supplied TypeScript/JavaScript source is analyzed. Other languages are inventory only.',
                               'Directory groups are logical modules; packages are not automatically deployed services.',
                               'SDK use identifies a library; an actual database/server endpoint may remain unknown.',
                               'Dynamic dispatch, relative API destinations, generated code and framework callbacks may remain unresolved.',
                               'Configuration resources are declarations, not observed runtime connections.']}
