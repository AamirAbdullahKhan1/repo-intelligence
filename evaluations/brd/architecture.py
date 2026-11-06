"""Evidence-preserving abstraction and intended-process views for BRD lab 2.1."""
import hashlib
import json
import re


def norm(text):
    return ' '.join(text.split())


def clean(text):
    return str(text).replace('|', '/').replace('`', "'").replace('<', '(').replace('>', ')').replace('\n', ' ')


def label(text):
    text = re.sub(r'\s*\([A-Z][A-Z0-9_]*-\d+(?:\s*,\s*[A-Z][A-Z0-9_]*-\d+)*\)', '', str(text))
    return re.sub(r'[^\w .,()/:-]', ' ', text).strip()[:110] or 'Unspecified'


def enrich(model, source):
    blocks = {r['source_id']: r for r in source['records']}
    entities = {e['id']: e for e in model['entities']}
    issues = []
    def issue(code, identity, message):
        issues.append({'code': code, 'id': identity, 'message': message})
    def evidence(refs):
        return (isinstance(refs, list) and 0 < len(refs) <= 30 and all(
            isinstance(r, dict) and isinstance(r.get('source_id'), str) and r['source_id'] in blocks and
            isinstance(r.get('quote'), str) and 1 <= len(norm(r['quote'])) <= 2000 and any(c.isalnum() for c in r['quote']) and
            norm(r['quote']) in norm(blocks[r['source_id']]['text']) for r in refs))
    for entity in model['entities']:
        vendor = entity.get('vendor_status', 'unspecified')
        if vendor not in ('selected', 'pending', 'candidate', 'unspecified', 'not_applicable'):
            issue('vendor_status', entity['id'], 'Invalid vendor-selection status; treated as unspecified.')
            vendor = 'unspecified'
        entity['vendor_status'] = vendor
        if entity['kind'] != 'operation':
            continue
        owner = entity.get('owner_id')
        if (not isinstance(owner, str) or owner not in entities or entities[owner]['kind'] != 'component' or
                not evidence(entity.get('owner_evidence'))):
            if owner is not None:
                model['validation']['quarantined'].append({'group': 'ownership', 'id': entity['id'], 'reason': 'Owner must be an existing component with exact supporting evidence.'})
            entity['owner_id'] = None
            entity['owner_evidence'] = []
            issue('unowned_operation', entity['id'], 'Operation has no validated logical owner; retained without aggregation.')
    refs = [r for group in ('entities', 'relationships', 'workflows', 'findings') for item in model[group] for r in item['evidence']]
    for entity in model['entities']:
        refs.extend(entity.get('owner_evidence', []) if entity.get('owner_id') else [])
    for workflow in model['workflows']:
        steps, transitions = workflow.get('steps', []), workflow.get('transitions', [])
        if not isinstance(steps, list) or len(steps) > 60 or not isinstance(transitions, list) or len(transitions) > 120:
            steps, transitions = [], []
            issue('process_shape', workflow['id'], 'Invalid or over-budget process arrays; no process sequence compiled.')
        accepted_steps, accepted_transitions = {}, {}
        for step in steps:
            valid = (isinstance(step, dict) and isinstance(step.get('id'), str) and
                     re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', step['id']) and step['id'] not in accepted_steps and
                     step.get('kind') in ('action', 'decision', 'approval', 'validation', 'authorization', 'outcome') and
                     isinstance(step.get('label'), str) and 0 < len(step['label']) <= 500 and
                     step.get('approval_requirement') in ('required', 'conditional', 'not_required', 'unspecified') and
                     (step.get('entity_id') is None or isinstance(step.get('entity_id'), str) and
                      step['entity_id'] in workflow['entity_ids']) and evidence(step.get('evidence')))
            if valid:
                accepted_steps[step['id']] = step
                refs.extend(step['evidence'])
            else:
                issue('invalid_step', workflow['id'], 'A process step failed evidence, identity or entity-membership checks.')
        for transition in transitions:
            valid = (isinstance(transition, dict) and isinstance(transition.get('id'), str) and
                     re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,63}', transition['id']) and transition['id'] not in accepted_transitions and
                     isinstance(transition.get('source'), str) and transition['source'] in accepted_steps and
                     isinstance(transition.get('target'), str) and transition['target'] in accepted_steps and
                     transition.get('branch') in ('normal', 'success', 'failure', 'conditional') and
                     isinstance(transition.get('condition'), str) and 0 < len(transition['condition']) <= 500 and
                     evidence(transition.get('evidence')))
            if valid:
                accepted_transitions[transition['id']] = transition
                refs.extend(transition['evidence'])
                if transition['branch'] in ('conditional', 'failure') and transition['condition'].lower() == 'unspecified':
                    issue('unknown_guard', workflow['id'], 'A conditional/failure path has an unspecified guard.')
            else:
                issue('invalid_transition', workflow['id'], 'Transition lacks valid endpoints, guard classification or evidence.')
        workflow['steps'], workflow['transitions'] = list(accepted_steps.values()), list(accepted_transitions.values())
        basis = workflow.get('sequence_basis', 'unspecified')
        workflow['sequence_basis'] = basis if basis in ('explicit', 'derived', 'unspecified') else 'unspecified'
        adjacency = {key: [] for key in accepted_steps}
        incoming = {key: [] for key in accepted_steps}
        for transition in accepted_transitions.values():
            adjacency[transition['source']].append(transition['target'])
            incoming[transition['target']].append(transition['source'])
        declared_entries = workflow.get('entry_step_ids', [])
        if not isinstance(declared_entries, list) or not all(isinstance(key, str) and key in accepted_steps for key in declared_entries):
            declared_entries = []
            issue('invalid_process_entry', workflow['id'], 'Process entry IDs are absent from accepted steps.')
        workflow['entry_step_ids'] = list(dict.fromkeys(declared_entries))
        if accepted_steps and not declared_entries:
            issue('entry_not_declared', workflow['id'], 'Process has no explicit starting-step declaration; roots are only a structural fallback.')
        if not accepted_steps:
            issue('no_process_steps', workflow['id'], 'Workflow has an interaction inventory but no validated process steps.')
        action_approvals = [step for step in accepted_steps.values() if step.get('approval_requirement') in ('required', 'conditional')]
        if workflow['human_approval'] in ('required', 'conditional') or action_approvals:
            approvals = [key for key, step in accepted_steps.items() if step['kind'] == 'approval']
            reachable = set(approvals)
            pending = approvals[:]
            while pending:
                for target in adjacency[pending.pop()]:
                    if target not in reachable:
                        reachable.add(target); pending.append(target)
            if not approvals or not any(key in reachable and step['kind'] == 'action' for key, step in accepted_steps.items()):
                issue('missing_approval_gate', workflow['id'], 'Declared approval has no evidenced path to a subsequent action.')
            if (workflow['human_approval'] == 'required' or any(s.get('approval_requirement') == 'required' for s in action_approvals)) and approvals:
                starts = declared_entries or [key for key in accepted_steps if not incoming[key]]
                bypass = {key for key in starts if key not in approvals}
                pending = list(bypass)
                while pending:
                    for target in adjacency[pending.pop()]:
                        if target not in approvals and target not in bypass:
                            bypass.add(target); pending.append(target)
                if any(key in bypass and step['kind'] == 'action' and (step.get('approval_requirement') == 'required' or
                       workflow['human_approval'] == 'required' and re.search(r'\b(send|release|publish|pay|execute|close|commit)\b', step['label'], re.I))
                       for key, step in accepted_steps.items()):
                    issue('approval_bypass', workflow['id'], 'A consequential action has a represented path bypassing required approval.')
        if re.search(r'\b(fail|failed|failure|retry|cancel|error|unavailable|unsupported|denied)\b', workflow['failure_handling'], re.I) and accepted_steps and not any(
                t['branch'] == 'failure' for t in accepted_transitions.values()):
            issue('failure_not_modeled', workflow['id'], 'Failure behavior is described but has no structured failure branch; review applicability.')
        for key, step in accepted_steps.items():
            if step['kind'] == 'decision' and len(adjacency[key]) < 2:
                issue('incomplete_decision', workflow['id'], 'Decision has fewer than two represented outcomes.')
            if len(accepted_steps) > 1 and not adjacency[key] and not incoming[key]:
                issue('isolated_step', workflow['id'], 'Process contains an isolated step.')
        if accepted_steps and workflow['sequence_basis'] == 'unspecified':
            issue('unknown_sequence', workflow['id'], 'Step order is unspecified; only interaction view will be emitted.')
        workflow['process_status'] = 'needs_review' if any(i['id'] == workflow['id'] for i in issues) else 'structurally_valid'
    # Flag possible scope differences; never silently resolve the model's conflict claim.
    for finding in model['findings']:
        if finding['kind'] == 'conflict':
            text = ' '.join(blocks[r['source_id']]['text'] for r in finding['evidence'])
            if re.search(r'\b(pilot|test workload)\b', text, re.I) and re.search(r'\b(planning estimate|production capacity|production workload)\b', text, re.I):
                issue('scope_difference', finding['id'], 'Check whether differing values concern different workloads/releases rather than incompatible requirements.')
    units, omitted = [], 0
    by_source = {}
    for ref in refs:
        by_source.setdefault(ref['source_id'], []).append(norm(ref['quote']))
    for block in source['records']:
        for index, unit in enumerate(re.split(r'(?<=[.;!?])\s+(?=[A-Z0-9\u0080-\uffff])', block['text']), 1):
            if not unit.strip(): continue
            if len(units) >= 6000:
                omitted += 1; continue
            value = norm(unit)
            quotes = by_source.get(block['source_id'], [])
            status = 'fully_quoted' if any(value in q for q in quotes) else 'partially_quoted' if any(q in value for q in quotes) else 'not_quoted'
            units.append({'id': f"{block['source_id']}.C{index:02}", 'source_id': block['source_id'], 'text': unit,
                          'quotation_coverage': status, 'semantic_status': 'not_assessed'})
    degrees = {key: 0 for key in entities}
    for edge in model['relationships']:
        degrees[edge['source']] += 1; degrees[edge['target']] += 1
    # A component participates through its validated owned operations even when
    # it has no direct canonical edges of its own.
    for entity in model['entities']:
        if entity.get('owner_id') in degrees:
            degrees[entity['owner_id']] += degrees[entity['id']]
    for workflow in model['workflows']:
        for step in workflow['steps']:
            if step.get('entity_id') in degrees:
                degrees[step['entity_id']] += 1
    unconnected = [key for key, entity in entities.items() if entity['kind'] in ('actor', 'component', 'external_system') and
                   entity['status'] == 'intended' and not degrees[key]]
    for key in unconnected:
        issue('unconnected_entity', key, 'No supported interaction is represented; do not invent an edge to fill the gap.')
    unapplied = [key for key, entity in entities.items() if entity['kind'] == 'control' and active(entity) and not degrees[key]]
    for key in unapplied:
        issue('unlinked_control_scope', key, 'Control is described but has no represented target/process association; inspect its scope.')
    model['coverage'].update({'unowned_operations': [e['id'] for e in model['entities'] if e['kind'] == 'operation' and not e.get('owner_id')],
                              'unconnected_entities': unconnected, 'unlinked_controls': unapplied, 'clause_units': units,
                              'clause_budget_omissions': omitted, 'clause_coverage_scope': 'Lexical quote overlap only; not semantic completeness.'})
    model['quality_issues'] = issues
    if issues or model['validation']['quarantined']:
        model['validation']['status'] = 'needs_review'
    model['validation']['limitations'].append('Workflow gate and branch checks establish graph structure, not behavioral proof.')
    return model


