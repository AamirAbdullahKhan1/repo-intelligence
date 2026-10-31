"""Synthetic regressions for actual extractor/projection behavior, no target execution."""
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from types import SimpleNamespace
from app.evidence.validation import validate
from app.graph.projections import project
SCRIPT = Path(__file__).resolve().parents[1] / 'workers/typescript/index.cjs'
coordinator = SimpleNamespace(validate=validate, project=project)

class StaticPocTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.root = Path(cls.temp.name)
        sources = {
            'package.json': '{"name":"sample","dependencies":{"openai":"test"}}',
            'tsconfig.json': '{"compilerOptions":{"paths":{"~/*":["src/*"]},"plugins":[{"name":"NEVER_RUN"}]}}',
            'src/store.ts': 'export function save() { return 1; }',
            'src/types.ts': 'export interface User { name: string }',
            'src/barrel.ts': 'export { save as persist } from "./store";',
            'src/main.ts': '''
import {persist as write} from '~/barrel';
import absent from './does-not-exist';
import OpenAI from 'openai';
import { type User } from './types';
interface Port { send(): void }
export function run(port: Port) { write(); port.send(); }
function fetch(value: string) { return value; }
fetch('https://not-a-remote-call.test/');
const unusedEndpoint = 'https://unused-config.test/';
const client = new OpenAI();
client.responses.create({});
let uncertain = new OpenAI();
uncertain = absent();
uncertain.responses.create({});
''',
            'src/network.ts': 'export function request() { return fetch("https://api.example.test/v1"); }',
            'src/app/api/users/route.ts': '''
// export function DELETE() { return 'fake' }
export function GET() { return 'ok' }
const example = "export function POST() {}";
''',
            'src/helper.test.ts': 'throw new Error("TARGET MUST NOT EXECUTE"); fetch("https://excluded.test");',
            'src/test-redis.ts': 'fetch("https://test-helper.test");',
            'wrangler.jsonc': '{"name":"site","main":"src/main.ts","services":[{"binding":"API","service":"api"}]}',
            'wrangler.api.jsonc': '{"name":"api","main":"src/network.ts"}',
        }
        for name, text in sources.items():
            target=cls.root/name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(text, encoding='utf-8')
        process=subprocess.run(['node',str(SCRIPT),str(cls.root)],capture_output=True,encoding='utf-8',check=True,timeout=45)
        cls.graph=json.loads(process.stdout)
        cls.entities={e['id']:e for e in cls.graph['entities']}
        cls.evidence={e['id']:e for e in cls.graph['evidence']}

    @classmethod
    def tearDownClass(cls):
        cls.temp.cleanup()

    def test_alias_reexport_resolves_implementation(self):
        calls=[e for e in self.graph['edges'] if e['kind']=='CALLS']
        self.assertTrue(any(self.entities[e['target']]['label']=='save' and self.entities[e['target']]['file']=='src/store.ts' for e in calls))

    def test_signature_not_promoted_to_implementation(self):
        self.assertFalse(any(e['kind']=='CALLS' and self.entities[e['target']]['label']=='send' for e in self.graph['edges']))
        self.assertTrue(any(u['reason'].startswith('signature only') for u in self.graph['unknowns']))

    def test_unresolved_import_not_automatically_external(self):
        self.assertTrue(any(u.get('specifier')=='./does-not-exist' for u in self.graph['unknowns']))
        self.assertFalse(any(e['label']=='./does-not-exist' for e in self.graph['entities']))

    def test_named_type_only_import_not_runtime_dependency(self):
        links=[e for e in self.graph['edges'] if self.entities[e['target']].get('file')=='src/types.ts' and e['kind'] in ('IMPORTS','TYPE_REFERENCES','REEXPORTS')]
        self.assertEqual([e['kind'] for e in links],['TYPE_REFERENCES'])

    def test_http_shadowing_unused_config_and_tests(self):
        hosts={e['label'] for e in self.graph['entities'] if e['kind']=='external_service'}
        self.assertIn('api.example.test',hosts)
        for host in ('not-a-remote-call.test','unused-config.test','excluded.test','test-helper.test'):
            self.assertNotIn(host,hosts)

    def test_comments_and_strings_do_not_register_routes(self):
        self.assertEqual([(r['method'],r['path']) for r in self.graph['routes']],[('GET','/api/users')])

    def test_sdk_requires_bound_receiver(self):
        calls=[e for e in self.graph['edges'] if e['kind']=='SDK_API_CALL']
        self.assertEqual(len(calls),1, 'Unresolved reassignment must not become a proven SDK receiver')

    def test_config_target_merges_actual_entry(self):
        api=next(e for e in self.graph['entities'] if e['kind']=='deployable' and e['label']=='api')
        self.assertEqual(api['entry'],'src/network.ts')
        self.assertTrue(any(e['kind']=='BINDS_SERVICE' for e in self.graph['edges']))

    def test_grounding_and_projection(self):
        coordinator.validate(self.graph,self.root)
        views=coordinator.project(self.graph)
        ids={n['id'] for n in views['overview']['nodes']}
        self.assertTrue(all(e['source'] in ids and e['target'] in ids for e in views['overview']['edges']))
        bad=json.loads(json.dumps(self.graph))
        bad['edges'][0]['target']='missing'
        with self.assertRaises(ValueError): coordinator.validate(bad,self.root)
        bad=json.loads(json.dumps(self.graph))
        bad['evidence'][0]['column']+=1
        with self.assertRaises(ValueError): coordinator.validate(bad,self.root)

    def test_stable_rerun(self):
        process=subprocess.run(['node',str(SCRIPT),str(self.root)],capture_output=True,encoding='utf-8',check=True,timeout=45)
        self.assertEqual(self.graph,json.loads(process.stdout))


if __name__=='__main__':
    unittest.main()
