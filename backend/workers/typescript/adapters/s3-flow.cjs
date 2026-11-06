'use strict';
module.exports=function(api){
  const {ts,sources,checker,symbol,unwrap,texts,path,rel,ev,id,importBindings,isExternal,owner,entity,edge,enclosing}=api;
  const flow=require('./flow.cjs')(api),operations=[],reported=new Set();
  function unresolved(n,reason){const support=ev(n.getSourceFile(),n,'s3-operation-unresolved'),key=support+'|'+reason;
    if(reported.has(key))return;reported.add(key);
    api.unknowns.push({kind:'resource',file:rel(n.getSourceFile().fileName),line:n.getSourceFile().getLineAndCharacterOfPosition(n.getStart()).line+1,
      reason,provider:'trusted-ts-flow',resolution:'unresolved',evidence_ids:[support]});
  }
  for(const sf of sources){function visit(n){
    if(ts.isCallExpression(n)&&ts.isPropertyAccessExpression(n.expression)&&n.expression.name.text==='send'&&n.arguments.length){
      for(const context of flow.operationContexts(n))operations.push({n,context,receiver:flow.expression(n.expression.expression,context),command:flow.expression(n.arguments[0],context)});
    }ts.forEachChild(n,visit);
  }visit(sf);}
  flow.solve();
  const supported=new Map([['GetObjectCommand','read'],['PutObjectCommand','write'],['DeleteObjectCommand','delete'],['HeadObjectCommand','metadata'],['ListObjectsV2Command','list']]);
  const questions=[];
  for(const op of operations){
    const clients=flow.values(op.receiver),commands=flow.values(op.command);
    const knownClients=clients.filter(v=>v.kind==='instance'&&v.package==='@aws-sdk/client-s3'&&v.path.join('.')==='S3Client');
    const knownCommands=commands.filter(v=>v.kind==='instance'&&v.package==='@aws-sdk/client-s3'&&supported.has(v.path.join('.')));
    if(!knownClients.length)continue;
    if(!knownCommands.length){unresolved(op.n,'Bound S3 client; command identity unavailable or unsupported');continue;}
    // Unknown alternatives prevent a destination claim; null cache states are allowed as conditional initialization.
    const uncertain=clients.some(v=>v.kind==='unknown'&&v.reason!=='undefined alternative')||commands.some(v=>v.kind==='unknown'&&v.reason!=='undefined alternative');
    if(uncertain){unresolved(op.n,'S3 operation has unknown client or command alternatives');continue;}
    for(const cmd of knownCommands){const allocation=flow.allocationNodes.get(cmd.site);if(!allocation?.arguments?.[0])continue;
      questions.push({...op,cmd,bucket:flow.property(allocation.arguments[0],'Bucket',cmd.context)});
    }
  }
  flow.solve();
  for(const q of questions){
    const values=flow.values(q.bucket),destinations=values.filter(v=>v.kind==='environment'||v.kind==='literal');
    if(!destinations.length){unresolved(q.n,'S3 operation bucket value unavailable or analysis bound reached');continue;}
    const incomplete=values.some(v=>v.kind==='unknown'&&v.reason!=='undefined alternative');
    // Never silently discard an unknown possible destination to make a unique resource.
    if(incomplete){unresolved(q.n,'S3 bucket has unknown alternatives; no unique destination claimed for this context');continue;}
    const proof=flow.proof([q.receiver,q.command,q.bucket]);
    for(const destination of destinations){
      const sf=q.n.getSourceFile(),r=rel(sf.fileName),application=owner(r).id;
      const key=JSON.stringify([application,'s3-compatible',destination]);
      const target=entity('storage',key,destination.kind==='environment'?'Object storage · '+destination.name:'Object storage bucket · '+destination.value,
        {technology:'S3-compatible object storage',application_id:application,identity:'Logical source-configured bucket reference; deployment not established',
          configuration:destination,evidence_ids:proof.evidence_ids,resolution:'conditional'});
      edge(enclosing(q.n),target,'USES_RESOURCE',[ev(sf,q.n,'s3-command-operation'),...proof.evidence_ids],
        {callsite:ev(sf,q.n,'s3-command-operation'),resolution:destinations.length>1?'ambiguous':'conditional',operation:supported.get(q.cmd.path.join('.')),command:q.cmd.path[0],
          provider:'trusted-ts-flow',derivation_version:'bounded-flow-1',...proof,
          flow_context_id:q.context?id('flow-context',q.context):undefined,
          context_callsite:q.context?ev(flow.contextCall(q.context).getSourceFile(),flow.contextCall(q.context),'callsite'):undefined,
          analysis_partial:flow.partial,
          derivation:'Bound S3 client and command allocation, returned receiver flow and Bucket value; logical configuration, not deployed resource',
          limitation:'Possible source operation; branch feasibility, delivery and cloud account are not established'});
    }
  }
  return flow.report();
};
