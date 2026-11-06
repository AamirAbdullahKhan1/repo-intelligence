import copy
from pathlib import Path
import unittest
from intelligence import VERSION, ledger, validate, diagrams, markdown, extraction_messages
from architecture import projected_graph


def blank():
    return {'schema_version': VERSION, 'entities': [], 'relationships': [], 'workflows': [], 'findings': [], 'dispositions': []}


def record(identity, block, **fields):
    if fields.get('kind') in ('actor', 'component', 'resource', 'operation', 'external_system', 'control', 'data'):
        fields.setdefault('owner_id', None); fields.setdefault('owner_evidence', []); fields.setdefault('vendor_status', 'unspecified')
    return {'id': identity, 'scope': 'Purchase release scope', 'status': 'intended', 'modality': 'unspecified',
            'release': 'current', 'derivation': 'explicit', 'evidence': [{'source_id': block['source_id'], 'quote': block['text']}], **fields}


def purchase_model():
    source = ledger((Path(__file__).parent / 'fixtures/procurement.md').read_text(encoding='utf-8'))
    by_id = {b['requirement_id']: b for b in source['records']}
    a, b, c, d = [by_id[f'REQ-{i:02}'] for i in range(1, 5)]
    proposal = blank()
    proposal['entities'] = [record('employee', a, kind='actor', label='Employee'),
        record('portal', a, kind='component', label='Purchase portal'),
        record('purchases', a, kind='component', label='Purchase Management'),
        record('submit', a, kind='operation', label='Submit purchase', owner_id='purchases', owner_evidence=[{'source_id': a['source_id'], 'quote': 'Purchase Management stores the purchase record.'}]),
        record('records', a, kind='resource', label='Purchase records'),
        record('supplier', d, kind='external_system', label='Supplier service', vendor_status='pending')]
    proposal['relationships'] = [record('e1', a, source='employee', target='portal', type='INTERACTS_WITH', label='Uses portal'),
        record('e2', a, source='portal', target='submit', type='INVOKES', label='Submit purchase'),
        record('e3', a, source='submit', target='records', type='WRITES', label='Stores purchase'),
        record('e4', d, source='purchases', target='supplier', type='INVOKES', label='Release order')]
    refs = [{'source_id': b['source_id'], 'quote': b['text']}]
    proposal['workflows'] = [record('release', b, title='Release purchase', entity_ids=['purchases', 'supplier'], relationship_ids=['e4'],
        inputs='Purchase awaiting review', outputs='Approved order or rejection', human_approval='required',
        automated_validation='unspecified', authorization='Finance approval', failure_handling='If rejected, notify without sending.',
        sequence_basis='explicit', entry_step_ids=['review'], steps=[
            {'id': 'review', 'kind': 'approval', 'label': 'Finance approves', 'entity_id': None, 'evidence': refs},
            {'id': 'send', 'kind': 'action', 'label': 'Send order', 'entity_id': 'purchases', 'approval_requirement': 'required', 'evidence': refs},
            {'id': 'reject', 'kind': 'outcome', 'label': 'Notify employee without order', 'entity_id': None,
             'evidence': [{'source_id': c['source_id'], 'quote': c['text']}]}], transitions=[
            {'id': 'approved', 'source': 'review', 'target': 'send', 'branch': 'success', 'condition': 'Finance approved', 'evidence': refs},
            {'id': 'rejected', 'source': 'review', 'target': 'reject', 'branch': 'failure', 'condition': 'Finance rejects',
             'evidence': [{'source_id': c['source_id'], 'quote': c['text']}]}])]
    for step in proposal['workflows'][0]['steps']:
        step.setdefault('approval_requirement', 'unspecified')
    return proposal, source


