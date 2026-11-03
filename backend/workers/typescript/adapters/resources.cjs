'use strict';
module.exports=function({ts,sources,entities,edges,entity,edge,ev,rel,owner,component,symbol,enclosing,literal,unwrap,writtenSymbols,dynamicScopeFiles,importBindings,unknowns}) {
  const nodes=new Map(entities.map(n=>[n.id,n])), clients=new Map(), changed=new Set(writtenSymbols);
  function rootSymbol(n) {n=unwrap(n);while(n&&(ts.isPropertyAccessExpression(n)||ts.isElementAccessExpression(n)))n=unwrap(n.expression);return n&&symbol(n);}
  // Property replacement on a client/env invalidates this narrow receiver model.
  for(const sf of sources) {
    function visit(n) {
      if(ts.isBinaryExpression(n)&&n.operatorToken.kind>=ts.SyntaxKind.FirstAssignment&&n.operatorToken.kind<=ts.SyntaxKind.LastAssignment||ts.isDeleteExpression(n)) {
        const target=ts.isDeleteExpression(n)?n.expression:n.left;const s=rootSymbol(target);if(s)changed.add(s);
      }
      if((ts.isPrefixUnaryExpression(n)||ts.isPostfixUnaryExpression(n))&&[ts.SyntaxKind.PlusPlusToken,ts.SyntaxKind.MinusMinusToken].includes(n.operator)) {
        const s=rootSymbol(n.operand);if(s)changed.add(s);
      }
      if((ts.isForInStatement(n)||ts.isForOfStatement(n))&&!ts.isVariableDeclarationList(n.initializer)) {
        const s=rootSymbol(n.initializer);if(s)changed.add(s);
      }
      ts.forEachChild(n,visit);
    }visit(sf);
  }
  const entries=new Map(),bindingIndex=new Map();
  for(const b of edges)if(b.kind==='BINDS_RESOURCE'&&nodes.get(b.target)?.technology==='R2 bucket') {
    const key=b.source+'|'+b.profile;if(!bindingIndex.has(key))bindingIndex.set(key,[]);bindingIndex.get(key).push(b);
  }
  for(const e of edges.filter(e=>e.kind==='ENTRYPOINT')) {
    const file=nodes.get(e.target)?.file;if(!file)continue;
    const bindings=bindingIndex.get(e.source+'|'+e.profile)||[];
    if(!entries.has(file))entries.set(file,[]);entries.get(file).push(...bindings.map(b=>({...b,
      entry_edge_id:e.id,evidence_ids:[...b.evidence_ids,...e.evidence_ids]})));
  }
  for(const sf of sources) {
    if(dynamicScopeFiles.has(sf))continue;
    const r=rel(sf.fileName);
    // Only named, externally bound SDK constructors with inline options.
    function constructors(n) {
      if(ts.isVariableDeclaration(n)&&ts.isIdentifier(n.name)&&n.initializer) {
        const init=unwrap(n.initializer), s=symbol(n.name);
        if(s&&!changed.has(s)&&s.declarations?.length===1&&(ts.isNewExpression(init)||ts.isCallExpression(init))) {
          const imported=importBindings.get(symbol(init.expression));
          const technology=imported&&!imported.typeOnly&&imported.package==='pg'&&['Pool','Client'].includes(imported.name)&&ts.isNewExpression(init)?'PostgreSQL':
            imported&&!imported.typeOnly&&imported.package==='redis'&&imported.name==='createClient'&&ts.isCallExpression(init)?'Redis':null;
          if(technology) {
            const options=unwrap(init.arguments?.[0]);let value,prop;const definitions=[];
            if(options&&ts.isObjectLiteralExpression(options)&&options.properties.every(p=>ts.isPropertyAssignment(p)&&!ts.isComputedPropertyName(p.name))) {
              const key=technology==='PostgreSQL'?'connectionString':'url';
              prop=options.properties.filter(p=>p.name.text===key).at(-1);
              // Other connection fields may override the URL; not modeled here.
              if(prop&&!options.properties.some(p=>['host','port','database','socket'].includes(p.name.text)))value=literal(prop.initializer,0,definitions);
            }
            let resource;
            if(value)try {
              const url=new URL(value),allowed=technology==='PostgreSQL'?['postgres:','postgresql:']:['redis:','rediss:'];
              if(allowed.includes(url.protocol)&&url.hostname) {
                const endpoint=url.protocol+'//'+url.host+url.pathname;
                resource=entity('storage','client-resource:'+endpoint,technology+' · '+url.hostname,{technology,identity:'Source-configured destination; not verified deployment',
                  application_id:owner(r).id,evidence_ids:[ev(sf,prop,'client-resource-url')]});
              }
            }catch{}
            clients.set(s,{resource,technology,evidence:[ev(sf,init,'resource-client-construction'),...imported.evidence,
              ...definitions.map(d=>ev(d.getSourceFile(),d,'resource-value-definition'))]});
          }
        }
      }
      ts.forEachChild(n,constructors);
    }constructors(sf);
  }
  for(const sf of sources) {
    if(dynamicScopeFiles.has(sf))continue;
    const r=rel(sf.fileName), envs=new Map();
    for(const statement of sf.statements)if(ts.isExportAssignment(statement)&&!statement.isExportEquals) {
      const object=unwrap(statement.expression);
      if(object&&ts.isObjectLiteralExpression(object))for(const member of object.properties) {
        const fn=ts.isMethodDeclaration(member)?member:ts.isPropertyAssignment(member)?unwrap(member.initializer):null;
        if(member.name?.text==='fetch'&&fn?.body&&ts.isIdentifier(fn.parameters?.[1]?.name))envs.set(symbol(fn.parameters[1].name),ev(sf,fn.parameters[1],'worker-fetch-environment'));
      }
    }
    function operations(n) {
      if(ts.isCallExpression(n)&&ts.isPropertyAccessExpression(n.expression)) {
        const receiver=unwrap(n.expression.expression),operation=n.expression.name.text,support=ev(sf,n,'resource-operation'),caller=enclosing(n);
        const client=ts.isIdentifier(receiver)?clients.get(symbol(receiver)):null;
        if(client&&(client.technology==='PostgreSQL'?operation==='query':['get','set','del','mGet','mSet','hGet','hSet','incr','expire','publish','subscribe'].includes(operation))) {
          if(client.resource)edge(caller,client.resource,'USES_RESOURCE',[support,...client.evidence],{callsite:support,resolution:'conditional',operation,
            derivation:'Bound client construction and source-configured destination; invocation/delivery not established'});
          else unknowns.push({kind:'resource',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:'Bound '+client.technology+' operation; destination configuration unavailable or unsupported',evidence_ids:[support,...client.evidence]});
        }
        if(receiver&&ts.isPropertyAccessExpression(receiver)&&ts.isIdentifier(receiver.expression)&&['get','put','delete','head','list','createMultipartUpload','resumeMultipartUpload'].includes(operation)) {
          const s=symbol(receiver.expression),envSupport=envs.get(s);
          if(envSupport&&!changed.has(s)) {
            const candidates=(entries.get(r)||[]).filter(b=>b.binding===receiver.name.text), profiles=new Map();
            for(const binding of candidates) {if(!profiles.has(binding.profile))profiles.set(binding.profile,[]);profiles.get(binding.profile).push(binding);}
            for(const [profile,bindings] of profiles) {
              if(bindings.length!==1) {unknowns.push({kind:'resource',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,
                resolution:'ambiguous',candidate_ids:[...new Set(bindings.map(b=>b.target))].sort(),profile,
                reason:'Multiple configured R2 targets for the same binding/profile',evidence_ids:[support,envSupport,...bindings.flatMap(b=>b.evidence_ids)]});continue;}
              const binding=bindings[0];edge(caller,binding.target,'USES_RESOURCE',
                [support,envSupport,...binding.evidence_ids],{callsite:support,profile,resolution:'conditional',operation,binding:binding.binding,
                  support_edge_ids:[binding.id,binding.entry_edge_id],derivation:'Configured Worker entry, fetch env parameter and matching R2 binding; profile-specific static use, not runtime delivery'});
            }
          }
        }
      }
      ts.forEachChild(n,operations);
    }operations(sf);
  }
};
