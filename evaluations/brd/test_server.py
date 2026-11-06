import importlib.util
import json
import os
from pathlib import Path
import tempfile
import io
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).parent))
spec = importlib.util.spec_from_file_location('brd_server', Path(__file__).with_name('server.py'))
server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(server)


class RunnerTests(unittest.TestCase):
    def test_independent_skills_and_no_evaluator_leak(self):
        for skill in server.SKILLS:
            instructions, prompt = server.messages(skill, 'REQ-01: Search knowledge.\nNo vendor selected.')
            self.assertIn('name: ' + skill, instructions)
            self.assertIn('L2: No vendor selected.', prompt[1]['content'])
            self.assertNotIn('Expected findings', json.dumps(prompt))
            self.assertEqual(len(prompt), 2)
        with self.assertRaises(ValueError):
            server.messages('../evaluator', 'text')

    def test_url_and_rejected_credential_redirect_targets(self):
        cfg = {'endpoint': 'https://sample.openai.azure.com/', 'deployment': 'GPT 4.1/test', 'api_version': '2025-03-01-preview'}
        self.assertIn('/GPT%204.1%2Ftest/chat/completions?', server.completion_url(cfg))
        for endpoint in ('http://sample.openai.azure.com', 'https://example.com', 'https://user:pass@sample.openai.azure.com', 'https://sample.openai.azure.com/other'):
            with self.assertRaises(ValueError):
                server.completion_url({**cfg, 'endpoint': endpoint})

    def test_citation_checks_do_not_claim_semantic_validation(self):
        result = server.checks('Claim [L1-L2]. Bad [L0-L3].\n```mermaid\nflowchart LR\nA --> B\n```', 'one\ntwo', 'length')
        self.assertEqual(result['invalid_line_ranges'], ['L0-L3'])
        self.assertEqual(result['diagram_count'], 1)
        self.assertTrue(result['partial'])
        self.assertIn('require review', result['scope'])

    def test_saved_result_and_failure_without_network(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            skill = root / 'skills/repository-analysis'
            skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('test instructions', encoding='utf-8')
            proposal = json.dumps({'schema_version': '2.1', 'entities': [], 'relationships': [], 'workflows': [], 'findings': [], 'dispositions': []})
            with patch.object(server, 'ROOT', root), patch.object(server, 'call_azure', return_value=(proposal, {'total_tokens': 20}, 'stop', 'test-model')):
                server.BUSY.acquire()
                server.run_job('abc', 'repository-analysis', 'Requirement', 'test.md')
                saved = json.loads((root / 'results/abc/result.json').read_text())
                self.assertEqual(saved['status'], 'completed')
                self.assertEqual(saved['usage']['total_tokens'], 40)
                self.assertEqual(len(saved['stage_usage']), 2)
                self.assertNotIn('api_key', json.dumps(saved))
                self.assertTrue((root / 'results/abc/report.md').exists())
                self.assertTrue((root / 'results/abc/intelligence-model.json').exists())
                self.assertEqual(saved['runner_version'], '2.1')
            with patch.object(server, 'call_azure', side_effect=ValueError('API key is missing.')):
                server.BUSY.acquire()
                server.run_job('failure', 'repository-analysis', 'text', 'test.md')
                self.assertEqual(server.JOBS['failure']['status'], 'failed')

    def test_missing_key_stops_before_network(self):
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': ''}), patch.object(server, 'load_env'):
            with self.assertRaisesRegex(ValueError, 'API key is missing'):
                server.call_azure(server.config(), [])

    def test_truncated_or_invalid_model_is_not_published(self):
        for raw, finish in (('{"schema_version":', 'length'), ('Not JSON', 'stop')):
            with self.subTest(finish=finish), tempfile.TemporaryDirectory() as folder:
                root = Path(folder)
                skill = root / 'skills/repository-analysis'
                skill.mkdir(parents=True)
                (skill / 'SKILL.md').write_text('test instructions', encoding='utf-8')
                with patch.object(server, 'ROOT', root), patch.object(server, 'call_azure', return_value=(raw, {}, finish, 'test-model')):
                    server.BUSY.acquire()
                    server.run_job('incomplete', 'repository-analysis', 'Requirement', 'test.md')
                    self.assertEqual(server.JOBS['incomplete']['status'], 'failed')
                    self.assertFalse((root / 'results/incomplete/report.md').exists())
                    self.assertTrue((root / 'results/incomplete/proposal.txt').exists())
                    self.assertTrue((root / 'results/incomplete/failure.json').exists())

    def test_ai_absence_does_not_force_a_second_model_call_or_diagram(self):
        proposal = {'schema_version': '2.1', 'entities': [], 'relationships': [], 'workflows': [], 'dispositions': [],
            'findings': [{'id': 'absence', 'kind': 'observation', 'title': 'No AI specified',
                'description': 'The supplied input specifies no AI.', 'scope': 'Supplied BRD only', 'status': 'unspecified',
                'modality': 'unspecified', 'release': 'unspecified', 'derivation': 'explicit',
                'evidence': [{'source_id': 'S00001', 'quote': 'No AI capability is requested.'}]}]}
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder); skill = root / 'skills/ai-usage-inventory'; skill.mkdir(parents=True)
            (skill / 'SKILL.md').write_text('AI requirements only', encoding='utf-8')
            with patch.object(server, 'ROOT', root), patch.object(server, 'call_azure', return_value=(json.dumps(proposal), {'total_tokens': 20}, 'stop', 'test-model')) as call:
                server.BUSY.acquire()
                server.run_job('noai', 'ai-usage-inventory', 'No AI capability is requested.', 'no-ai.md')
                saved = server.JOBS['noai']
                self.assertEqual(saved['status'], 'completed')
                self.assertEqual(call.call_count, 1)
                self.assertEqual(saved['views'], [])
                self.assertIn('AI requirement assessment', saved['report'])
                self.assertNotIn('audit_report', saved)  # large appendix is fetched separately
                self.assertTrue((root / 'results/noai/audit-report.md').exists())

    def test_request_guards_and_missing_key_response(self):
        def request(body, token=server.TOKEN, host='127.0.0.1:8766'):
            handler = object.__new__(server.Handler)
            payload = json.dumps(body).encode()
            handler.headers = {'Host': host, 'X-Session-Token': token, 'Content-Length': str(len(payload))}
            handler.server = SimpleNamespace(server_port=8766)
            handler.path = '/api/runs'
            handler.rfile = io.BytesIO(payload)
            captured = []
            handler.send = lambda status, value: captured.append((status, value))
            handler.do_POST()
            return captured[0]
        body = {'text': 'Requirement', 'skill': 'repository-analysis', 'consent': True}
        self.assertEqual(request(body, token='bad')[0], 403)
        self.assertEqual(request(body, host='evil.example')[0], 403)
        self.assertEqual(request({**body, 'text': 'x' * (server.MAX_INPUT + 1)})[0], 400)
        self.assertEqual(request({**body, 'consent': False})[0], 400)
        with patch.dict(os.environ, {'AZURE_OPENAI_API_KEY': ''}), patch.object(server, 'load_env'):
            status, data = request(body)
            self.assertEqual(status, 400)
            self.assertIn('AZURE_OPENAI_API_KEY', data['error'])


if __name__ == '__main__':
    unittest.main()
