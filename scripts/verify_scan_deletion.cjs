// Destructive acceptance test ONLY against the disposable compiler-delete-review database.
const fs=require('node:fs'),path=require('node:path'),assert=require('node:assert/strict');
const {chromium}=require(process.env.PLAYWRIGHT_MODULE||'playwright');
const old=JSON.parse(fs.readFileSync('output/resource-responsibilities/gitdiagram-summary.json','utf8')).snapshot_id;
const fresh=JSON.parse(fs.readFileSync('output/compiler-library-fix/gitdiagram-summary.json','utf8')).snapshot_id;
const output=path.resolve('output/compiler-delete-review');
(async()=>{
 const browser=await chromium.launch({headless:true,channel:'chrome'});
 try{
  const page=await browser.newPage({viewport:{width:1600,height:1100}}),errors=[];
  let deletes=0,submissions=0;
  page.on('pageerror',e=>errors.push(String(e)));
  page.on('request',r=>{if(r.method()==='DELETE')deletes++;if(r.method()==='POST'&&r.url().includes('/analyze/'))submissions++;});
  await page.goto('http://127.0.0.1:5183/');
  await page.locator('.history-item > button').filter({hasText:old.slice(0,12)}).click();
  await page.getByText(/Older scan: this result predates/).waitFor();
  await page.locator('.history-item > button').filter({hasText:fresh.slice(0,12)}).click();
  await page.getByRole('heading',{name:'Overall architecture',exact:true}).waitFor();
  await page.locator('.react-flow__node').first().waitFor();
  assert.equal(await page.getByText(/Older scan: this result predates/).count(),0);
  await page.getByRole('button',{name:'Delete scan '+old.slice(0,12),exact:true}).click();
  await page.getByRole('button',{name:'Keep scan',exact:true}).click();
  assert.equal(deletes,0);
  await page.getByRole('button',{name:'Delete scan '+old.slice(0,12),exact:true}).click();
  await page.getByRole('button',{name:'Confirm delete',exact:true}).click();
  await page.getByRole('button',{name:'Delete scan '+old.slice(0,12),exact:true}).waitFor({state:'detached'});
  assert.equal(await page.evaluate(()=>localStorage.getItem('analysis-id')),fresh);
  await page.screenshot({path:path.join(output,'current-scan.png'),fullPage:true});
  await page.getByRole('button',{name:'Delete scan '+fresh.slice(0,12),exact:true}).click();
  await page.screenshot({path:path.join(output,'delete-confirmation.png'),fullPage:true});
  await page.getByRole('button',{name:'Confirm delete',exact:true}).click();
  await page.getByRole('heading',{name:'Start with the big picture.',exact:true}).waitFor();
  assert.equal(await page.evaluate(()=>localStorage.getItem('analysis-id')),null);
  await page.reload();
  await page.getByText('No saved snapshots yet.',{exact:true}).waitFor();
  assert.equal(deletes,2);assert.equal(submissions,0);assert.deepEqual(errors,[]);
  const report={cancel_does_not_delete:true,deleting_unselected_preserves_selection:true,deleting_selected_clears_canvas_and_storage:true,deletion_survives_reload:true,legacy_warning_verified:true,delete_requests:deletes,analysis_submissions:submissions,browser_errors:errors};
  fs.writeFileSync(path.join(output,'browser-results.json'),JSON.stringify(report,null,2));console.log(JSON.stringify(report,null,2));
 }finally{await browser.close();}
})().catch(e=>{console.error(e);process.exitCode=1;});