def active(item):
    return item['status'] == 'intended' and item['release'] != 'future' and item['modality'] != 'prohibited'


def projected_graph(model):
    entities = {e['id']: e for e in model['entities']}
    owners = {e['id']: e['owner_id'] for e in model['entities'] if e['kind'] == 'operation' and
              e.get('owner_id') in entities and active(entities[e['owner_id']])}
    nodes = {key: value for key, value in entities.items() if active(value) and key not in owners}
    groups, internal = {}, []
    for edge in model['relationships']:
        if not active(edge): continue
        start, end = owners.get(edge['source'], edge['source']), owners.get(edge['target'], edge['target'])
        if start == end:
            internal.append(edge['id']); continue
        if start not in nodes or end not in nodes: continue
        key = (start, end, edge['type'])
        if key not in groups:
            groups[key] = {'id': 'A' + hashlib.sha256('|'.join(key).encode()).hexdigest()[:14],
                           'source': start, 'target': end, 'type': edge['type'], 'label': edge['type'].replace('_', ' ').lower(),
                           'evidence': [], 'supporting_relationship_ids': [], 'supporting_entity_ids': [],
                           'modalities': [], 'scopes': [], 'derivation': 'derived'}
        aggregate = groups[key]
        aggregate['supporting_relationship_ids'].append(edge['id'])
        aggregate['modalities'].append(edge['modality'])
        aggregate['scopes'].append(edge['scope'])
        aggregate['evidence'].extend(edge['evidence'])
        for endpoint in (edge['source'], edge['target']):
            if endpoint in owners:
                aggregate['supporting_entity_ids'].append(endpoint)
                aggregate['evidence'].extend(entities[endpoint]['owner_evidence'])
    for aggregate in groups.values():
        aggregate['evidence'] = list({(r['source_id'], r['quote']): r for r in aggregate['evidence']}.values())
        aggregate['supporting_entity_ids'] = sorted(set(aggregate['supporting_entity_ids']))
        aggregate['modalities'] = sorted(set(aggregate['modalities']))
        aggregate['scopes'] = sorted(set(aggregate['scopes']))
        if any(value in ('optional', 'desirable', 'mixed') for value in aggregate['modalities']):
            aggregate['label'] += ' (may or conditional)'
        if aggregate['supporting_entity_ids'] and aggregate['type'] in ('AUTHORIZES', 'APPLIES_TO'):
            aggregate['label'] += ' (scoped operations)'
    return nodes, list(groups.values()), internal


