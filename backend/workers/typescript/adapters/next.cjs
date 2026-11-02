'use strict';
module.exports = function({ts,r,sf,fid,ev,entity,edge,owner,component,symbolEntity,routes}) {
  // Next convention: registration derived from supplied route modules, no Next build/config execution.
  const pkg=owner(r), local=pkg.root==='.' ? r : r.slice(pkg.root.length+1);
  const match=/^(?:src\/)?app\/(?:(.*)\/)?route\.[jt]s$/.exec(local);
  if(match) {
    const routePath='/'+(match[1]||'').split('/').filter(x=>!/^\(.*\)$/.test(x)&&!x.startsWith('@')).join('/');
    for(const statement of sf.statements) {
      const exported=statement.modifiers?.some(x=>x.kind===ts.SyntaxKind.ExportKeyword);
      const names=ts.isFunctionDeclaration(statement)&&statement.name ? [statement.name.text] : ts.isVariableStatement(statement) ? statement.declarationList.declarations.map(x=>x.name.getText(sf)) : [];
      if(!exported)continue;
      for(const method of names.filter(x=>/^(GET|POST|PUT|PATCH|DELETE|HEAD|OPTIONS)$/.test(x))) {
        const support=ev(sf,statement,'next-route-export'), rid=entity('endpoint',`${r}:${method}`,`${method} ${routePath}`,{file:r,method,path:routePath,application_id:owner(r).id,component_id:component(r),evidence_ids:[support]});
        routes.push({id:rid,file:r,method,path:routePath,evidence_ids:[support]});
        const declaration=ts.isFunctionDeclaration(statement) ? statement : statement.declarationList.declarations.find(x=>x.name.getText(sf)===method)?.initializer;
        if(declaration?.body)edge(rid,symbolEntity(declaration),'HANDLED_BY',[support],{derivation:'exported Next route implementation; static convention'});
 edge(fid,rid,'REGISTERS_ROUTE',[support],{derivation:'Next app-route convention; rewrites/middleware/runtime reachability not evaluated'});
      }
    }
  }
};
