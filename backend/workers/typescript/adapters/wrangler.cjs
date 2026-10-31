'use strict';
module.exports = function({texts,json,ts,rel,ev,literal,entity,edge,contained,fileIds,unknowns,path}) {
// Deployment declarations are a separate projection. Each config is its own profile.
for(const p of texts.keys()) if(/(?:^|[\\/])wrangler[^\\/]*\.jsonc?$/.test(p)) {
  const cfg=json(p);if(!cfg?.name)continue;
  const sf=ts.createSourceFile(p,texts.get(p),ts.ScriptTarget.Latest,true,ts.ScriptKind.JSON), profile=rel(p);
  function propertyEvidence(key,value) {
    let found=sf;const visit=n=>{if(ts.isPropertyAssignment(n)&&n.name.getText(sf).replace(/["']/g,'')===key && (value===undefined||literal(n.initializer)===value))found=n;ts.forEachChild(n,visit);};visit(sf);
    return ev(sf,found,'wrangler-'+key,'infrastructure');
  }
  const configEv=propertyEvidence('name',cfg.name), unit=entity('deployable',cfg.name,cfg.name,{profile,entry:cfg.main||null,evidence_ids:[configEv],scope:cfg.name.includes('test')||profile.includes('staging')?'alternative/test':'declared'});
  const entry=cfg.main&&path.resolve(path.dirname(p),cfg.main);
  if(entry&&contained(entry)&&texts.has(entry))edge(unit,fileIds.get(rel(entry))||entity('file',rel(entry),rel(entry),{file:rel(entry),evidence_ids:[]}), 'ENTRYPOINT',[propertyEvidence('main',cfg.main)],{profile});
  else if(cfg.main)unknowns.push({kind:'entrypoint',file:profile,reason:'configured entry file unavailable (possibly generated)',evidence_ids:[propertyEvidence('main',cfg.main)]});
  for(const item of cfg.services||[]) {
    const tid=entity('deployable',item.service,item.service,{evidence_ids:[propertyEvidence('service',item.service)],scope:'declared binding target'});
    edge(unit,tid,'BINDS_SERVICE',[propertyEvidence('service',item.service)],{profile,binding:item.binding,derivation:'service binding declaration; invocation not established'});
  }
  for(const item of cfg.tail_consumers||[]) {
    const tid=entity('deployable',item.service,item.service,{evidence_ids:[propertyEvidence('service',item.service)]});
    edge(unit,tid,'CONFIGURES_LOG_SINK',[propertyEvidence('service',item.service)],{profile,derivation:'tail-consumer declaration, not observed log delivery'});
  }
  for(const item of cfg.r2_buckets||[]) {
    const rid=entity('storage',item.bucket_name,item.bucket_name,{technology:'R2 bucket',evidence_ids:[propertyEvidence('bucket_name',item.bucket_name)]});
    edge(unit,rid,'BINDS_RESOURCE',[propertyEvidence('bucket_name',item.bucket_name)],{profile,binding:item.binding});
  }
  const sqliteClasses=new Set((cfg.migrations||[]).flatMap(m=>m.new_sqlite_classes||[]));
  for(const item of cfg.durable_objects?.bindings||[]) {
    const key=item.script_name||cfg.name;const rid=entity('storage',key+':'+item.class_name,item.class_name,{technology:sqliteClasses.has(item.class_name)?'SQLite-backed Durable Object':'Durable Object / container binding',evidence_ids:[propertyEvidence('class_name',item.class_name)]});
    edge(unit,rid,'BINDS_RESOURCE',[propertyEvidence('class_name',item.class_name)],{profile,binding:item.name});
  }
  for(const item of cfg.containers||[]) {
    const targetId=entity('container',cfg.name+':'+item.class_name,item.class_name,{image:item.image,profile,evidence_ids:[propertyEvidence('class_name',item.class_name)]});
    edge(unit,targetId,'DECLARES_CONTAINER',[propertyEvidence('class_name',item.class_name)],{profile,derivation:'configured container role; runtime execution not observed'});
  }
}

};