def compile_view(identity, title, nodes, edges, limit=16, kind='architecture'):
    degree = {key: sum(e['source'] == key or e['target'] == key for e in edges) for key in nodes}
    disconnected = sorted(key for key in nodes if not degree[key])
    rank = {'component': 6, 'external_system': 5, 'resource': 4, 'actor': 3, 'control': 2, 'data': 1, 'operation': 0}
    ordered = sorted((key for key in nodes if degree[key]), key=lambda key: (-rank.get(nodes[key]['kind'], 0), -degree[key], key))
    selected = []
    for category in ('actor', 'component', 'resource', 'external_system', 'control'):
        match = next((key for key in ordered if nodes[key]['kind'] == category), None)
        if match is not None: selected.append(match)
    selected.extend(key for key in ordered if key not in selected)
    selected = sorted(selected[:limit])
    # Trim nodes stranded by the bounded selection; report all omissions.
    retained_edges = [e for e in edges if e['source'] in selected and e['target'] in selected]
    selected = sorted({key for e in retained_edges for key in (e['source'], e['target'])})
    names = {key: f'N{i}' for i, key in enumerate(selected)}
    lines = ['flowchart LR'] + [f'  {names[key]}["{label(nodes[key]["label"])}"]' for key in selected]
    for edge in sorted(retained_edges, key=lambda e: e['id']):
        lines.append(f'  {names[edge["source"]]} -->|"{label(edge["label"])}"| {names[edge["target"]]}')
    return {'id': identity, 'title': title, 'kind': kind, 'source': '\n'.join(lines),
            'entity_ids': selected, 'relationship_ids': [e['id'] for e in retained_edges],
            'omitted_entity_ids': sorted(set(nodes) - set(selected)),
            'omitted_relationship_ids': sorted(set(e['id'] for e in edges) - set(e['id'] for e in retained_edges)),
            'unconnected_entity_ids': disconnected, 'trace': [nodes[key] for key in selected] + retained_edges,
            'syntax_validation': 'closed generated grammar; independent Mermaid parser not run'}


