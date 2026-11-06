'use strict';
module.exports=({ts,checker,symbol,unwrap,resolveValue,texts,path,trustedLib,importBindings,writtenSymbols,dynamicScopeFiles,ev,edge,enclosing,symbolEntity})=>{
  function callback(raw){
    const definitions=[],n=resolveValue(raw,definitions);if(!n)return null;
    if(ts.isFunctionLike(n)&&n.body)return {fn:n,definitions};
    let s=symbol(n);if(s?.flags&ts.SymbolFlags.Alias)try{s=checker.getAliasedSymbol(s);}catch{return null;}
    if(writtenSymbols.has(s))return null;
    const fn=s?.valueDeclaration;if(fn?.body&&ts.isFunctionLike(fn))return {fn,definitions};
    return null;
  }
  const summaries=new Map();
  return n=>{
    if(dynamicScopeFiles.has(n.getSourceFile()))return;
    // Summarize only actual parameter invocations in a bound local body.
    // Link at the invoking call site to keep different callers' arguments apart.
    if(ts.isCallExpression(n)){
      const fn=checker.getResolvedSignature(n)?.declaration;
      if(fn?.body&&texts.has(path.resolve(fn.getSourceFile().fileName))&&!dynamicScopeFiles.has(fn.getSourceFile())){
        if(!summaries.has(fn)){
          const uses=[];
          function visit(x){
            if(x!==fn&&ts.isFunctionLike(x))return;
            if(ts.isCallExpression(x)){
              const callee=unwrap(x.expression),base=ts.isPropertyAccessExpression(callee)?callee.expression:callee;
              if(ts.isIdentifier(base)){
                const i=fn.parameters.findIndex(p=>ts.isIdentifier(p.name)&&symbol(p.name)===symbol(base));
                if(i>=0&&!writtenSymbols.has(symbol(base)))uses.push({i,key:ts.isPropertyAccessExpression(callee)?callee.name.text:null,site:x});
              }
            }
            ts.forEachChild(x,visit);
          }visit(fn);summaries.set(fn,uses);
        }
        for(const use of summaries.get(fn)){
          const definitions=[],arg=n.arguments[use.i];
          const value=use.key?resolveValue.property(arg,use.key,definitions):arg,found=callback(value);
          if(!found)continue;
          const support=ev(n.getSourceFile(),n,'local-callback-argument');
          edge(enclosing(n),symbolEntity(found.fn),'MAY_INVOKE_CALLBACK',[support,ev(use.site.getSourceFile(),use.site,'local-parameter-invocation'),ev(found.fn.getSourceFile(),found.fn,'callback-implementation'),...definitions.concat(found.definitions).map(d=>ev(d.getSourceFile(),d,'callback-value-definition'))],
            {callsite:support,resolution:'conditional',api:'local parameter'+(use.key?'.'+use.key:''),derivation:'Bound local implementation invokes supplied parameter; call-site-specific argument summary',limitation:'Invocation may depend on branches, retries and exceptions; no runtime order or frequency inferred'});
        }
      }
    }
    const expression=unwrap(n.expression);let raw,api,condition;
    if(ts.isIdentifier(expression)){
      const declarations=symbol(expression)?.declarations||[],global=!writtenSymbols.has(symbol(expression))&&declarations.length&&declarations.every(d=>trustedLib(d.getSourceFile().fileName));
      if(global&&ts.isNewExpression(n)&&expression.text==='ReadableStream'){
        const object=unwrap(n.arguments?.[0]);if(!object||!ts.isObjectLiteralExpression(object)||object.properties.some(p=>ts.isSpreadAssignment(p)||p.name&&ts.isComputedPropertyName(p.name)))return;
        const starts=object.properties.filter(p=>p.name?.text==='start');if(starts.length!==1)return;
        raw=ts.isMethodDeclaration(starts[0])?starts[0]:starts[0].initializer;api='ReadableStream.start';condition='Constructor start callback; may throw or reject; not a complete runtime sequence';
      }else if(global&&ts.isNewExpression(n)&&expression.text==='Promise'){
        raw=n.arguments?.[0];api='Promise.executor';condition='Executor invoked by construction; resolution/rejection and subsequent callbacks not inferred';
      }else if(global&&ts.isCallExpression(n)&&['setTimeout','setInterval','queueMicrotask'].includes(expression.text)){
        raw=n.arguments[0];api=expression.text;condition='Scheduled callback; execution depends on scheduling, lifetime and cancellation';
      }else {
        const imported=importBindings.get(symbol(expression));
        if(ts.isCallExpression(n)&&imported?.package==='next/server'&&imported.name==='after'&&!imported.typeOnly&&!writtenSymbols.has(symbol(expression))){raw=n.arguments[0];api='next.after';condition='Deferred until response or prerender completion; lifecycle and platform limits apply';}
      }
    }else if(ts.isCallExpression(n)&&ts.isPropertyAccessExpression(expression)&&expression.name.text==='addEventListener'){
      const target=checker.getResolvedSignature(n)?.declaration;
      if(target&&trustedLib(target.getSourceFile().fileName)){raw=n.arguments[1];api='EventTarget.addEventListener';condition='Possible event callback only if the registered event occurs and listener remains registered';}
    }
    if(!raw)return;const found=callback(raw);if(!found||!texts.has(path.resolve(found.fn.getSourceFile().fileName)))return;
    const support=ev(n.getSourceFile(),n,'callback-registration');
    edge(enclosing(n),symbolEntity(found.fn),'MAY_INVOKE_CALLBACK',[support,ev(found.fn.getSourceFile(),found.fn,'callback-implementation'),...found.definitions.map(d=>ev(d.getSourceFile(),d,'callback-value-definition'))],
      {callsite:support,resolution:'conditional',api,derivation:'Bound API callback contract; registration is distinct from a direct function call',limitation:condition});
  };
};
