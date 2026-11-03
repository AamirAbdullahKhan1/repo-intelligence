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
const excluded = new Set(['.git', 'node_modules', 'vendor', 'vendors', '.next', '.open-next', '.open-next-history', '.venv', 'dist', 'build', '__pycache__']);
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
    // Public browser scripts and application plugins/scripts can contain real
    // implementations. Parse them as candidates; a folder name is not dead-code evidence.
    if (/(?:^|\/)(?:experiments|docs)(?:\/|$)/.test(r) || /(?:\.test\.|\.spec\.|\.fixture\.|\/__tests__\/|\/test\/|\/test-[^/]+$)/.test(r)) {
      skips.push({ file:r, reason:'test/documentation/experimental scope' }); continue;
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
const options={allowJs:true,checkJs:false,noEmit:true,skipLibCheck:true,types:[],target:ts.ScriptTarget.ES2022,
  module:ts.ModuleKind.ESNext,moduleResolution:ts.ModuleResolutionKind.Bundler,jsx:ts.JsxEmit.Preserve,
};
// Only explicitly supplied text and trusted compiler standard libraries are visible.
const libRoot=path.resolve(path.dirname(ts.getDefaultLibFilePath(options)));
const trustedLib=p=>path.dirname(path.resolve(p))===libRoot && /^lib\..*\.d\.ts$/.test(path.basename(p));
const sourceDirectories=new Set([root]);
for(const p of texts.keys()) {
  let dir=path.dirname(p);
  while(contained(dir)&&!sourceDirectories.has(dir)) {
    sourceDirectories.add(dir);const parent=path.dirname(dir);if(parent===dir)break;dir=parent;
  }
}
const host=ts.createCompilerHost(options);
const oldRead=host.readFile;
host.readFile=p=>texts.get(path.resolve(p)) ?? (trustedLib(p) ? oldRead(p) : undefined);
host.fileExists=p=>texts.has(path.resolve(p)) || (trustedLib(p)&&fs.existsSync(p));
host.directoryExists=p=>sourceDirectories.has(path.resolve(p)) || path.resolve(p)===libRoot;
host.realpath=p=>path.resolve(p);
host.getCurrentDirectory=()=>root;
host.getSourceFile=(p,version)=>{const t=host.readFile(p); return t===undefined ? undefined : ts.createSourceFile(p,t,version,true);};
host.writeFile=()=>{throw Error('Emission is prohibited');};
// Parse inert project configuration using the compiler, with no filesystem
// fallback. Project-specific resolution is shared by extraction and binding.
const configCache=new Map(), fileOptions=new Map(), resolutionCache=new Map();
const configHost={...host,useCaseSensitiveFileNames:true,readDirectory:()=>[],
  onUnRecoverableConfigFileDiagnostic:()=>{}};
function projectOptions(file) {
  const dir=path.dirname(file);if(fileOptions.has(dir))return fileOptions.get(dir);
  let at=dir, configPath;
  while(contained(at)) {
    configPath=['tsconfig.json','jsconfig.json'].map(n=>path.join(at,n)).find(p=>texts.has(p));
    if(configPath||at===root)break;at=path.dirname(at);
  }
  let result=options;
  if(configPath) {
    if(!configCache.has(configPath)) {
      const parsed=ts.getParsedCommandLineOfConfigFile(configPath,{},configHost);
      const errors=(parsed?.errors||[]).filter(e=>e.code!==18003);
      if(!parsed||errors.length) {
        diagnostics.push({file:rel(configPath),kind:'project-configuration',codes:errors.map(e=>e.code),
          limitation:'Invalid or unavailable configuration; aliases are not guessed.'});
        configCache.set(configPath,{...options,paths:{}});
      } else configCache.set(configPath,{...options,...parsed.options,allowJs:true,noEmit:true,types:[]});
    }
    result=configCache.get(configPath);
  }
  fileOptions.set(dir,result);return result;
}
// Virtual workspace installation for explicitly declared package.json workspaces.
// TypeScript still interprets exports/main/types and conditions; missing dist
// outputs are never guessed to be src implementations.
function workspaceMatch(pattern,value) {
  if(typeof pattern!=='string'||pattern.startsWith('!')||/[{}[\]\\]/.test(pattern))return false;
  const escaped=pattern.replace(/\/$/,'').split('/').map(x=>x==='**'?'.*':x.split('*').map(y=>y.replace(/[.*+?^${}()|[\]\\]/g,'\\$&')).join('[^/]*')).join('/');
  return new RegExp('^'+escaped+'$').test(value);
}
const workspaceRoots=new Map();
for(const parent of packages) {
  const patterns=Array.isArray(parent.data.workspaces)?parent.data.workspaces:parent.data.workspaces?.packages;
  if(!Array.isArray(patterns))continue;
  const names=new Map();
  for(const pkg of packages) {
    const local=path.posix.relative(parent.root,pkg.root), name=pkg.data.name;
    if(!name||local.startsWith('..')||!patterns.some(p=>workspaceMatch(p,local)))continue;
    names.set(name,names.has(name)?null:path.resolve(root,pkg.root));
  }
  workspaceRoots.set(path.resolve(root,parent.root),names);
}
function workspacePath(p) {
  const absolute=path.resolve(p), marker=path.sep+'node_modules'+path.sep, i=absolute.lastIndexOf(marker);
  if(i<0)return absolute;
  const base=absolute.slice(0,i), rest=absolute.slice(i+marker.length).split(path.sep);
  const name=rest[0]?.startsWith('@')?rest.slice(0,2).join('/'):rest[0];
  const destination=workspaceRoots.get(base)?.get(name);
  if(!destination)return absolute;
  const mapped=path.resolve(destination,...rest.slice(name.startsWith('@')?2:1));
  return contained(mapped)&&!path.relative(destination,mapped).startsWith('..')?mapped:absolute;
}
const resolutionHost={...host,
  fileExists:p=>host.fileExists(workspacePath(p)),readFile:p=>host.readFile(workspacePath(p)),
  directoryExists:raw=>{const p=path.resolve(raw);return path.basename(p)==='node_modules'&&workspaceRoots.has(path.dirname(p))||
    path.basename(p).startsWith('@')&&path.basename(path.dirname(p))==='node_modules'&&
      [...(workspaceRoots.get(path.dirname(path.dirname(p)))?.keys()||[])].some(n=>n.startsWith(path.basename(p)+'/'))||
    host.directoryExists(workspacePath(p));},
  realpath:workspacePath};
function resolveModule(spec,file) {
  const key=file+'|'+spec;if(resolutionCache.has(key))return resolutionCache.get(key);
  const resolved=ts.resolveModuleName(spec,file,projectOptions(file),resolutionHost).resolvedModule;
  const result=resolved?{...resolved,resolvedFileName:workspacePath(resolved.resolvedFileName)}:undefined;
  resolutionCache.set(key,result);return result;
}
host.resolveModuleNames=(names,file)=>names.map(name=>resolveModule(name,file));
const program=ts.createProgram(files,options,host), checker=program.getTypeChecker();
const sources=program.getSourceFiles().filter(s=>texts.has(path.resolve(s.fileName)) && files.includes(path.resolve(s.fileName)));
const importBindings=new Map(), assignments=new Map(), originCache=new Map();
const writtenSymbols=new Set(), dynamicScopeFiles=new Set();
function symbol(n) { try { return checker.getSymbolAtLocation(n); } catch {return null;} }
function unwrap(n) { while(n&&(ts.isAwaitExpression(n)||ts.isParenthesizedExpression(n)||ts.isAsExpression(n)||ts.isNonNullExpression(n)||ts.isTypeAssertionExpression(n))) n=n.expression; return n; }
// Indexed once in pass one, rather than rescanning the repository for each URL.
// Reaching definitions are not modeled yet: any write invalidates initializer
// following, including conditional, captured and destructuring assignments.
function markWritten(raw) {
  const n=unwrap(raw); if(!n)return;
  if(ts.isIdentifier(n)) {const s=symbol(n);if(s)writtenSymbols.add(s);}
  else if(ts.isArrayLiteralExpression(n))for(const item of n.elements)markWritten(item);
  else if(ts.isObjectLiteralExpression(n))for(const item of n.properties) {
    if(ts.isShorthandPropertyAssignment(item)) {
      const s=checker.getShorthandAssignmentValueSymbol(item)||symbol(item.name);if(s)writtenSymbols.add(s);
    } else if(ts.isPropertyAssignment(item))markWritten(item.initializer);
    else if(ts.isSpreadAssignment(item))markWritten(item.expression);
  }
  else if(ts.isSpreadElement(n))markWritten(n.expression);
  else if(ts.isBinaryExpression(n)&&n.operatorToken.kind===ts.SyntaxKind.EqualsToken)markWritten(n.left);
}
function pkgName(s) { return s.startsWith('@') ? s.split('/').slice(0,2).join('/') : s.split('/')[0]; }
function declared(p,s) { return !!(p.data.dependencies?.[pkgName(s)] || p.data.devDependencies?.[pkgName(s)]); }
function knownWorkspace(spec,file) {
  let at=path.dirname(path.resolve(file));
  while(contained(at)) {if(workspaceRoots.get(at)?.has(pkgName(spec)))return true;if(at===root)break;at=path.dirname(at);}
  return false;
}
function isExternal(spec,p,sf) { return !knownWorkspace(spec,sf.fileName)&&!spec.startsWith('.')&&!spec.startsWith('/')&&!Object.keys(projectOptions(sf.fileName).paths||{}).some(k=>spec.startsWith(k.replace('*',''))) && (declared(p,spec)||spec.startsWith('node:')); }
function localTarget(spec,sf) { return resolveModule(spec,sf.fileName)?.resolvedFileName; }
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
    if(ts.isBinaryExpression(n)&&n.operatorToken.kind>=ts.SyntaxKind.FirstAssignment&&n.operatorToken.kind<=ts.SyntaxKind.LastAssignment)markWritten(n.left);
    if((ts.isPrefixUnaryExpression(n)||ts.isPostfixUnaryExpression(n))&&
       (n.operator===ts.SyntaxKind.PlusPlusToken||n.operator===ts.SyntaxKind.MinusMinusToken))markWritten(n.operand);
    if((ts.isForInStatement(n)||ts.isForOfStatement(n))&&!ts.isVariableDeclarationList(n.initializer))markWritten(n.initializer);
    if(ts.isWithStatement(n)||ts.isCallExpression(n)&&ts.isIdentifier(n.expression)&&n.expression.text==='eval')dynamicScopeFiles.add(sf);
    if(ts.isImportDeclaration(n)&&ts.isStringLiteral(n.moduleSpecifier)) {
      const spec=n.moduleSpecifier.text, support=ev(sf,n,'import-statement'), target=localTarget(spec,sf), external=!(target&&contained(target)&&texts.has(path.resolve(target)))&&isExternal(spec,owner(r),sf);
      const bindings=[]; const clause=n.importClause;
      if(clause?.name) bindings.push([clause.name,'default',!!clause.isTypeOnly]);
      if(clause?.namedBindings) {
        if(ts.isNamespaceImport(clause.namedBindings)) bindings.push([clause.namedBindings.name,'*',!!clause.isTypeOnly]);
        else for(const x of clause.namedBindings.elements) bindings.push([x.name,x.propertyName?.text||x.name.text,!!clause.isTypeOnly||!!x.isTypeOnly]);
      }
      for(const [b,name,typeOnly] of bindings) {const s=symbol(b); if(s&&external)importBindings.set(s,{package:spec,name,evidence:[support],instance:false,typeOnly});}
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
function literal(raw,depth=0,definitions=[]) {
  const n=unwrap(raw);if(!n||depth>5)return null;
  if(ts.isStringLiteralLike(n))return n.text;
  if(ts.isTemplateExpression(n)) {
    let value=n.head.text;
    for(const span of n.templateSpans) {const part=literal(span.expression,depth+1,definitions);if(part===null)return null;value+=part+span.literal.text;}
    return value;
  }
  if(ts.isBinaryExpression(n)&&n.operatorToken.kind===ts.SyntaxKind.PlusToken) {const a=literal(n.left,depth+1,definitions),b=literal(n.right,depth+1,definitions);return a!==null&&b!==null ? a+b : null;}
  if(ts.isIdentifier(n)) {
    let s=symbol(n);
    if(s?.flags&ts.SymbolFlags.Alias) {
      const declarations=s.declarations||[];
      if(declarations.some(d=>ts.isImportSpecifier(d)&&d.isTypeOnly||ts.isImportClause(d)&&d.isTypeOnly||ts.isImportSpecifier(d)&&d.parent.parent.isTypeOnly))return null;
      try {s=checker.getAliasedSymbol(s);}catch{return null;}
      if(!s?.valueDeclaration||!texts.has(path.resolve(s.valueDeclaration.getSourceFile().fileName)))return null;
      definitions.push(...declarations);
    }
    const d=s?.valueDeclaration;
    if(writtenSymbols.has(s)||s?.declarations?.length!==1||dynamicScopeFiles.has(n.getSourceFile()))return null;
    if(d&&ts.isVariableDeclaration(d)&&d.initializer&&!dynamicScopeFiles.has(d.getSourceFile())) {
      definitions.push(d);
      return literal(d.initializer,depth+1,definitions);
    }
  }
  return null;
}
const sdkPackages=new Set(['openai','@anthropic-ai/sdk','@aws-sdk/client-s3','stripe','resend','@modelcontextprotocol/sdk','@cloudflare/containers','pg','redis','@upstash/redis']);
require('./adapters/express.cjs')({ts,sources,symbol,importBindings,assignments,unwrap,ev,entity,edge,rel,owner,component,fileIds,symbolEntity,routes,checker,unknowns});
const linkHttp=require('./adapters/http.cjs')({ts,inventory,routes,edges,owner,ev,edge,literal,unwrap});
// Pass two: bound local implementation calls, SDK uses and explicit HTTP call sites.
const libraryReferences=[];
const counts={call_expressions:0,resolved_implementation_calls:0,signature_only_calls:0,known_library_calls:0,unresolved_calls:0,sdk_api_calls:0};
for(const sf of sources) {
  const r=rel(sf.fileName), visit=n=>{
    if(ts.isCallExpression(n)||ts.isNewExpression(n)) {
      counts.call_expressions++;
      const support=ev(sf,n,ts.isNewExpression(n)?'constructor-callsite':'callsite'), caller=enclosing(n), signature=checker.getResolvedSignature(n), target=signature?.declaration;
      if(target?.body&&texts.has(path.resolve(target.getSourceFile().fileName))) {
        const sid=symbolEntity(target);if(sid) {edge(caller,sid,ts.isNewExpression(n)?'CONSTRUCTS':'CALLS',[support,...entityMap.get(sid).evidence_ids],{callsite:support,derivation:'compiler signature with local implementation body; static only'});counts.resolved_implementation_calls++;}
      } else {
        if(target)counts.signature_only_calls++;else counts.unresolved_calls++;
        if(target&&trustedLib(target.getSourceFile().fileName)) {
          counts.known_library_calls++;
          libraryReferences.push({id:id('library-reference',support),source:caller,file:r,
            line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,
            api:target.name?.getText(target.getSourceFile())||ts.SyntaxKind[target.kind],
            library:path.basename(target.getSourceFile().fileName),resolution:'signature-resolved',
            implementation:'trusted standard-library declaration; runtime body not analyzed',evidence_ids:[support]});
        } else unknowns.push({kind:'call',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:target?'signature only; concrete implementation not established':'compiler target unavailable',evidence_ids:[support]});
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
          const definitions=[], value=literal(n.arguments[0],0,definitions);
          if(value&&/^https?:\/\//i.test(value)) {
            try {const url=new URL(value);const supports=[support,...definitions.map(d=>ev(d.getSourceFile(),d,'literal-value-definition'))];const tid=entity('external_service','host:'+url.hostname,url.hostname,{scope:'external',identity:'literal HTTP host',evidence_ids:supports});edge(caller,tid,'CALLS_HTTP',supports,{callsite:support,target_scope:'external',derivation:'unshadowed fetch with literal or unmodified initializer chain; static destination, not runtime delivery'});}catch{}
          } else if(value?.startsWith('/')) {
            const unknown=linkHttp({n,sf,r,caller,support,value,definitions});if(unknown)unknowns.push(unknown);
          } else unknowns.push({kind:'http',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:'dynamic, reassigned or config-dependent destination; value flow not established',evidence_ids:[support]});
        }
      }
    }
    ts.forEachChild(n,visit);
  };visit(sf);
}
require('./adapters/wrangler.cjs')({texts,json,ts,rel,ev,literal,entity,edge,contained,fileIds,unknowns,path});
require('./adapters/resources.cjs')({ts,sources,entities,edges,entity,edge,ev,rel,owner,component,symbol,enclosing,literal,unwrap,writtenSymbols,dynamicScopeFiles,importBindings,unknowns});
// One snapshot covers indexed file content, scope and tool version. No timing in canonical graph.
const snapshot=digest(JSON.stringify([...texts].map(([p,t])=>[rel(p),digest(t)]).sort()));
const analyzerHash=digest([__filename,path.join(__dirname,'guard.cjs'),...fs.readdirSync(path.join(__dirname,'adapters')).sort().map(n=>path.join(__dirname,'adapters',n))].map(p=>fs.readFileSync(p)).join(''));
const result={schema_version:'repo-intelligence-1',repository:path.basename(root),source_snapshot_id:snapshot,analyzer_sha256:analyzerHash,
  snapshot_id:digest(snapshot+ts.version+analyzerHash),typescript_version:ts.version,
  languages:inventory.reduce((a,f)=>{const ext=path.extname(f.path).toLowerCase()||'<none>';a[ext]=(a[ext]||0)+1;return a;},{}),
  scope:{production_source:true,tests:false,tooling:true,generated:false,dependencies_installed:false,client_code_executed:false,
    limitation:'Public, scripts and plugins source candidates are parsed; production reachability is not established. Test, documentation, experimental and generated/vendor exclusions remain. Trusted analyzer guards and heap/deadline limits are not an OS sandbox.'},
  coverage:{inventoried_files:inventory.length,parsed_source_files:sources.length,source_bytes:bytes,syntax_failures:diagnostics.filter(d=>d.kind==='parse').length,
    standard_library_files:program.getSourceFiles().filter(sf=>trustedLib(sf.fileName)).length,...counts,skipped:skips},
  library_references:libraryReferences,
  packages:packages.map(p=>({id:p.id,root:p.root,name:p.data.name,dependencies:Object.keys(p.data.dependencies||{}).sort()})),
  entities:entities.sort((a,b)=>a.id.localeCompare(b.id)),edges:edges.sort((a,b)=>a.id.localeCompare(b.id)),evidence:evidence.sort((a,b)=>a.id.localeCompare(b.id)),
  routes:routes.sort((a,b)=>a.file.localeCompare(b.file)||a.method.localeCompare(b.method)),unknowns,diagnostics};
process.stdout.write(JSON.stringify(result));
