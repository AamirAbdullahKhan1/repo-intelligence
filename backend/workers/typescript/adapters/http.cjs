'use strict';
// Same-package Next route candidates, not proof of runtime routing or delivery.
module.exports=function({ts,inventory,routes,edges,owner,ev,edge,literal,unwrap}) {
  const index=new Map(),configIndex=new Map();
  const handled=new Set(edges.filter(e=>e.kind==='HANDLED_BY').map(e=>e.source));
  for(const file of inventory)if(/(?:^|\/)(?:next\.config\.[^/]+|middleware\.[jt]s|proxy\.[jt]s)$/.test(file.path)) {
    const key=owner(file.path).id;if(!configIndex.has(key))configIndex.set(key,[]);configIndex.get(key).push(file.path);
  }
  for(const route of routes) {
    // Express paths omit mount prefixes; do not match them as full URLs.
    if(route.framework!=='next'||!handled.has(route.id))continue;
    const key=owner(route.file).id+'|'+route.method+'|'+route.path.split('/').filter(Boolean).length;
    if(!index.has(key))index.set(key,[]);index.get(key).push(route);
  }
  function method(n,definitions) {
    if(n.arguments.length<2)return 'GET';
    const init=unwrap(n.arguments[1]);if(!init||!ts.isObjectLiteralExpression(init))return null;
    let value='GET';
    for(const p of init.properties) {
      // Spreads/computed keys/accessors can replace the method; do not guess.
      if(!ts.isPropertyAssignment(p)&&!ts.isShorthandPropertyAssignment(p)||p.name&&ts.isComputedPropertyName(p.name))return null;
      if(p.name?.text==='method') {
        if(!ts.isPropertyAssignment(p))return null;
        value=literal(p.initializer,0,definitions);
        if(value===null||! /^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$/i.test(value))return null;
        value=value.toUpperCase();
      }
    }
    return value;
  }
  function matches(pattern,url) {
    const a=pattern.split('/').filter(Boolean), b=url.split('/').filter(Boolean);
    if(a.length!==b.length)return false;
    return a.every((part,i)=>part===b[i]||/^\[[^.[\]]+\]$/.test(part));
  }
  return function link({n,sf,r,caller,support,value,definitions}) {
    const pkg=owner(r), verb=method(n,definitions);
    const supports=[support,...definitions.map(d=>ev(d.getSourceFile(),d,'http-value-definition'))];
    const fail=(reason,extra={})=>({kind:'http',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,
      reason,evidence_ids:supports,...extra});
    if(!value||!value.startsWith('/')||value.startsWith('//')||/[\\\x00-\x20]/.test(value))return fail('Unsupported or non-local relative URL; origin not established');
    if(!verb)return fail('HTTP method or request options are dynamic/unsupported');
    let directive;
    for(const statement of sf.statements) {
      if(!ts.isExpressionStatement(statement)||!ts.isStringLiteral(statement.expression))break;
      if(statement.expression.text==='use client')directive=statement;
    }
    if(!directive||!(pkg.data.dependencies?.next||pkg.data.devDependencies?.next))return fail('Relative URL origin not established in a supported Next client module');
    const url=value.split(/[?#]/,1)[0];
    if(/%|\/\/|(?:^|\/)\.{1,2}(?:\/|$)/.test(url))return fail('Encoded, repeated-slash or dot-segment URL needs additional normalization');
    const candidates=(index.get(pkg.id+'|'+verb+'|'+url.split('/').filter(Boolean).length)||[]).filter(route=>matches(route.path,url));
    if(candidates.length!==1)return fail(candidates.length?'Multiple compatible route candidates':'No compatible supported route in the owning application',
      {resolution:candidates.length?'ambiguous':'unresolved',candidate_ids:candidates.map(x=>x.id).sort(),method:verb});
    const route=candidates[0];
    const client=ev(sf,directive,'next-client-module-boundary');
    const configs=configIndex.get(pkg.id)||[];
    edge(caller,route.id,'CALLS_HTTP',[...supports,client,...route.evidence_ids],{callsite:support,
      resolution:'conditional',target_scope:'internal',method:verb,
      derivation:'Unique method/path-compatible Next route in the same client application; candidate under same-origin routing',
      limitations:['Routing configuration, middleware, hosting origin, client invocation and runtime delivery are not established',
        ...(configs.length?['Routing/configuration files present; their effects are not evaluated']:[])],
      routing_config_files:[...configs].sort()});
    return null;
  };
};
