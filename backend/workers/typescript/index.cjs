/* Trusted analyzer only: target files are parsed, never required, imported or emitted. */
'use strict';
require('./guard.cjs');
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const ts = require('typescript');
const root = fs.realpathSync(process.argv[2] || '.');
const LIMITS = { files: 4000, bytes: 32 * 1024 * 1024, fileBytes: 1200000, records: 150000 };
const digest = s => crypto.createHash('sha256').update(s).digest('hex');
const id = (kind, key) => `${kind}:${digest(key).slice(0, 20)}`;
const rel = p => path.relative(root, p).split(path.sep).join('/');
const contained = p => { const r = path.relative(root, path.resolve(p)); return !r.startsWith('..') && !path.isAbsolute(r); };
const excluded = new Set(['.git', 'node_modules', '.next', '.open-next', '.open-next-history', '.venv', 'dist', 'build', '__pycache__']);
const inventory = [], skips = [], texts = new Map();
let bytes = 0;
function walk(dir) {
  for (const entry of fs.readdirSync(dir, { withFileTypes: true }).sort((a,b) => a.name.localeCompare(b.name, 'en'))) {
    const p = path.join(dir, entry.name), r = rel(p);
    if (entry.isSymbolicLink()) { skips.push({ file: r, reason: 'symlink' }); continue; }
    if (entry.isDirectory()) {
      if (excluded.has(entry.name)) { skips.push({ file: r, reason: 'generated/vendor directory' }); continue; }
      walk(p); continue;
    }
    if (!entry.isFile()) { skips.push({ file:r, reason:'special file' }); continue; }
    if (inventory.length >= LIMITS.files) throw Error('File-count limit reached; no complete result published');
    const size = fs.statSync(p).size;
    inventory.push({ path:r, size });
    const relevant = /\.(?:[cm]?[jt]sx?|jsonc?)$/.test(r) || /(?:^|\/)(?:Dockerfile|Procfile)$/.test(r);
    if (!relevant) continue;
    if (/(?:^|\/)(?:experiments|public|docs|scripts|plugins)(?:\/|$)/.test(r) || /(?:\.test\.|\.spec\.|\.fixture\.|\/__tests__\/|\/test\/|\/test-[^/]+$)/.test(r)) {
      skips.push({ file:r, reason:'test/tooling/assets scope' }); continue;
    }
    if (size > LIMITS.fileBytes) { skips.push({file:r, reason:'per-file byte limit'}); continue; }
    bytes += size;
    if (bytes > LIMITS.bytes) throw Error('Total parsed-byte limit reached');
    texts.set(path.resolve(p), fs.readFileSync(p, 'utf8'));
  }
}
walk(root);
const json = p => {
  const text = texts.get(path.resolve(p));
  if (text === undefined) return null;
  const result = ts.parseConfigFileTextToJson(rel(p), text);
  if (result.error) return null;
  return result.config;
};
const files = [...texts.keys()].filter(p => /\.[cm]?[jt]sx?$/.test(p));
const entities = [], edges = [], evidence = [], diagnostics = [], routes = [], unknowns = [];
const entityMap = new Map(), edgeMap = new Map(), evMap = new Map();
function entity(kind, key, label, extra={}) {
  const eid = id(kind,key);
  if (!entityMap.has(eid)) { const e={id:eid,kind,label,...extra}; entityMap.set(eid,e); entities.push(e); }
  else {
    const current=entityMap.get(eid);
    for(const [k,v] of Object.entries(extra))if(current[k]===undefined)current[k]=v;
    if(extra.evidence_ids)current.evidence_ids=[...new Set([...(current.evidence_ids||[]),...extra.evidence_ids])];
  }
  return eid;
}
function ev(sf, node, rule, origin='source_code') {
  const start=node.getStart(sf), end=node.end, at=sf.getLineAndCharacterOfPosition(start), to=sf.getLineAndCharacterOfPosition(end);
  const key=`${rel(sf.fileName)}:${start}:${end}:${rule}`, eid=id('evidence',key);
  if (!evMap.has(eid)) {
    const e={id:eid,file:rel(sf.fileName),start,end,line:at.line+1,column:at.character+1,end_line:to.line+1,end_column:to.character+1,
      column_encoding:'utf16',rule,origin,sha256:digest(texts.get(path.resolve(sf.fileName)) || sf.text)};
    evMap.set(eid,e); evidence.push(e);
  }
  return eid;
}
function edge(source,target,kind,support,extra={}) {
  const key=[source,target,kind,extra.callsite || '',extra.profile || 'source'].join('|');
  if (!edgeMap.has(key)) {
    const e={id:id('edge',key),source,target,kind,resolution:'resolved',grounding:'passed',evidence_ids:[...new Set(support)],...extra};
    edgeMap.set(key,e); edges.push(e);
    if (edges.length > LIMITS.records) throw Error('Record limit reached');
  }
  return edgeMap.get(key);
}
const packages = [];
for (const p of texts.keys()) if (path.basename(p)==='package.json') {
  const data=json(p); if (!data) continue;
  const base=rel(path.dirname(p));
  const sf=ts.createSourceFile(p,texts.get(p),ts.ScriptTarget.Latest,true,ts.ScriptKind.JSON);
  const eid=entity('application',base||'.',data.name || 'Source root', {root:base||'.',technology:data.dependencies?.next?'Next.js package':data.dependencies?.react?'React package':'JS/TS package',boundary:'package; deployment not implied',evidence_ids:[ev(sf,sf,'package-boundary','manifest')]});
  packages.push({root:base||'.',id:eid,data});
}
if (!packages.some(p=>p.root==='.')) {
  const eid=entity('application','.','Source root',{root:'.',boundary:'source root candidate',evidence_ids:[]}); packages.push({root:'.',id:eid,data:{}});
}
packages.sort((a,b)=>b.root.length-a.root.length);
function owner(r) { return packages.find(p=>p.root==='.' || r.startsWith(p.root+'/')); }
const fileIds=new Map(), componentIds=new Map();
function component(r) {
  const pkg=owner(r), local=pkg.root==='.' ? r : r.slice(pkg.root.length+1), parts=local.split('/');
  let group=parts.slice(0,-1).join('/') || '.';
  if (parts[0]==='src' && parts[1]==='server') group=parts.length>3 ? parts.slice(0,3).join('/') : 'src/server';
  else if (parts[0]==='src') group=parts.slice(0,Math.min(parts.length-1,2)).join('/');
  else if (parts[0]==='cloudflare') group='cloudflare';
  const key=pkg.root+'::'+group;
  if (!componentIds.has(key)) {
    const label=group==='.' ? pkg.data.name || 'Root module' : group.replace(/^src\//,'').replace(/^server\//,'').split('/').join(' / ');
    const eid=entity('component',key,label,{application_id:pkg.id,root:pkg.root,group,projection_rule:'directory ownership, logical component only',evidence_ids:[]});
    componentIds.set(key,eid);
  }
  return componentIds.get(key);
}
const config=json(path.join(root,'tsconfig.json')) || {};
const options={allowJs:true,checkJs:false,noEmit:true,skipLibCheck:true,types:[],target:ts.ScriptTarget.ES2022,
  module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,jsx:ts.JsxEmit.Preserve,
  baseUrl:root,paths:config.compilerOptions?.paths || {}};
// Only explicitly supplied text and trusted compiler standard libraries are visible.
const libRoot=path.dirname(ts.getDefaultLibFilePath(options));
const trustedLib=p=>path.dirname(path.resolve(p))===libRoot && /^lib\..*\.d\.ts$/.test(path.basename(p));
const host=ts.createCompilerHost(options);
const oldRead=host.readFile;
host.readFile=p=>texts.get(path.resolve(p)) ?? (trustedLib(p) ? oldRead(p) : undefined);
host.fileExists=p=>texts.has(path.resolve(p)) || (trustedLib(p)&&fs.existsSync(p));
host.directoryExists=p=>[...texts.keys()].some(f=>f.startsWith(path.resolve(p)+path.sep)) || path.resolve(p)===libRoot;
host.realpath=p=>path.resolve(p);
host.getCurrentDirectory=()=>root;
host.getSourceFile=(p,version)=>{const t=host.readFile(p); return t===undefined ? undefined : ts.createSourceFile(p,t,version,true);};
host.writeFile=()=>{throw Error('Emission is prohibited');};
const program=ts.createProgram(files,options,host), checker=program.getTypeChecker();
const sources=program.getSourceFiles().filter(s=>texts.has(path.resolve(s.fileName)) && files.includes(path.resolve(s.fileName)));
const importBindings=new Map(), assignments=new Map(), originCache=new Map();
function symbol(n) { try { return checker.getSymbolAtLocation(n); } catch {return null;} }
function unwrap(n) { while(n&&(ts.isAwaitExpression(n)||ts.isParenthesizedExpression(n)||ts.isAsExpression(n)||ts.isNonNullExpression(n)||ts.isTypeAssertionExpression(n))) n=n.expression; return n; }
function pkgName(s) { return s.startsWith('@') ? s.split('/').slice(0,2).join('/') : s.split('/')[0]; }
function declared(p,s) { return !!(p.data.dependencies?.[pkgName(s)] || p.data.devDependencies?.[pkgName(s)]); }
function isExternal(spec,p) { return !spec.startsWith('.')&&!spec.startsWith('/')&&!Object.keys(options.paths).some(k=>spec.startsWith(k.replace('*',''))) && (declared(p,spec)||spec.startsWith('node:')); }
function localTarget(spec,sf) { return ts.resolveModuleName(spec,sf.fileName,options,host).resolvedModule?.resolvedFileName; }
function symbolEntity(decl) {
  if (!decl || !texts.has(path.resolve(decl.getSourceFile().fileName))) return null;
  const sf=decl.getSourceFile(), r=rel(sf.fileName), name=decl.name?.getText(sf) || (ts.isArrowFunction(decl)&&decl.parent?.name?.getText(sf)) || '<anonymous>';
  const sid=entity('symbol',`${r}:${decl.getStart(sf)}:${name}`,name,{file:r,component_id:component(r),application_id:owner(r).id,
    declaration_kind:ts.SyntaxKind[decl.kind],has_body:!!decl.body,evidence_ids:[ev(sf,decl,'symbol-declaration')]});
  const fid=entity('file',r,r,{file:r,component_id:component(r),application_id:owner(r).id,evidence_ids:[]});
  edge(sid,fid,'DEFINED_IN',[ev(sf,decl,'symbol-declaration')],{derivation:'source membership, not a call'});
  return sid;
}
function enclosing(n) { let p=n.parent; while(p) {if(ts.isFunctionLike(p)&&p.body) return symbolEntity(p); p=p.parent;} return fileIds.get(rel(n.getSourceFile().fileName)); }
// Pass one: ownership, imports, definitions and assignments. Target code never executes.
for (const sf of sources) {
  const r=rel(sf.fileName), fid=entity('file',r,r,{file:r,component_id:component(r),application_id:owner(r).id,evidence_ids:[ev(sf,sf,'source-file')]}); fileIds.set(r,fid);
  const comp=entityMap.get(component(r)); if(!comp.evidence_ids.length) comp.evidence_ids=[ev(sf,sf,'component-membership')];
  if (sf.parseDiagnostics.length) diagnostics.push({file:r,kind:'parse',count:sf.parseDiagnostics.length});
  const visit=n=>{
    if(ts.isImportDeclaration(n)&&ts.isStringLiteral(n.moduleSpecifier)) {
      const spec=n.moduleSpecifier.text, support=ev(sf,n,'import-statement'), target=localTarget(spec,sf), external=isExternal(spec,owner(r));
      const bindings=[]; const clause=n.importClause;
      if(clause?.name) bindings.push([clause.name,'default',!!clause.isTypeOnly]);
      if(clause?.namedBindings) {
        if(ts.isNamespaceImport(clause.namedBindings)) bindings.push([clause.namedBindings.name,'*',!!clause.isTypeOnly]);
        else for(const x of clause.namedBindings.elements) bindings.push([x.name,x.propertyName?.text||x.name.text,!!clause.isTypeOnly||!!x.isTypeOnly]);
      }
      for(const [b,name,typeOnly] of bindings) {const s=symbol(b); if(s)importBindings.set(s,{package:spec,name,evidence:[support],instance:false,typeOnly});}
      const targetId=target&&contained(target)&&texts.has(path.resolve(target)) ? entity('file',rel(target),rel(target),{file:rel(target),component_id:component(rel(target)),application_id:owner(rel(target)).id,evidence_ids:[]}) : external ? entity('dependency',pkgName(spec),pkgName(spec),{scope:'external',evidence_ids:[support]}) : null;
      const onlyTypes=clause?.isTypeOnly || bindings.length>0&&bindings.every(b=>b[2]);
      if(targetId) edge(fid,targetId,onlyTypes?'TYPE_REFERENCES':'IMPORTS',[support],{specifier:spec,target_scope:external?'external':'internal'});
      else unknowns.push({kind:'import',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:'local/generated/undeclared target unavailable',specifier:spec,evidence_ids:[support]});
    }
    if(ts.isExportDeclaration(n)&&n.moduleSpecifier&&ts.isStringLiteral(n.moduleSpecifier)) {
      const target=localTarget(n.moduleSpecifier.text,sf);
      if(target&&contained(target)&&texts.has(path.resolve(target)))edge(fid,entity('file',rel(target),rel(target),{file:rel(target),component_id:component(rel(target)),application_id:owner(rel(target)).id,evidence_ids:[]}),n.isTypeOnly?'TYPE_REFERENCES':'REEXPORTS',[ev(sf,n,'re-export')]);
    }
    if(ts.isFunctionLike(n)&&n.body || ts.isClassDeclaration(n)||ts.isInterfaceDeclaration(n)) {
      const sid=symbolEntity(n);let parent=n.parent;
      while(parent&&!ts.isFunctionLike(parent))parent=parent.parent;
      if(parent?.body&&sid)edge(symbolEntity(parent),sid,'CONTAINS_SYMBOL',[ev(sf,n,'lexical-function-membership')],{resolution:'conditional',derivation:'lexical containment only; invocation not established'});
    }
    if(ts.isBinaryExpression(n)&&[ts.SyntaxKind.EqualsToken,ts.SyntaxKind.QuestionQuestionEqualsToken,ts.SyntaxKind.BarBarEqualsToken].includes(n.operatorToken.kind)) {
      const s=symbol(n.left); if(s) {const a=assignments.get(s)||[];a.push(n.right);assignments.set(s,a);}
    }
    ts.forEachChild(n,visit);
  }; visit(sf);
  require('./adapters/next.cjs')({ts,r,sf,fid,ev,entity,edge,owner,component,symbolEntity,routes});
}
function resolveOrigin(raw,depth=0,seen=new Set()) {
  const n=unwrap(raw); if(!n||depth>9)return null;
  if(ts.isIdentifier(n)) {
    const s=symbol(n);if(!s||seen.has(s))return null;
    if(importBindings.has(s))return importBindings.get(s);
    const next=new Set(seen);next.add(s);
    const values=[];
    for(const d of s.declarations||[]) {
      if(ts.isVariableDeclaration(d)&&d.initializer)values.push(d.initializer);
      if(ts.isBindingElement(d)&&ts.isVariableDeclaration(d.parent?.parent)&&d.parent.parent.initializer)values.push(d.parent.parent.initializer);
    }
    values.push(...(assignments.get(s)||[]));
    const effective=values.filter(x=>x.kind!==ts.SyntaxKind.NullKeyword && !(ts.isIdentifier(x)&&x.text==='undefined'));
    const os=effective.map(x=>resolveOrigin(x,depth+1,next)).filter(Boolean);
    if(os.length===effective.length&&os.length&&new Set(os.map(x=>x.package)).size===1)return {...os[0],evidence:[...new Set(os.flatMap(x=>x.evidence))]};
  }
  if(ts.isPropertyAccessExpression(n))return resolveOrigin(n.expression,depth+1,seen);
  if(ts.isNewExpression(n)) {
    const o=resolveOrigin(n.expression,depth+1,seen);if(o)return {...o,instance:true,evidence:[...o.evidence,ev(n.getSourceFile(),n,'bound-client-constructor')]};
  }
  if(ts.isCallExpression(n)) {
    if(n.expression.kind===ts.SyntaxKind.ImportKeyword&&ts.isStringLiteral(n.arguments[0]))return {package:n.arguments[0].text,name:'*',instance:false,evidence:[ev(n.getSourceFile(),n,'dynamic-import-literal')]};
    const target=checker.getResolvedSignature(n)?.declaration;
    if(target?.body&&texts.has(path.resolve(target.getSourceFile().fileName))) {
      if(originCache.has(target))return originCache.get(target);
      originCache.set(target,null);const returns=[];
      function find(x){if(x!==target&&ts.isFunctionLike(x))return;if(ts.isReturnStatement(x)&&x.expression)returns.push(x.expression);ts.forEachChild(x,find);}
      find(target);
      const os=returns.map(x=>resolveOrigin(x,depth+1,seen)).filter(Boolean);
      if(os.length===returns.length&&os.length&&new Set(os.map(x=>x.package)).size===1) {
        const o={...os[0],evidence:[...new Set([...os.flatMap(x=>x.evidence),ev(n.getSourceFile(),n,'local-factory-return')])]};originCache.set(target,o);return o;
      }
    }
  }
  return null;
}
function literal(raw,depth=0) {
  const n=unwrap(raw);if(!n||depth>5)return null;
  if(ts.isStringLiteralLike(n))return n.text;
  if(ts.isBinaryExpression(n)&&n.operatorToken.kind===ts.SyntaxKind.PlusToken) {const a=literal(n.left,depth+1),b=literal(n.right,depth+1);return a!==null&&b!==null ? a+b : null;}
  if(ts.isIdentifier(n)){const s=symbol(n);const d=s?.valueDeclaration;if(d&&ts.isVariableDeclaration(d)&&d.initializer)return literal(d.initializer,depth+1);}
  return null;
}
const sdkPackages=new Set(['openai','@anthropic-ai/sdk','@aws-sdk/client-s3','stripe','resend','@modelcontextprotocol/sdk','@cloudflare/containers','pg','redis','@upstash/redis']);
require('./adapters/express.cjs')({ts,sources,symbol,importBindings,assignments,unwrap,ev,entity,edge,rel,owner,component,fileIds,symbolEntity,routes,checker,unknowns});
// Pass two: bound local implementation calls, SDK uses and explicit HTTP call sites.
const counts={call_expressions:0,resolved_implementation_calls:0,signature_only_calls:0,unresolved_calls:0,sdk_api_calls:0};
for(const sf of sources) {
  const r=rel(sf.fileName), visit=n=>{
    if(ts.isCallExpression(n)||ts.isNewExpression(n)) {
      counts.call_expressions++;
      const support=ev(sf,n,ts.isNewExpression(n)?'constructor-callsite':'callsite'), caller=enclosing(n), signature=checker.getResolvedSignature(n), target=signature?.declaration;
      if(target?.body&&texts.has(path.resolve(target.getSourceFile().fileName))) {
        const sid=symbolEntity(target);if(sid) {edge(caller,sid,ts.isNewExpression(n)?'CONSTRUCTS':'CALLS',[support,...entityMap.get(sid).evidence_ids],{callsite:support,derivation:'compiler signature with local implementation body; static only'});counts.resolved_implementation_calls++;}
      } else {
        if(target)counts.signature_only_calls++;else counts.unresolved_calls++;
        unknowns.push({kind:'call',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:target?'signature only; concrete implementation not established':'compiler target unavailable',evidence_ids:[support]});
      }
      const origin=resolveOrigin(ts.isNewExpression(n)?n:n.expression);
      if(origin&&!origin.typeOnly&&sdkPackages.has(pkgName(origin.package))&&(origin.instance||!ts.isNewExpression(n)&&origin.name!=='*')) {
        const name=pkgName(origin.package), targetId=entity('sdk','sdk:'+name,name+' (SDK)',{scope:'external',technology:'Library use; remote endpoint not established',identity:'SDK API; remote deployment/endpoint not established',evidence_ids:origin.evidence});
        edge(caller,targetId,ts.isNewExpression(n)?'CONSTRUCTS_CLIENT':'SDK_API_CALL',[support,...origin.evidence],{callsite:support,target_scope:'external',derivation:'bound import/constructor or supported local factory; SDK invocation is not proof of network delivery'});
        if(!ts.isNewExpression(n))counts.sdk_api_calls++;
      }
      // Global fetch must not be a local function with the same name.
      if(ts.isCallExpression(n)&&ts.isIdentifier(n.expression)&&n.expression.text==='fetch') {
        const decls=symbol(n.expression)?.declarations||[];
        const local=decls.some(d=>texts.has(path.resolve(d.getSourceFile().fileName)));
        if(!local) {
          const value=literal(n.arguments[0]);
          if(value&&/^https?:\/\//i.test(value)) {
            try {const url=new URL(value);const tid=entity('external_service','host:'+url.hostname,url.hostname,{scope:'external',identity:'literal HTTP host',evidence_ids:[support]});edge(caller,tid,'CALLS_HTTP',[support],{callsite:support,target_scope:'external',derivation:'unshadowed fetch with statically literal absolute URL'});}catch{}
          } else unknowns.push({kind:'http',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:value?.startsWith('/')?'relative URL; browser/proxy target unresolved':'dynamic URL or config-dependent destination',evidence_ids:[support]});
        }
      }
    }
    ts.forEachChild(n,visit);
  };visit(sf);
}
require('./adapters/wrangler.cjs')({texts,json,ts,rel,ev,literal,entity,edge,contained,fileIds,unknowns,path});
// One snapshot covers indexed file content, scope and tool version. No timing in canonical graph.
const snapshot=digest(JSON.stringify([...texts].map(([p,t])=>[rel(p),digest(t)]).sort()));
const analyzerHash=digest([__filename,path.join(__dirname,'guard.cjs'),...fs.readdirSync(path.join(__dirname,'adapters')).sort().map(n=>path.join(__dirname,'adapters',n))].map(p=>fs.readFileSync(p)).join(''));
const result={schema_version:'repo-intelligence-1',repository:path.basename(root),source_snapshot_id:snapshot,analyzer_sha256:analyzerHash,
  snapshot_id:digest(snapshot+ts.version+analyzerHash),typescript_version:ts.version,
  languages:inventory.reduce((a,f)=>{const ext=path.extname(f.path).toLowerCase()||'<none>';a[ext]=(a[ext]||0)+1;return a;},{}),
  scope:{production_source:true,tests:false,tooling:false,generated:false,dependencies_installed:false,client_code_executed:false,
    limitation:'Trusted local analyzer; filesystem confinement and heap/deadline limits, not a fully qualified OS sandbox or network-isolation claim'},
  coverage:{inventoried_files:inventory.length,parsed_source_files:sources.length,source_bytes:bytes,syntax_failures:diagnostics.length,...counts,skipped:skips},
  packages:packages.map(p=>({id:p.id,root:p.root,name:p.data.name,dependencies:Object.keys(p.data.dependencies||{}).sort()})),
  entities:entities.sort((a,b)=>a.id.localeCompare(b.id)),edges:edges.sort((a,b)=>a.id.localeCompare(b.id)),evidence:evidence.sort((a,b)=>a.id.localeCompare(b.id)),
  routes:routes.sort((a,b)=>a.file.localeCompare(b.file)||a.method.localeCompare(b.method)),unknowns,diagnostics};
process.stdout.write(JSON.stringify(result));
