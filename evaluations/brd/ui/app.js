const $ = id => document.getElementById(id);
let configuration, current, view = 'report', filename = 'pasted-brd.md', running = false;
async function api(path, options) {
  const response = await fetch(path, options);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || 'Request failed.');
  return data;
}
function node(tag, text, className) {const e = document.createElement(tag); if (text !== undefined) e.textContent = text; if (className) e.className = className; return e;}
function count() {$('count').textContent = `${$('document').value.length.toLocaleString()} / 100,000 characters`; $('run').disabled = running || !configuration?.key_configured || !$('document').value.trim() || $('document').value.length > 100000 || !$('consent').checked;}
function download(name, content, type='text/plain') {const url=URL.createObjectURL(new Blob([content],{type}));const a=node('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
// Minimal Markdown renderer: generated HTML is never inserted or executed.
function renderMarkdown(text, target) {
  const lines=text.split('\n'); let fence=null, buffer=[], table=null;
  for (const line of lines) {
    if (line.startsWith('```')) {if(fence!==null){if(fence==='mermaid')target.append(node('p','Mermaid diagram source · download or edit this block to render it.','muted'));target.append(node('pre',buffer.join('\n')));fence=null;buffer=[];}else{fence=line.slice(3).trim();table=null;}continue;}
    if(fence!==null){buffer.push(line);continue;}
    if(/^\s*\|/.test(line)) {if(/^\s*\|?[\s:|-]+\|\s*$/.test(line))continue;const cells=line.trim().replace(/^\||\|$/g,'').split('|');if(!table){table=node('table');target.append(table);}const row=node('tr');for(const cell of cells)row.append(node(table.children.length?'td':'th',cell.trim()));table.append(row);continue;}
    table=null;if(!line.trim())continue;
    const heading=line.match(/^(#{1,6})\s+(.+)/);if(heading){target.append(node('h'+heading[1].length,heading[2]));continue;}
    const item=line.match(/^\s*(?:[-*]|\d+\.)\s+(.+)/);target.append(node('p',item?'• '+item[1]:line));
  }
  if(fence!==null)target.append(node('pre',buffer.join('\n')));
}
function render() {
  const target=$('result');target.replaceChildren();if(!current)return;
  if(view==='source')target.append(node('pre',current.report));
  else if(view==='model'){
    target.append(node('p','Canonical model: accepted interpretation proposals with evidence. Structural validity does not establish semantic correctness.','warning'));
    target.append(node('pre',current.intelligence_model?JSON.stringify(current.intelligence_model,null,2):'This is a v1 report. Run the skill again to generate a structured model.'));
  }
  else if(view==='ledger'){
    target.append(node('p','Source wording and locations are indexed by the runner before the model call. Cues are lexical hints, not final classifications.','muted'));
    if(!current.source_ledger)target.append(node('p','This v1 run has no source ledger.'));
    for(const source of current.source_ledger?.records||[]){target.append(node('h3',`${source.source_id} · ${source.requirement_id||source.kind} · L${source.start_line}-L${source.end_line}`),node('p',source.section,'muted'),node('pre',source.text));}
  }
  else if(view==='checks'){target.append(node('p',current.validation.scope,'warning'));target.append(node('pre',JSON.stringify({...current.validation,diagrams:undefined,usage:current.usage,duration_seconds:current.duration_seconds,skill:current.skill},null,2)));}
  else if(view==='diagrams'){
    target.append(node('p','Editable Mermaid sources are saved with the report. No document content is sent to a third-party diagram renderer.','muted'));
    if(!current.validation.diagrams.length)target.append(node('p','The model returned no complete Mermaid blocks.'));
    current.validation.diagrams.forEach((diagram,i)=>{target.append(node('h3',`Diagram ${i+1}`));const button=node('button','Download .mmd','secondary');button.onclick=()=>download(`diagram-${i+1}.mmd`,diagram);target.append(button,node('pre',diagram));});
  }else{for(const warning of current.validation.warnings)target.append(node('p',warning,'warning'));renderMarkdown(current.report,target);}
}
async function history() {const records=await api('/api/runs');$('history').replaceChildren();if(!records.length)$('history').append(node('p','No saved runs yet.','muted'));for(const record of records){const b=node('button',`v${record.runner_version||'1.0'} · ${record.skill==='repository-analysis'?'Repository':'AI inventory'} · ${record.filename}\n${new Date(record.created_at).toLocaleString()}`,'history-item');b.onclick=async()=>{try{show(await api('/api/runs/'+record.id));}catch(e){$('status').textContent=e.message;}};$('history').append(b);}}
function show(data) {current=data;$('download').disabled=false;$('metadata').disabled=false;$('audit').disabled=!(data.audit_report||data.audit_available);render();$('status').textContent=`Saved v${data.runner_version||'1.0'} · ${data.reprocess_of?'local revalidation '+data.duration_seconds+'s; original analysis '+data.original_analysis_seconds+'s':data.duration_seconds+'s'} · ${data.validation.citation_count} citations · ${data.validation.diagram_count} diagrams` + (data.intelligence_model?' · semantic review required':' · legacy report');}
$('document').addEventListener('input',count);$('consent').addEventListener('change',count);
$('file').onchange=async event=>{const file=event.target.files[0];if(!file)return;if(!/\.(md|txt)$/i.test(file.name)||file.size>400000){$('status').textContent='Choose a .md or .txt file under 400 KB. Paste extracted text for PDF or Word documents.';return;}$('document').value=await file.text();filename=file.name;$('filename').textContent=filename;count();};
$('sample').onclick=async()=>{try{$('document').value=(await api('/api/sample')).text;filename='ServiceBridge-BRD.md';$('filename').textContent=filename;count();}catch(e){$('status').textContent=e.message;}};
$('run').onclick=async()=>{running=true;count();$('status').textContent='Indexing source statements…';try{const run=await api('/api/runs',{method:'POST',headers:{'Content-Type':'application/json','X-Session-Token':configuration.token},body:JSON.stringify({text:$('document').value,filename,skill:document.querySelector('[name=skill]:checked').value,consent:$('consent').checked})});let result;do{await new Promise(resolve=>setTimeout(resolve,1200));result=await api('/api/runs/'+run.id);if(result.stage)$('status').textContent=result.stage+'…';}while(result.status==='running');if(result.status==='failed')throw new Error(result.error);show(result);await history();}catch(e){$('status').textContent=e.message;}finally{running=false;count();}};
document.querySelectorAll('.tab').forEach(button=>button.onclick=()=>{view=button.dataset.view;document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b===button));if(current)render();});
$('download').onclick=()=>download(`${current.skill}-${current.id.slice(0,8)}.md`,current.report,'text/markdown');$('metadata').onclick=()=>download(`result-${current.id.slice(0,8)}.json`,JSON.stringify(current,null,2),'application/json');
$('audit').onclick=async()=>{try{let text=current.audit_report;if(!text){const response=await fetch(`/api/runs/${current.id}/audit`);if(!response.ok)throw new Error('Audit report is unavailable.');text=await response.text();}download(`audit-${current.id.slice(0,8)}.md`,text,'text/markdown');}catch(error){$('status').textContent=error.message;}};
(async()=>{try{configuration=await api('/api/config');$('lab-version').textContent=`BRD evaluation lab v${configuration.runner_version||'1.0'}`;$('deployment').textContent=configuration.deployment;$('version').textContent=configuration.api_version;$('credentials').textContent=configuration.key_configured?'Key configured on server':'Key required';$('endpoint').textContent=configuration.endpoint;$('status').textContent=configuration.key_configured?'Select a BRD and confirm data sharing to begin.':'Add your key to .env and refresh to enable analysis.';count();await history();}catch(e){$('status').textContent=e.message;}})();
