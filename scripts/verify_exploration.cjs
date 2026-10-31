// Acceptance over an existing saved graph; never submits or reanalyzes target source.
const fs=require('node:fs'),path=require('node:path');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const root=path.resolve(__dirname,'..'),output=path.join(root,'output/usability');
fs.mkdirSync(output,{recursive:true});
const sid='8b14186f6aec18085a25f11c5e1198612708b226793c6aae190c7fa977198b2a';
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1900,height:1250}}),errors=[];
  let analysisSubmissions=0;
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('request',r=>{const u=new URL(r.url());if(r.method()==='POST'&&u.pathname.includes('/analyze/'))analysisSubmissions++;if(['http:','https:'].includes(u.protocol)&&!['127.0.0.1','localhost'].includes(u.hostname))errors.push('External page request: '+u.hostname)});
  page.on('response',async r=>{if(r.status()>=400&&r.url().includes('/api/'))errors.push('API '+r.status()+' '+r.url())});
  await page.goto(process.env.APP_URL||'http://127.0.0.1:5175/');
  await page.locator('.history button').filter({hasText:sid.slice(0,12)}).click();
  await page.getByRole('heading',{name:'gitdiagram',exact:true}).waitFor();
  await page.locator('.react-flow__node').first().waitFor();
  const defaultNodes=await page.locator('.react-flow__node').count(),defaultEdges=await page.locator('.react-flow__edge').count();
  if(defaultNodes>24||defaultEdges>24)throw Error('Default view exceeded presentation caps');
  if(await page.locator('.node-kind').filter({hasText:/^FUNCTION$|^METHOD$|^CLASS$|^file$|^endpoint$/}).count())throw Error('Low-level records leaked into default diagram');
  if(await page.locator('.node-kind').filter({hasText:'LOGICAL MODULE'}).count()<3)throw Error('Major modules are missing');
  await page.screenshot({path:path.join(output,'system-overview.png'),fullPage:true});
  await page.locator('.diagram').screenshot({path:path.join(output,'system-diagram.png')});
  await page.locator('.hierarchy-items button[data-entity-id="application:cdb4ee2aea69cc6a8333"]').click();
  await page.getByRole('heading',{name:'Logical modules',exact:true}).waitFor();
  await page.locator('.hierarchy-items strong').getByText('storage',{exact:true}).waitFor();
  await page.locator('.hierarchy-items strong').getByText('generate',{exact:true}).click();
  await page.getByRole('heading',{name:'Functions & classes',exact:true}).waitFor();
  await page.locator('.node-kind').filter({hasText:/FUNCTION|METHOD/}).first().waitFor();
  await page.waitForFunction(()=>document.querySelectorAll('.react-flow__edge').length>0);
  const workflowNodes=await page.locator('.react-flow__node').count();
  // Click an actual routed stroke, avoiding the empty center of its SVG bounding box.
  const edge=page.locator('.react-flow__edge-interaction').first();
  const point=await edge.evaluate(el=>{const p=el.getPointAtLength(el.getTotalLength()*.5);const pt=el.ownerSVGElement.createSVGPoint();pt.x=p.x;pt.y=p.y;const q=pt.matrixTransform(el.getScreenCTM());return{x:q.x,y:q.y}});
  await page.mouse.click(point.x,point.y);
  await page.getByRole('complementary',{name:'Evidence inspector'}).waitFor();
  await page.getByText('Caller / source',{exact:true}).waitFor();
  await page.locator('.citation').first().waitFor();
  await page.waitForFunction(()=>{const box=document.querySelector('.diagram').getBoundingClientRect();return [...document.querySelectorAll('.react-flow__node')].every(n=>{const r=n.getBoundingClientRect();return r.left>=box.left&&r.right<=box.right&&r.top>=box.top&&r.bottom<=box.bottom})});
  await page.screenshot({path:path.join(output,'module-workflow.png'),fullPage:true});
  await page.locator('.diagram').screenshot({path:path.join(output,'workflow-diagram.png')});
  await page.getByRole('button',{name:'Close inspector',exact:true}).click();
  await page.locator('.hierarchy-items strong').getByText('admitGenerationRequest',{exact:true}).click();
  await page.locator('.node-label').getByText('admitGenerationRequest',{exact:true}).waitFor();
  await page.getByRole('button',{name:/^Needs context/}).click();
  await page.locator('.issue-row').first().click();
  await page.locator('.evidence-panel .status-badge.unresolved').waitFor();
  await page.locator('.citation').first().waitFor();
  await page.screenshot({path:path.join(output,'unresolved-reference.png'),fullPage:true});
  await page.getByRole('button',{name:'Detailed diagnostics & tools',exact:true}).click();
  await page.getByText('Current backend environment',{exact:true}).waitFor();
  await page.locator('.tool-matrix').waitFor();
  await page.screenshot({path:path.join(output,'runtime-tools.png'),fullPage:true});
  await page.getByRole('button',{name:'Architecture explorer',exact:true}).click();
  await page.getByRole('button',{name:'System architecture',exact:true}).click();
  await page.locator('.react-flow__node').first().waitFor();
  await page.locator('.history button').filter({hasText:sid.slice(0,12)}).click();
  await page.locator('.node-kind').filter({hasText:'LOGICAL MODULE'}).first().waitFor();
  await page.reload();
  await page.getByRole('heading',{name:'gitdiagram',exact:true}).waitFor();
  await page.locator('.node-kind').filter({hasText:'LOGICAL MODULE'}).first().waitFor();
  if(await page.evaluate(()=>localStorage.getItem('analysis-id'))!==sid)throw Error('Snapshot changed on reopen');
  if(process.env.VERIFY_ZIP==='1'){
    const priorFixture=page.locator('.history button').filter({hasText:/^known-system/});
    if(await priorFixture.count()){
      await priorFixture.first().click();
      await page.getByRole('heading',{name:'known-system',exact:true}).waitFor();
      await page.locator('.react-flow__node').first().waitFor();
      await page.getByRole('button',{name:'Core workflow',exact:true}).click();
      await page.locator('.node-kind').filter({hasText:/FUNCTION|METHOD/}).first().waitFor();
    }
    await page.getByLabel('Repository ZIP').setInputFiles(path.join(root,'tmp/known-system.zip'));
    await page.getByRole('heading',{name:'known-system',exact:true}).waitFor({timeout:120000});
    await page.waitForFunction(()=>document.querySelector('.tabs button.active')?.textContent==='System architecture',undefined,{timeout:120000});
    await page.locator('.react-flow__node').first().waitFor();
    await page.locator('.history button').filter({hasText:sid.slice(0,12)}).click();
    await page.getByRole('heading',{name:'gitdiagram',exact:true}).waitFor();
  }
  if(errors.length)throw Error(errors.join('\n'));
  if(analysisSubmissions!==(process.env.VERIFY_ZIP==='1'?1:0))throw Error('Unexpected number of analysis submissions');
  const result={snapshot_id:sid,default_nodes:defaultNodes,default_edges:defaultEdges,workflow_nodes:workflowNodes,hierarchy_levels:['repository','package','component','function/class'],module:'generate',relationship_evidence:true,unresolved_reference_inspected:true,two_views_switched:true,reopened:true,analysis_submissions:analysisSubmissions,page_errors:errors};
  fs.writeFileSync(path.join(output,process.env.VERIFY_ZIP==='1'?'browser-roundtrip.json':'browser-acceptance.json'),JSON.stringify(result,null,2));console.log(JSON.stringify(result,null,2));
 }finally{await browser.close()}
})().catch(e=>{console.error(e);process.exitCode=1});
