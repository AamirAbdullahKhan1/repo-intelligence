"""Location-normalized comparison only; extra edges are not scored as correct."""
import json
from pathlib import Path

root=Path(__file__).resolve().parents[1]
out=root/'output/research/tsjs-core-reset'
ours=json.loads((root/'output/callback-values-review/gitdiagram-analysis.json').read_text())
jelly=json.loads((out/'jelly-callgraph.json').read_text())
evidence={e['id']:e for e in ours['evidence']}
nodes={n['id']:n for n in ours['entities']}
def position(raw):
    bits=raw.split(':')
    return (jelly['files'][int(bits[0])].replace('\\','/'),int(bits[1]),int(bits[2])) if len(bits)==5 else None
locations={i:position(loc) for i,loc in jelly['functions'].items()}
canonical={}
for n in nodes.values():
    if n['kind']=='symbol':
        cites=[evidence[i] for i in n['evidence_ids'] if evidence[i]['rule']=='symbol-declaration']
        if cites:
            e=cites[0];canonical[n['id']]=(e['file'],e['line'],e['column'])
jelly_pairs={(locations.get(str(a)),locations.get(str(b))) for a,b in jelly['fun2fun']}
jelly_pairs={p for p in jelly_pairs if None not in p}
our_pairs={(canonical.get(e['source']),canonical.get(e['target'])) for e in ours['edges'] if e['kind'] in ('CALLS','CONSTRUCTS','MAY_INVOKE_CALLBACK')}
our_pairs={p for p in our_pairs if None not in p}
shared_positions=set(canonical.values())&set(locations.values())
restricted_ours={p for p in our_pairs if p[0] in shared_positions and p[1] in shared_positions}
restricted_jelly={p for p in jelly_pairs if p[0] in shared_positions and p[1] in shared_positions}
result={'comparison':'Function declaration start positions; no correctness inference or automatic graph merge',
        'common_source_files':len({n['file'] for n in nodes.values() if n['kind']=='file'} & {p.replace('\\','/') for p in jelly['files']}),
        'matched_function_starts':len(set(canonical.values())&set(locations.values())),
        'existing_unique_function_pairs':len(our_pairs),'jelly_unique_function_pairs':len(jelly_pairs),
        'common_pairs':len(our_pairs&jelly_pairs),'existing_only_pairs':len(our_pairs-jelly_pairs),
        'jelly_only_candidate_pairs':len(jelly_pairs-our_pairs)}
result['matched_endpoint_pairs_only']={'existing':len(restricted_ours),'jelly':len(restricted_jelly),
    'common':len(restricted_ours&restricted_jelly),'existing_only':len(restricted_ours-restricted_jelly),
    'jelly_only_candidates':len(restricted_jelly-restricted_ours)}
source_root=root/'output/callback-values-review/source/gitdiagram'
result['existing_only_files']=sorted({n['file'] for n in nodes.values() if n['kind']=='file'}-{p.replace('\\','/') for p in jelly['files']})
result['jelly_only_sample']=[{'source':a,'target':b} for a,b in sorted(restricted_jelly-restricted_ours)[:30]]
(out/'provider-comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='jelly_only_sample'},indent=2))