def build_views(model):
    original = {e['id']: e for e in model['entities']}
    relations = {e['id']: e for e in model['relationships']}
    nodes, edges, internal = projected_graph(model)
    views = []
    ordinary = [e for e in edges if e['type'] not in ('APPLIES_TO', 'AUTHORIZES', 'PRECEDES')]
    if ordinary:
        view = compile_view('overview', 'Intended overall architecture', nodes, ordinary)
        view['internal_relationship_ids'] = internal
        views.append(view)
    controls = [e for e in edges if e['type'] in ('APPLIES_TO', 'AUTHORIZES')]
    if controls:
        views.append(compile_view('controls', 'Cross-cutting controls', nodes, controls, 24, 'controls'))
    for workflow in model['workflows']:
        if not active(workflow): continue
        blocking = [issue['code'] for issue in model['quality_issues'] if issue['id'] == workflow['id'] and issue['code'] in
                    ('approval_bypass', 'missing_approval_gate', 'invalid_step', 'invalid_transition', 'unknown_sequence', 'invalid_process_entry')]
        if workflow['steps'] and workflow['sequence_basis'] != 'unspecified' and not blocking:
            step_nodes = {s['id']: {**s, 'kind': s['kind']} for s in workflow['steps']}
            transitions = [{**t, 'label': t['branch'] + (': ' + t['condition'] if t['condition'].lower() != 'unspecified' else
                           ': condition unspecified' if t['branch'] in ('conditional', 'failure') else '')}
                           for t in workflow['transitions']]
            view = compile_view(workflow['id'], 'Intended process ' + workflow['title'], step_nodes, transitions, 60, 'process')
            view['sequence_basis'] = workflow['sequence_basis']
            view['review_status'] = workflow['process_status']
        else:
            members = {key: original[key] for key in workflow['entity_ids'] if active(original[key])}
            links = [relations[key] for key in workflow['relationship_ids'] if active(relations[key])]
            view = compile_view(workflow['id'], 'Interaction view ' + workflow['title'], members, links, 40, 'interactions')
            view['process_not_compiled_reasons'] = blocking or ['No supported process order supplied.']
        if view['relationship_ids']:
            views.append(view)
    return views


