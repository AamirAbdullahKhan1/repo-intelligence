import json
from pathlib import Path
import tempfile
import unittest
from reprocess import reprocess
from intelligence import VERSION, ledger


class ReprocessTests(unittest.TestCase):
    def test_revalidation_preserves_parent_and_makes_no_model_calls(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory); parent_id = 'a' * 32; parent = root / 'results' / parent_id; parent.mkdir(parents=True)
            source = ledger('No AI capability is requested.')
            proposal = {'schema_version': VERSION, 'entities': [], 'relationships': [], 'workflows': [], 'findings': [], 'dispositions': []}
            original = {'id': parent_id, 'status': 'completed', 'skill': 'ai-usage-inventory', 'filename': 'noai.md',
                        'created_at': '2026-11-06', 'duration_seconds': 45, 'usage': {'total_tokens': 123}, 'input_sha256': source['input_sha256']}
            for name, data in (('result.json', original), ('source-ledger.json', source), ('inventory-proposal.txt', proposal)):
                (parent / name).write_text(json.dumps(data), encoding='utf-8')
            before = (parent / 'result.json').read_bytes()
            result = reprocess(root, parent_id)
            self.assertNotEqual(result['id'], parent_id)
            self.assertEqual(result['usage']['total_tokens'], 0)
            self.assertEqual(result['original_analysis_usage']['total_tokens'], 123)
            self.assertEqual(result['reprocess_of'], parent_id)
            self.assertEqual((parent / 'result.json').read_bytes(), before)
            self.assertTrue((root / 'results' / result['id'] / 'audit-report.md').exists())

    def test_path_traversal_and_legacy_or_changed_snapshots_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError): reprocess(directory, '../other')
            parent = Path(directory) / 'results' / ('b' * 32); parent.mkdir(parents=True)
            for name, data in (('result.json', {'status': 'completed', 'input_sha256': 'different'}),
                               ('source-ledger.json', {'input_sha256': 'original'}),
                               ('inventory-proposal.txt', {'schema_version': '2.0'})):
                (parent / name).write_text(json.dumps(data), encoding='utf-8')
            with self.assertRaisesRegex(ValueError, 'matching source snapshot'):
                reprocess(directory, 'b' * 32)