class ArchitectureTests(unittest.TestCase):
    def test_operation_paths_roll_up_with_original_evidence(self):
        proposal, source = purchase_model()
        model = validate(proposal, source)
        nodes, edges, _ = projected_graph(model)
        self.assertNotIn('submit', nodes)
        rolled = next(e for e in edges if e['source'] == 'portal' and e['target'] == 'purchases')
        self.assertEqual(rolled['supporting_relationship_ids'], ['e2'])
        self.assertEqual(rolled['supporting_entity_ids'], ['submit'])
        self.assertTrue(rolled['evidence'])
        self.assertIn('submit', {e['id'] for e in model['entities']})
        overview = next(v for v in diagrams(model) if v['id'] == 'overview')
        self.assertEqual(overview['unconnected_entity_ids'], [])
        self.assertIn('supplier', overview['entity_ids'])
        self.assertEqual(nodes['supplier']['vendor_status'], 'pending')

    def test_invalid_ownership_cannot_invent_aggregate(self):
        proposal, source = purchase_model()
        operation = next(e for e in proposal['entities'] if e['id'] == 'submit')
        operation['owner_id'] = 'records'
        model = validate(proposal, source)
        nodes, edges, _ = projected_graph(model)
        self.assertIn('submit', nodes)
        self.assertFalse(any(e['source'] == 'portal' and e['target'] == 'records' for e in edges))
        self.assertTrue(any(q['group'] == 'ownership' for q in model['validation']['quarantined']))

    def test_component_is_connected_through_owned_operation(self):
        proposal, source = purchase_model()
        proposal['relationships'] = [e for e in proposal['relationships'] if e['id'] != 'e4']
        proposal['workflows'] = []
        model = validate(proposal, source)
        self.assertNotIn('purchases', model['coverage']['unconnected_entities'])
        self.assertTrue(any(e['target'] == 'purchases' for e in projected_graph(model)[1]))

    def test_gate_and_rejection_have_distinct_evidenced_paths(self):
        proposal, source = purchase_model()
        model = validate(proposal, source)
        workflow = model['workflows'][0]
        self.assertEqual(workflow['process_status'], 'structurally_valid')
        process = next(v for v in diagrams(model) if v['id'] == 'release')
        self.assertEqual(process['kind'], 'process')
        self.assertIn('failure: Finance rejects', process['source'])
        self.assertIn('success: Finance approved', process['source'])
        self.assertTrue(all(item['evidence'] for item in process['trace']))

    def test_required_approval_bypass_blocks_process_publication(self):
        proposal, source = purchase_model()
        workflow = proposal['workflows'][0]
        extra = copy.deepcopy(workflow['steps'][1]); extra.update(id='start', label='Request release')
        workflow['steps'].append(extra)
        workflow['entry_step_ids'].append('start')
        bypass = copy.deepcopy(workflow['transitions'][0]); bypass.update(id='bypass', source='start', target='send')
        workflow['transitions'].append(bypass)
        model = validate(proposal, source)
        self.assertIn('approval_bypass', [q['code'] for q in model['quality_issues']])
        view = next(v for v in diagrams(model) if v['id'] == 'release')
        self.assertEqual(view['kind'], 'interactions')
        self.assertIn('approval_bypass', view['process_not_compiled_reasons'])

    def test_gate_check_uses_structured_action_scope_not_only_english_labels(self):
        proposal, source = purchase_model()
        workflow = proposal['workflows'][0]
        workflow['steps'][1]['label'] = '发送订单'
        start = copy.deepcopy(workflow['steps'][1]); start.update(id='start', label='开始', approval_requirement='unspecified')
        workflow['steps'].append(start)
        workflow['entry_step_ids'].append('start')
        bypass = copy.deepcopy(workflow['transitions'][0]); bypass.update(id='bypass', source='start', target='send')
        workflow['transitions'].append(bypass)
        model = validate(proposal, source)
        self.assertIn('approval_bypass', [q['code'] for q in model['quality_issues']])

    def test_invalid_step_or_transition_not_accepted_as_process(self):
        proposal, source = purchase_model()
        proposal['workflows'][0]['transitions'][0]['evidence'][0]['quote'] = 'Approve an invented payment'
        model = validate(proposal, source)
        self.assertIn('invalid_transition', [q['code'] for q in model['quality_issues']])
        self.assertFalse(any(v['kind'] == 'process' and v['id'] == 'release' for v in diagrams(model)))

    def test_missing_action_approval_classification_cannot_be_published_as_a_process(self):
        proposal, source = purchase_model()
        del proposal['workflows'][0]['steps'][1]['approval_requirement']
        model = validate(proposal, source)
        self.assertIn('invalid_step', [q['code'] for q in model['quality_issues']])
        self.assertFalse(any(v['kind'] == 'process' and v['id'] == 'release' for v in diagrams(model)))

    def test_partial_clause_reference_is_not_complete_understanding(self):
        source = ledger('REQ-01: Users submit a request. Failed submissions must preserve the original reference.')
        proposal = blank()
        entity = record('portal', source['records'][0], kind='component', label='Portal')
        entity['evidence'][0]['quote'] = 'Users submit a request'
        proposal['entities'] = [entity]
        model = validate(proposal, source)
        self.assertEqual(model['coverage']['referenced_blocks'], 1)
        self.assertTrue(any(u['quotation_coverage'] == 'not_quoted' for u in model['coverage']['clause_units']))
        self.assertTrue(all(u['semantic_status'] == 'not_assessed' for u in model['coverage']['clause_units']))

    def test_varied_text_formats_and_domains_preserve_nonblank_content(self):
        fixtures = Path(__file__).parent / 'fixtures'
        for path in fixtures.iterdir():
            with self.subTest(fixture=path.name):
                text = path.read_text(encoding='utf-8')
                source = ledger(text)
                self.assertTrue(source['records'])
                for block in source['records']:
                    self.assertEqual(block['text'], '\n'.join(text.splitlines()[block['start_line'] - 1:block['end_line']]))
                covered = {number for block in source['records'] for number in range(block['start_line'], block['end_line'] + 1)}
                self.assertTrue(all(number in covered for number, line in enumerate(text.splitlines(), 1) if line.strip()))
                # No fixed architecture is injected for a new business domain.
                self.assertEqual(diagrams(validate(blank(), source)), [])
        table = ledger((fixtures / 'warehouse-table.md').read_text())
        self.assertIn('WMS-04', {b['requirement_id'] for b in table['records']})
        clinic = ledger((fixtures / 'clinic.txt').read_text())
        self.assertGreaterEqual(len(clinic['records']), 7)

    def test_requires_is_mandatory_cue_and_scope_conflict_is_reviewable(self):
        source = ledger('Storage requires asynchronous job state.\n\nThe pilot covers 20 users. A planning estimate covers 200 production users.')
        self.assertIn('mandatory', source['records'][0]['cues'])
        proposal = blank()
        proposal['findings'] = [record('scope', source['records'][1], kind='conflict', title='Workload difference',
                                      description='Different workload numbers.', status='contradictory')]
        model = validate(proposal, source)
        self.assertIn('scope_difference', [q['code'] for q in model['quality_issues']])
        self.assertEqual(model['findings'][0]['status'], 'contradictory')  # no silent resolution

    def test_prompt_omits_redundant_hashes_but_keeps_every_block(self):
        source = ledger('REQ-01: A clinic shall book appointments.')
        prompt = extraction_messages('skill', source, 'repository-analysis')
        import json
        sent = json.loads(prompt[1]['content'])['source_ledger']['records']
        self.assertEqual(len(sent), len(source['records']))
        self.assertEqual(sent[0]['text'], source['records'][0]['text'])
        self.assertNotIn('text_sha256', sent[0])

    def test_normative_heading_is_not_lost(self):
        source = ledger('# REQ-99 All stored records must be encrypted\n\n## Purpose\nThis is a records application.')
        self.assertEqual(source['records'][0]['requirement_id'], 'REQ-99')
        self.assertIn('mandatory', source['records'][0]['cues'])
        self.assertEqual(source['records'][0]['kind'], 'heading')

    def test_short_unicode_role_evidence_is_not_rejected_by_english_length_rule(self):
        source = ledger('员工')
        proposal = blank()
        proposal['entities'] = [record('employee', source['records'][0], kind='actor', label='员工')]
        model = validate(proposal, source)
        self.assertEqual(len(model['entities']), 1)
        self.assertEqual(model['validation']['quarantined'], [])

    def test_new_contract_does_not_silently_accept_missing_entity_fields(self):
        proposal, source = purchase_model()
        del proposal['entities'][0]['vendor_status']
        model = validate(proposal, source)
        self.assertNotIn('employee', {e['id'] for e in model['entities']})
        self.assertTrue(any('2.1 entity contract' in q['reason'] for q in model['validation']['quarantined']))

    def test_summary_does_not_embed_entire_audit_register(self):
        proposal, source = purchase_model()
        model = validate(proposal, source)
        output = markdown(model, source, 'repository-analysis', diagrams(model))
        self.assertIn('Major logical responsibilities', output)
        self.assertNotIn('```json', output)
        self.assertIn('not semantic completeness', output)


if __name__ == '__main__':
    unittest.main()
