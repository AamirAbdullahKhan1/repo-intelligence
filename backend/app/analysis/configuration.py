"""Conservative Docker Compose inventory: declarations, never inferred traffic."""
import hashlib
from pathlib import Path
import yaml

def augment(graph: dict, root: Path):
    def digest(text):
        return hashlib.sha256(text.encode()).hexdigest()
    def identifier(kind, text):
        return kind + ':' + digest(text)[:20]
    for path in sorted(root.rglob('*')):
        if path.name not in ('compose.yml', 'compose.yaml', 'docker-compose.yml', 'docker-compose.yaml'):
            continue
        relative = path.relative_to(root).as_posix()
        if any(p in ('.git', 'node_modules', 'vendor', 'dist') for p in path.relative_to(root).parts):
            continue
        if path.stat().st_size > 256 * 1024:
            graph['diagnostics'].append({'kind': 'configuration', 'file': relative, 'reason': 'YAML byte limit'})
            continue
        text = path.read_bytes().decode('utf-8')
        try:
            count, depth = 0, 0
            for event in yaml.parse(text, Loader=yaml.SafeLoader):
                count += 1
                if isinstance(event,(yaml.MappingStartEvent,yaml.SequenceStartEvent)): depth += 1
                if isinstance(event,(yaml.MappingEndEvent,yaml.SequenceEndEvent)): depth -= 1
                if count>10000 or depth>32 or isinstance(event,yaml.AliasEvent):
                    raise ValueError('YAML aliases or excessive structure are unsupported')
            document = yaml.compose(text, Loader=yaml.SafeLoader)
            if not isinstance(document, yaml.MappingNode):
                continue
            services = next((v for k,v in document.value if k.value == 'services'), None)
            if not isinstance(services, yaml.MappingNode):
                continue
            ids, definitions = {}, {}
            for key, definition in services.value:
                if not isinstance(key, yaml.ScalarNode) or not isinstance(definition, yaml.MappingNode):
                    continue
                eid = identifier('evidence', relative+':'+str(key.start_mark.index)+':compose-service')
                prefix, end = text[:key.start_mark.index], text[:definition.end_mark.index]
                graph['evidence'].append(dict(id=eid, file=relative, start=len(prefix.encode('utf-16-le'))//2,
                    end=len(end.encode('utf-16-le'))//2, line=key.start_mark.line+1, column=key.start_mark.column+1,
                    sha256=digest(text), rule='compose-service-declaration', origin='infrastructure'))
                nid = identifier('deployable', relative+':'+key.value)
                graph['entities'].append(dict(id=nid,kind='deployable',label=key.value,profile=relative,
                    technology='Compose service declaration',evidence_ids=[eid]))
                ids[key.value] = (nid,eid)
                definitions[key.value] = {k.value:v for k,v in definition.value if isinstance(k,yaml.ScalarNode)}
            for name, definition in definitions.items():
                depends = definition.get('depends_on')
                targets = [n.value for n in depends.value if isinstance(n,yaml.ScalarNode)] if isinstance(depends,yaml.SequenceNode) else [k.value for k,v in depends.value] if isinstance(depends,yaml.MappingNode) else []
                for target in targets:
                    if target not in ids:
                        continue
                    source, support = ids[name]
                    graph['edges'].append(dict(id=identifier('edge',relative+':'+name+':'+target),source=source,target=ids[target][0],
                        kind='STARTS_AFTER',evidence_ids=[support],resolution='resolved',grounding='passed',profile=relative,
                        derivation='Compose depends_on declaration; communication and runtime readiness not established'))
        except (yaml.YAMLError, ValueError, RecursionError):
            graph['diagnostics'].append({'kind':'configuration','file':relative,'reason':'Unsupported or invalid YAML; no declarations inferred'})
    graph['configuration_parser'] = {'pyyaml': yaml.__version__, 'scope':'Compose services and depends_on declarations only'}