def report(model, source, skill, views):
    blocks = {b['source_id']: b for b in source['records']}
    def refs(item):
        return '; '.join(dict.fromkeys(f"{blocks[r['source_id']]['requirement_id'] or r['source_id']} [L{blocks[r['source_id']]['start_line']}-L{blocks[r['source_id']]['end_line']}]" for r in item.get('evidence', [])))
    title = 'AI Requirements and Capability Inventory' if skill == 'ai-usage-inventory' else 'Application Requirements and Intended Architecture'
    out = [f'# {title}', '', '**BRD-only analysis · v2.1 · semantic review required**', '',
           'This report describes intended responsibilities and processes. Vendor selection, deployment and achieved results are not established by requirements alone.', '', '## Business context', '']
    context = next((b for b in source['records'] if b['kind'] != 'heading' and re.search(r'\b(purpose|context|overview|background)\b', b['section'], re.I)), None)
    if context:
        out += [clean(context['text']), '', refs({'evidence': [{'source_id': context['source_id']}]}), '']
    else:
        out += ['A business overview was not separately identified. Review the source ledger and component inventory.', '']
    if skill == 'ai-usage-inventory':
        out += ['## AI requirement assessment', '']
        if not model['entities']:
            out += ['No supported AI architecture entities were extracted from this input. This is an input-scoped finding, not proof about an implementation.', '']
        for finding in model['findings']:
            if finding['kind'] in ('observation', 'unknown', 'capability'):
                out += [clean(finding['description']) + ' ' + refs(finding), '']
    out += ['## Major logical responsibilities', '', '| Component | Scope | Evidence |', '|---|---|---|']
    for entity in model['entities']:
        if entity['kind'] == 'component': out.append(f"| {clean(label(entity['label']))} | {clean(entity['scope'])} | {refs(entity)} |")
    overview = next((v for v in views if v['id'] == 'overview'), None)
    out += ['', '## Overall intended architecture', '']
    if overview:
        out += ['Aggregated arrows retain the original relationship and ownership evidence in the structured result. They do not establish deployment boundaries.', '', '```mermaid', overview['source'], '```', '']
        out += ['View ID: overview. Supporting evidence: ' + '; '.join(dict.fromkeys(refs(item) for item in overview['trace'])) + '.', '']
        if overview['omitted_entity_ids']:
            out += ['View omissions and unresolved connections: ' + ', '.join(overview['omitted_entity_ids']) + '. See the structured model and audit report.', '']
    else:
        out += ['There are insufficient connected, supported relationships for an overall architecture. No connections were invented.', '']
    out += ['## Decisions and uncertainties', '', '| Finding | Status | Evidence |', '|---|---|---|']
    decisions = [f for f in model['findings'] if f['kind'] in ('decision', 'conflict', 'unknown')]
    for finding in decisions:
        out.append(f"| {clean(finding['title'])}: {clean(finding['description'])} | {finding['status']} | {refs(finding)} |")
    out += ['', '## Workflow catalogue', '', '| Workflow | Approval | Process structure | Evidence |', '|---|---|---|---|']
    for workflow in model['workflows']:
        out.append(f"| {clean(workflow['title'])} | {workflow['human_approval']} | {workflow['process_status']} / {workflow['sequence_basis']} | {refs(workflow)} |")
    out += ['', '## Selected intended processes', '']
    selected = [v for v in views if v['kind'] == 'process'][:3]
    if not selected: out += ['No validated process order is available. Interaction views remain available separately.', '']
    for view in selected:
        out += ['### ' + clean(view['title']), '', 'Sequence basis: ' + view['sequence_basis'] + '; review status: ' + view['review_status'] + '. Branches describe intended behavior, not observed execution.', '', '```mermaid', view['source'], '```', '']
        out += ['View ID: ' + clean(view['id']) + '. Supporting evidence: ' + '; '.join(dict.fromkeys(refs(item) for item in view['trace'])) + '.', '']
    out += ['All views, original entities, typed relationships and evidence remain in the structured result. The audit report contains the complete registers.', '',
            '## Review findings', '']
    for issue in model['quality_issues'][:20]:
        out.append(f"- {issue['code']} ({issue['id']}): {clean(issue['message'])}")
    if len(model['quality_issues']) > 20: out.append('- Additional findings are in the structured model and audit report.')
    if not model['quality_issues']: out.append('- No additional structural review issues were found; semantic correctness is still unverified.')
    units = model['coverage']['clause_units']
    out += ['', '## Coverage and limits', '',
            f"- Source blocks: {model['coverage']['source_blocks']}; blocks referenced by accepted top-level records: {model['coverage']['referenced_blocks']}.",
            f"- Lexical fragments fully quoted: {sum(u['quotation_coverage'] == 'fully_quoted' for u in units)}; partially quoted: {sum(u['quotation_coverage'] == 'partially_quoted' for u in units)}; not quoted: {sum(u['quotation_coverage'] == 'not_quoted' for u in units)}.",
            '- Quote coverage is not semantic completeness. Every fragment remains not assessed for full semantic support.',
            '- Ownership, guards and branch topology are structurally checked; behavioral correctness still requires review.',
            '- Empty diagrams are suppressed. View omissions and unowned/unconnected entities remain explicit in the model.',
            '- Only supplied text/Markdown is processed. Unsupported languages, extraction layouts and missing context can limit interpretation.',
            '- No independent Mermaid parser or runtime execution was used.', '']
    return '\n'.join(out)


def audit(model, source, views):
    out = ['# Complete analysis and evidence register', '', 'Semantic correctness remains unverified.', '']
    for group in ('entities', 'relationships', 'workflows', 'findings', 'dispositions', 'quality_issues', 'coverage', 'validation'):
        out += ['## ' + group.replace('_', ' ').title(), '', '```json', json.dumps(model[group], ensure_ascii=False, indent=2), '```', '']
    out += ['## View traceability', '', '```json', json.dumps(views, ensure_ascii=False, indent=2), '```', '', '## Source ledger', '', '```json', json.dumps(source, ensure_ascii=False, indent=2), '```', '']
    return '\n'.join(out)
