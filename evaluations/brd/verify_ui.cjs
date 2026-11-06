// Browser verification with fake API results. Never calls Azure or requires a key.
const {chromium}=require(process.env.PLAYWRIGHT_MODULE || 'playwright');
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try {
  const page=await browser.newPage({viewport:{width:1440,height:1000}}), errors=[], external=[];
  // Serve the exact local UI through interception so this test also works in
  // environments that isolate the browser from loopback server processes.
  await page.route('http://127.0.0.1:8766/**',route=>{
   const pathname=new URL(route.request().url()).pathname;
   const assets={'/':['index.html','text/html'],'/app.js':['app.js','text/javascript'],'/style.css':['style.css','text/css']};
   if(assets[pathname])return route.fulfill({body:fs.readFileSync(path.join(__dirname,'ui',assets[pathname][0])),contentType:assets[pathname][1]});
   if(pathname==='/api/config')return route.fulfill({json:{deployment:'GPT-4.1',api_version:'2025-03-01-preview',key_configured:false,token:'fake',endpoint:'https://example.openai.azure.com/'}});
   if(pathname==='/api/sample')return route.fulfill({json:{text:fs.readFileSync(path.resolve(__dirname,'../../docs/fixtures/brd/ServiceBridge-BRD.md'),'utf8')}});
   if(pathname==='/api/runs')return route.fulfill({json:[]});
   return route.fulfill({status:404,json:{error:'Not found'}});
  });
  page.on('pageerror',error=>errors.push(String(error)));
  page.on('request',request=>{if(!request.url().startsWith('http://127.0.0.1:8766'))external.push(request.url());});
  await page.goto('http://127.0.0.1:8766');
  await page.getByText('Key required',{exact:true}).waitFor();
  assert.equal(await page.locator('#run').isDisabled(),true);
  await page.locator('#sample').click();
  await page.waitForFunction(()=>document.getElementById('document').value.includes('ServiceBridge'));
  const sample=await page.locator('#document').inputValue();
  assert(sample.includes('NOTE-01'));
  // Enable a simulated connection in this browser only, not the actual server.
  await page.route('**/api/config',route=>route.fulfill({json:{deployment:'GPT-4.1',api_version:'2025-03-01-preview',key_configured:true,token:'fake',endpoint:'https://example.openai.azure.com/'}}));
  const report='# Intended architecture\nClaim [L1-L2].\n<script>window.injected=true</script>\n```mermaid\nflowchart LR\nA["Employee"] --> B["Portal"]\n```';
  const result={id:'a'.repeat(32),status:'completed',runner_version:'2.1',audit_available:true,skill:'repository-analysis',filename:'sample.md',created_at:new Date().toISOString(),report,duration_seconds:1,usage:{total_tokens:100},intelligence_model:{schema_version:'2.1',entities:[],coverage:{source_blocks:1},validation:{semantic_status:'not_verified'}},source_ledger:{records:[{source_id:'S00001',kind:'statement',start_line:1,end_line:1,section:'Document',text:'Test source wording'}]},validation:{scope:'Structural checks only.',warnings:[],citation_count:1,diagram_count:1,diagrams:['flowchart LR\nA --> B'],partial:false}};
  let submitted;
  await page.route('**/api/runs',route=>{if(route.request().method()==='POST'){submitted=route.request().postDataJSON();return route.fulfill({status:202,json:{id:result.id,status:'running'}});}return route.fulfill({json:submitted?[result]:[]});});
  await page.route('**/api/runs/'+result.id,route=>route.fulfill({json:result}));
  await page.route('**/api/runs/'+result.id+'/audit',route=>route.fulfill({body:'# Complete audit\nEvidence register',contentType:'text/markdown'}));
  await page.reload();
  await page.locator('#sample').click();
  await page.locator('#consent').check();
  await page.locator('#run').click();
  await page.getByRole('heading',{name:'Intended architecture',exact:true}).waitFor();
  assert.equal(await page.evaluate(()=>window.injected),undefined);
  assert.equal(submitted.consent,true);
  assert.equal(submitted.skill,'repository-analysis');
  assert(!submitted.text.includes('Expected findings'));
  await page.getByRole('button',{name:'Diagram sources',exact:true}).click();
  await page.getByRole('button',{name:'Download .mmd',exact:true}).waitFor();
  const download=page.waitForEvent('download');await page.locator('#download').click();assert((await download).suggestedFilename().endsWith('.md'));
  const auditDownload=page.waitForEvent('download');await page.locator('#audit').click();assert((await auditDownload).suggestedFilename().startsWith('audit-'));
  await page.getByRole('button',{name:'Evidence checks',exact:true}).click();
  await page.getByText('Structural checks only.',{exact:true}).waitFor();
  await page.getByRole('button',{name:'Structured model',exact:true}).click();
  await page.getByText(/Canonical model: accepted/).waitFor();
  await page.getByRole('button',{name:'Source ledger',exact:true}).click();
  await page.getByText('Test source wording',{exact:true}).waitFor();
  await page.locator('.history-item').click();
  await page.getByRole('button',{name:'Report',exact:true}).click();
  const out=path.join(__dirname,'results','ui-verification');fs.mkdirSync(out,{recursive:true});
  await page.screenshot({path:path.join(out,'desktop.png'),fullPage:true});
  await page.setViewportSize({width:390,height:844});
  assert(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth));
  await page.screenshot({path:path.join(out,'mobile.png'),fullPage:true});
  assert.deepEqual(errors,[]);assert.deepEqual(external,[]);
  console.log(JSON.stringify({sample:true,missingKeyGuard:true,mockedRun:true,htmlInjectionBlocked:true,markdownDownload:true,auditDownload:true,history:true,mobile:true,externalRequests:external.length,errors}));
 }finally{await browser.close();}
})().catch(error=>{console.error(error);process.exit(1);});
