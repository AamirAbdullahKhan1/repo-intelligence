'use strict';
// Bounded expression summaries, never evaluation. Reject control-dependent returns.
module.exports=({ts,checker,symbol,unwrap,writtenSymbols,dynamicScopeFiles,texts,path})=>{
  function resolve(raw,definitions=[],depth=0,env=new Map(),seen=new Set()) {
    const n=unwrap(raw);if(!n||depth>12||dynamicScopeFiles.has(n.getSourceFile()))return null;
    if(ts.isIdentifier(n)) {
      let s=ts.isShorthandPropertyAssignment(n.parent)?checker.getShorthandAssignmentValueSymbol(n.parent):symbol(n);if(!s||writtenSymbols.has(s)||seen.has(s))return null;
      if(env.has(s))return resolve(env.get(s).node,definitions,depth+1,env.get(s).env,seen);
      if(s.flags&ts.SymbolFlags.Alias){definitions.push(...s.declarations||[]);try{s=checker.getAliasedSymbol(s);}catch{return null;}}
      if(writtenSymbols.has(s)||s.declarations?.length!==1)return null;
      const d=s.valueDeclaration||s.declarations[0];if(!d||!texts.has(path.resolve(d.getSourceFile().fileName)))return n;
      const next=new Set(seen);next.add(s);
      if(ts.isVariableDeclaration(d)&&d.initializer){definitions.push(d);return resolve(d.initializer,definitions,depth+1,env,next);}
      if(ts.isBindingElement(d)&&!d.dotDotDotToken&&!d.initializer&&ts.isObjectBindingPattern(d.parent)&&ts.isVariableDeclaration(d.parent.parent)) {
        definitions.push(d);return property(d.parent.parent.initializer,(d.propertyName||d.name).text,definitions,depth+1,env,next);
      }
      return n;
    }
    if(ts.isPropertyAccessExpression(n))return property(n.expression,n.name.text,definitions,depth+1,env,seen)||n;
    if(ts.isCallExpression(n)) {
      const fn=checker.getResolvedSignature(n)?.declaration;
      if(fn?.body&&texts.has(path.resolve(fn.getSourceFile().fileName))&&!fn.asteriskToken&&!fn.modifiers?.some(m=>m.kind===ts.SyntaxKind.AsyncKeyword)) {
        // A single straight-line return avoids pretending branch alternatives are certain.
        const body=fn.body, statements=ts.isBlock(body)?body.statements:null;
        if(statements&&(!statements.length||!ts.isReturnStatement(statements.at(-1))||statements.slice(0,-1).some(s=>!ts.isVariableStatement(s))))return null;
        const value=statements?statements.at(-1).expression:body;if(!value||fn.parameters.some(p=>!ts.isIdentifier(p.name)||p.dotDotDotToken))return null;
        const bindings=new Map(env);
        for(let i=0;i<fn.parameters.length;i++){const p=fn.parameters[i],arg=n.arguments[i]||p.initializer;if(!arg)return null;bindings.set(symbol(p.name),{node:arg,env});}
        definitions.push(fn,n);return resolve(value,definitions,depth+1,bindings,seen);
      }
    }
    return n;
  }
  function property(raw,key,definitions,depth,env,seen){
    if(depth>12)return null;
    const call=unwrap(raw);
    if(call&&ts.isCallExpression(call)){
      const fn=checker.getResolvedSignature(call)?.declaration,body=fn?.body;
      if(body&&texts.has(path.resolve(fn.getSourceFile().fileName))&&!fn.asteriskToken&&!fn.modifiers?.some(m=>m.kind===ts.SyntaxKind.AsyncKeyword)){
        const statements=ts.isBlock(body)?body.statements:null;
        if(statements&&(!statements.length||!ts.isReturnStatement(statements.at(-1))||statements.slice(0,-1).some(s=>!ts.isVariableStatement(s))))return null;
        if(fn.parameters.some(p=>!ts.isIdentifier(p.name)||p.dotDotDotToken))return null;
        const bindings=new Map(env);
        for(let i=0;i<fn.parameters.length;i++){const p=fn.parameters[i],arg=call.arguments[i]||p.initializer;if(!arg)return null;bindings.set(symbol(p.name),{node:arg,env});}
        definitions.push(fn,call);return property(statements?statements.at(-1).expression:body,key,definitions,depth+1,bindings,seen);
      }
    }
    if(depth>12)return null;
    const object=resolve(raw,definitions,depth+1,env,seen);if(!object||!ts.isObjectLiteralExpression(object))return null;
    if(object.properties.some(p=>ts.isSpreadAssignment(p)||p.name&&ts.isComputedPropertyName(p.name)))return null;
    const matches=object.properties.filter(p=>p.name?.text===key);if(matches.length!==1)return null;
    const p=matches[0];definitions.push(p);
    return ts.isPropertyAssignment(p)?resolve(p.initializer,definitions,depth+1,env,seen):ts.isShorthandPropertyAssignment(p)?resolve(p.name,definitions,depth+1,env,seen):null;
  }
  resolve.property=(raw,key,definitions=[])=>property(raw,key,definitions,0,new Map(),new Set());
  return resolve;
};
