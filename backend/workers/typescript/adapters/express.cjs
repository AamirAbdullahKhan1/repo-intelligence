'use strict';
// Narrow Express receiver/route adapter. Mount prefixes and dynamic registrations remain unknown.
module.exports = function({ts,sources,symbol,importBindings,assignments,unwrap,ev,entity,edge,rel,owner,component,fileIds,symbolEntity,routes,checker,unknowns}) {
  function expressReceiver(expression) {
    if(!ts.isIdentifier(expression))return false;
    const binding=symbol(expression);
    if(!binding || assignments.has(binding))return false;
    const declaration=binding.valueDeclaration;
    if(!declaration || !ts.isVariableDeclaration(declaration))return false;
    const initializer=unwrap(declaration.initializer);
    if(!initializer || !ts.isCallExpression(initializer))return false;
    const constructor=initializer.expression;
    const origin=importBindings.get(symbol(ts.isPropertyAccessExpression(constructor)?constructor.expression:constructor));
    return origin?.package==='express' && ['default','*','Router'].includes(origin.name) && !origin.typeOnly && (!ts.isPropertyAccessExpression(constructor)||constructor.name.text==='Router');
  }
  for(const sf of sources) {
    const r=rel(sf.fileName);
    function visit(n) {
      if(ts.isCallExpression(n)&&ts.isPropertyAccessExpression(n.expression)&&expressReceiver(n.expression.expression)) {
        const method=n.expression.name.text.toUpperCase();
        if(/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS|ALL)$/.test(method)) {
          const arg=n.arguments[0],support=ev(sf,n,'express-route-registration');
          if(arg && ts.isStringLiteralLike(arg)) {
            const rid=entity('endpoint',r+':express:'+n.getStart(sf),method+' '+arg.text,{file:r,method,path:arg.text,application_id:owner(r).id,component_id:component(r),evidence_ids:[support]});
            routes.push({id:rid,file:r,method,path:arg.text,evidence_ids:[support],qualification:'Router mount prefix and runtime reachability not evaluated'});
            edge(fileIds.get(r),rid,'REGISTERS_ROUTE',[support],{derivation:'Express receiver constructed from bound express import; literal local route path'});
            for(const handler of n.arguments.slice(1)) {
              let declaration=handler;
              if(ts.isIdentifier(handler)) {
                let s=symbol(handler);
                if(s?.flags & ts.SymbolFlags.Alias) {try{s=checker.getAliasedSymbol(s)}catch{}}
                declaration=s?.valueDeclaration;
                if(declaration&&ts.isVariableDeclaration(declaration))declaration=unwrap(declaration.initializer);
              }
              if(declaration?.body) {
                const sid=symbolEntity(declaration);
                if(sid)edge(rid,sid,'HANDLED_BY',[support,ev(declaration.getSourceFile(),declaration,'express-handler-implementation')],{derivation:'Registered local handler; middleware order/control flow not modeled'});
              } else unknowns.push({kind:'handler',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:'Express handler implementation unavailable',evidence_ids:[support]});
            }
          } else unknowns.push({kind:'route',file:r,line:sf.getLineAndCharacterOfPosition(n.getStart(sf)).line+1,reason:'Dynamic Express route path',evidence_ids:[support]});
        }
      }
      ts.forEachChild(n,visit);
    }
    visit(sf);
  }
};
