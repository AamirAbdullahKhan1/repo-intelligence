'use strict';
// Demand-built monotone constraints. Customer text is parsed, never evaluated.
module.exports=function({ts,checker,sources,symbol,unwrap,texts,path,rel,ev,id,importBindings,isExternal,owner,dynamicScopeFiles}) {
  const limits={cells:12000,steps:40000,updates:100000,candidates:12,contexts:6,milliseconds:8000};
  const cells=new Map(),steps=new Map(),tokens=new Map(),queue=[],queued=new Set(),writes=new Map(),callers=new Map();
  const contexts=new Map(),issues=new Set();let active=null,updates=0,started=Date.now(),partial=false;
  const local=n=>n&&texts.has(path.resolve(n.getSourceFile().fileName));
  function sym(n){let s=ts.isShorthandPropertyAssignment(n.parent)?checker.getShorthandAssignmentValueSymbol(n.parent):symbol(n);if(s?.flags&ts.SymbolFlags.Alias)try{s=checker.getAliasedSymbol(s);}catch{}return s;}
  function fnOwner(n){for(let p=n.parent;p;p=p.parent)if(ts.isFunctionLike(p)&&p.body)return p;return null;}
  for(const sf of sources){function visit(n){
    if(ts.isCallExpression(n)) {const f=checker.getResolvedSignature(n)?.declaration;if(f?.body&&local(f)){const a=callers.get(f)||[];a.push(n);callers.set(f,a);}}
    if(ts.isBinaryExpression(n)&&n.operatorToken.kind>=ts.SyntaxKind.FirstAssignment&&n.operatorToken.kind<=ts.SyntaxKind.LastAssignment){
      let lhs=unwrap(n.left);while(ts.isPropertyAccessExpression(lhs)||ts.isElementAccessExpression(lhs))lhs=unwrap(lhs.expression);
      const s=sym(lhs);if(s){const a=writes.get(s)||[];a.push(n);writes.set(s,a);}
    }
    if(ts.isDeleteExpression(n)||(ts.isPrefixUnaryExpression(n)||ts.isPostfixUnaryExpression(n))&&[ts.SyntaxKind.PlusPlusToken,ts.SyntaxKind.MinusMinusToken].includes(n.operator)){
      let lhs=unwrap(ts.isDeleteExpression(n)?n.expression:n.operand);while(ts.isPropertyAccessExpression(lhs)||ts.isElementAccessExpression(lhs))lhs=unwrap(lhs.expression);
      const s=sym(lhs);if(s){const a=writes.get(s)||[];a.push(n);writes.set(s,a);}
    }
    if((ts.isForInStatement(n)||ts.isForOfStatement(n))&&!ts.isVariableDeclarationList(n.initializer)){
      const s=sym(n.initializer);if(s){const a=writes.get(s)||[];a.push(n);writes.set(s,a);}
    }
    ts.forEachChild(n,visit);
  }visit(sf);}
  // Invalidate simple aliases together when either is mutated; do not retain an
  // initializer-derived identity after alias.send/config replacement.
  for(let round=0;round<8;round++){
    let changed=false;
    for(const [s,records] of [...writes]){
      const d=s.valueDeclaration,init=d&&ts.isVariableDeclaration(d)&&d.initializer&&unwrap(d.initializer);
      if(init&&ts.isIdentifier(init)&&records.some(w=>!ts.isBinaryExpression(w)||!ts.isIdentifier(w.left))){
        const target=sym(init);if(target&&!writes.has(target)){writes.set(target,records);changed=true;}
      }
    }if(!changed)break;
  }
  function token(value){const key=JSON.stringify(value);const tid=id('flow-value',key);tokens.set(tid,value);return tid;}
  const unknown=reason=>token({kind:'unknown',reason});
  function schedule(c){if(!queued.has(c.id)){queued.add(c.id);queue.push(c);}}
  function cell(key,node,compute){
    const cid=id('flow-cell',key);if(cells.has(cid))return cells.get(cid);
    if(cells.size>=limits.cells){partial=true;issues.add('cell budget exhausted');return null;}
    const c={id:cid,node,compute,values:new Set(),listeners:new Set(),evidence_ids:[ev(node.getSourceFile(),node,'flow-expression')]};cells.set(cid,c);schedule(c);return c;
  }
  function read(c,kind='VALUE_FLOW'){
    if(!c)return new Set([unknown('analysis budget exhausted')]);
    if(active){c.listeners.add(active.id);const key=c.id+'|'+active.id+'|'+kind;
      if(!steps.has(key)){
        if(steps.size>=limits.steps){partial=true;issues.add('provenance step budget exhausted');return new Set([unknown('provenance budget exhausted')]);}
        steps.set(key,{id:id('flow-step',key),source:c.id,target:active.id,kind,evidence_ids:[...new Set([...c.evidence_ids,...active.evidence_ids])]});
      }
    }return c.values;
  }
  const loc=n=>rel(n.getSourceFile().fileName)+':'+n.getStart(n.getSourceFile())+':'+n.end+':'+n.kind;
  function context(n,parent,fn){
    const chain=parent?contexts.get(parent)?.chain||[]:[];
    if(chain.length>=limits.contexts){partial=true;issues.add('call context budget exhausted');return null;}
    const key=loc(n)+'|'+(parent||'root');if(!contexts.has(key))contexts.set(key,{fn,call:n,parent,chain:[...chain,key]});return key;
  }
  function scope(n,ctx){const f=fnOwner(n);while(ctx&&contexts.get(ctx)?.fn!==f)ctx=contexts.get(ctx)?.parent;return ctx||'';}
  function expression(raw,ctx=''){
    const n=unwrap(raw);if(!n)return null;
    return cell(loc(n)+'|'+ctx,n,()=>evaluate(n,ctx));
  }
  function property(raw,key,ctx=''){
    const n=unwrap(raw);if(!n)return null;
    return cell(loc(n)+'|'+ctx+'|property:'+key,n,()=>{
      const result=new Set();for(const t of read(expression(n,ctx),'PROPERTY_RECEIVER')){
        const v=tokens.get(t);
        if(v.kind==='object'){
          const object=objectNodes.get(v.site), props=object?.properties||[];
          if(props.some(p=>ts.isSpreadAssignment(p)||p.name&&ts.isComputedPropertyName(p.name))){result.add(unknown('spread/computed property not modeled'));continue;}
          const matches=props.filter(p=>p.name?.text===key);
          if(matches.length!==1){result.add(unknown('missing or duplicate object property'));continue;}
          const p=matches[0],value=ts.isPropertyAssignment(p)?p.initializer:ts.isShorthandPropertyAssignment(p)?p.name:null;
          if(value)for(const x of read(expression(value,v.context),'PROPERTY_VALUE'))result.add(x);
          else result.add(unknown('object accessor/method not modeled'));
        }else if(v.kind==='module')result.add(token({...v,path:[...v.path,key]}));
        else if(v.kind!=='unknown'||v.reason!=='undefined alternative')result.add(unknown('receiver is not a supported object'));
      }return result;
    });
  }
  const objectNodes=new Map(),allocationNodes=new Map();
  function evaluate(n,ctx){
    const out=new Set(),copy=(c,k)=>{for(const t of read(c,k))out.add(t);};
    if(dynamicScopeFiles.has(n.getSourceFile()))return new Set([unknown('dynamic scope or eval invalidates value flow')]);
    if(ts.isStringLiteralLike(n))out.add(token({kind:'literal',value:n.text}));
    else if(n.kind===ts.SyntaxKind.NullKeyword||ts.isIdentifier(n)&&n.text==='undefined')out.add(unknown('undefined alternative'));
    else if(ts.isIdentifier(n)){
      const s=sym(n),d=s?.valueDeclaration||s?.declarations?.[0];
      const imported=importBindings.get(symbol(n));
      if(imported&&!imported.typeOnly)out.add(token({kind:'module',package:imported.package,path:imported.name==='*'?[]:[imported.name]}));
      else if(!d||!local(d))out.add(unknown('unavailable binding'));
      else {
        const changed=writes.get(s)||[];
        const cached=changed.length&&changed.every(w=>ts.isBinaryExpression(w)&&ts.isIdentifier(w.left)&&w.operatorToken.kind===ts.SyntaxKind.QuestionQuestionEqualsToken);
        if(changed.length&&!cached)out.add(unknown('reassignment or object mutation'));
        else if(ts.isVariableDeclaration(d)){
          if(d.initializer)copy(expression(d.initializer,scope(d,ctx)),'INITIALIZER');
          for(const w of changed)copy(expression(w.right,scope(w,ctx)),'CACHED_INITIALIZER_ALTERNATIVE');
        }else if(ts.isBindingElement(d)&&!d.dotDotDotToken&&!d.initializer&&ts.isObjectBindingPattern(d.parent)&&ts.isVariableDeclaration(d.parent.parent))
          copy(property(d.parent.parent.initializer,(d.propertyName||d.name).text,scope(d,ctx)),'DESTRUCTURE');
        else if(ts.isParameter(d)&&ts.isIdentifier(d.name)){
          const fn=d.parent,index=fn.parameters.indexOf(d),frame=ctx&&contexts.get(ctx);
          if(frame?.fn===fn)copy(expression(frame.call.arguments[index]||d.initializer,frame.parent||''),'ARGUMENT_PARAMETER');
          else for(const call of callers.get(fn)||[])copy(expression(call.arguments[index]||d.initializer,''),'CALLER_ALTERNATIVES');
        }else if(ts.isFunctionLike(d)&&d.body)out.add(token({kind:'function',site:loc(d)}));
        else out.add(unknown('unsupported binding'));
      }
    }else if(ts.isObjectLiteralExpression(n)){
      objectNodes.set(loc(n),n);out.add(token({kind:'object',site:loc(n),context:ctx}));
    }else if(ts.isPropertyAccessExpression(n)||ts.isElementAccessExpression(n)){
      const base=unwrap(n.expression),name=ts.isPropertyAccessExpression(n)?n.name.text:null;
      const isEnv=ts.isPropertyAccessExpression(base)&&base.name.text==='env'&&ts.isIdentifier(base.expression)&&base.expression.text==='process'&&!(sym(base.expression)?.declarations||[]).some(d=>local(d)&&(ts.isVariableDeclaration(d)||ts.isParameter(d)||ts.isImportClause(d)||ts.isImportSpecifier(d)||ts.isBindingElement(d)||ts.isFunctionDeclaration(d)));
      if(isEnv){
        if(name)out.add(token({kind:'environment',name}));
        else for(const t of read(expression(n.argumentExpression,ctx),'CONFIG_KEY')){const v=tokens.get(t);if(v.kind==='literal')out.add(token({kind:'environment',name:v.value}));else out.add(unknown('dynamic environment key'));}
      }else if(name)copy(property(base,name,ctx),'PROPERTY_READ');
      else out.add(unknown('computed access not modeled'));
    }else if(ts.isConditionalExpression(n)){copy(expression(n.whenTrue,ctx),'BRANCH_ALTERNATIVE');copy(expression(n.whenFalse,ctx),'BRANCH_ALTERNATIVE');}
    else if(ts.isBinaryExpression(n)&&[ts.SyntaxKind.QuestionQuestionToken,ts.SyntaxKind.BarBarToken].includes(n.operatorToken.kind)){
      copy(expression(n.left,ctx),'BRANCH_ALTERNATIVE');copy(expression(n.right,ctx),'BRANCH_ALTERNATIVE');
    }else if(ts.isNewExpression(n)){
      for(const t of read(expression(n.expression,ctx),'CONSTRUCTOR_IDENTITY')){
        const v=tokens.get(t);if(v.kind==='module'){
          allocationNodes.set(loc(n),n);out.add(token({kind:'instance',package:v.package,path:v.path,site:loc(n),context:ctx}));
        }else out.add(unknown('unbound constructor'));
      }
    }else if(ts.isCallExpression(n)){
      if(n.expression.kind===ts.SyntaxKind.ImportKeyword&&ts.isStringLiteral(n.arguments[0])&&isExternal(n.arguments[0].text,owner(rel(n.getSourceFile().fileName)),n.getSourceFile()))
        out.add(token({kind:'module',package:n.arguments[0].text,path:[]}));
      else if(ts.isPropertyAccessExpression(n.expression)&&n.expression.name.text==='trim'){
        for(const t of read(expression(n.expression.expression,ctx),'CONFIG_STRING_TRIM')){const v=tokens.get(t);if(['environment','literal'].includes(v.kind))out.add(t);else out.add(unknown('trim receiver unknown'));}
      }else {
        const f=checker.getResolvedSignature(n)?.declaration;
        if(f?.body&&local(f)){
          const next=context(n,ctx,f);
          if(next===null)out.add(unknown('call context budget exhausted'));
          else {
            const returns=[];function visit(x){if(x!==f&&ts.isFunctionLike(x))return;if(ts.isReturnStatement(x))returns.push(x.expression);ts.forEachChild(x,visit);}
            if(ts.isBlock(f.body))visit(f);else returns.push(f.body);
            if(!returns.length)out.add(unknown('no returned value'));
            for(const value of returns)if(value)copy(expression(value,next),'RETURN_VALUE');else out.add(unknown('undefined alternative'));
          }
        }else out.add(unknown('external or unavailable call result'));
      }
    }else out.add(unknown('unsupported expression '+ts.SyntaxKind[n.kind]));
    return out;
  }
  function solve(){
    for(let cursor=0;cursor<queue.length;cursor++){
      if(++updates>limits.updates||Date.now()-started>limits.milliseconds){partial=true;issues.add('worklist/time budget exhausted');break;}
      const c=queue[cursor];queued.delete(c.id);active=c;let values;
      try{values=c.compute();}finally{active=null;}
      let changed=false;for(const t of values){if(!c.values.has(t)){
        if(c.values.size>=limits.candidates){partial=true;issues.add('candidate budget exhausted');const u=unknown('candidate budget exhausted');if(!c.values.has(u)){c.values.add(u);changed=true;}break;}
        c.values.add(t);changed=true;
      }}if(changed)for(const key of c.listeners)schedule(cells.get(key));
    }queue.length=0;queued.clear();
  }
  function values(c){return c?[...c.values].map(t=>tokens.get(t)):[];}
  function proof(roots){const pending=roots.filter(Boolean).map(c=>c.id),seen=new Set(),links=[];const incoming=new Map();for(const s of steps.values()){const a=incoming.get(s.target)||[];a.push(s);incoming.set(s.target,a);}
    while(pending.length){const key=pending.pop();if(seen.has(key))continue;seen.add(key);for(const s of incoming.get(key)||[]){links.push(s.id);pending.push(s.source);}}
    return {flow_root_ids:roots.filter(Boolean).map(c=>c.id),flow_step_ids:[...new Set(links)].sort(),evidence_ids:[...new Set([...seen].flatMap(k=>cells.get(k).evidence_ids))]};
  }
  function report(){return {version:'bounded-flow-1',provider:'trusted-ts-flow',partial,limits,reasons:[...issues].sort(),updates,
    nodes:[...cells.values()].map(c=>({id:c.id,evidence_ids:c.evidence_ids,values:values(c).map(v=>v.kind==='literal'?{kind:'literal',identity:id('flow-literal',v.value)}:v)})).sort((a,b)=>a.id.localeCompare(b.id)),steps:[...steps.values()].sort((a,b)=>a.id.localeCompare(b.id)),
    limitations:['Demand-driven possible-value analysis, not runtime execution','Branch alternatives are not path-sensitive','Unsupported writes invalidate bindings; alias side effects remain incomplete','Context, candidate and work budgets can yield partial results']};}
  function operationContexts(n){const fn=fnOwner(n),sites=callers.get(fn)||[];
    if(sites.length>40){partial=true;issues.add('operation caller budget exhausted');}
    return sites.length?sites.slice(0,40).map(call=>context(call,'',fn)):[''];
  }
  return {expression,property,solve,values,proof,report,allocationNodes,operationContexts,contextCall:key=>contexts.get(key)?.call,get partial(){return partial;}};
};
