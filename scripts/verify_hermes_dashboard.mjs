#!/usr/bin/env node
// Offline Chrome/CDP proof with no npm dependency or HTTP listener in the plugin.
// modes: normal (assert four widths, contrast, keyboard, exports) | zoom (native
// 400% browser zoom preference) | capture (screenshots only, never acceptance).
import {spawn} from 'node:child_process';
import {createHash} from 'node:crypto';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [artifact,output,mode='normal']=process.argv.slice(2);
if(!artifact||!output)throw Error('Usage: node scripts/verify_hermes_dashboard.mjs file.html output [normal|zoom|capture]');
if(mode==='baseline')throw Error('baseline mode was retired: it is capture evidence, never acceptance. Use normal or zoom.');
if(!['normal','zoom','capture'].includes(mode))throw Error('Unknown mode '+mode);
const acceptance=mode!=='capture';
const artifactBytes=await readFile(resolve(artifact));
const artifactSha256=createHash('sha256').update(artifactBytes).digest('hex');
const captureManifest={artifact:resolve(artifact),artifactSha256,mode,captures:[]};
const captureSection=async(sessionCall,sessionEval,name,selector,width)=>{
 const rect=await sessionEval(`(()=>{const e=document.querySelector(${JSON.stringify(selector)});if(!e)return null;e.scrollIntoView({block:'start'});const r=e.getBoundingClientRect();return {x:Math.max(0,Math.floor(r.left+scrollX)),y:Math.max(0,Math.floor(r.top+scrollY)),width:Math.min(Math.ceil(r.width),3000),height:Math.min(Math.ceil(r.height),12000)}})()`);
 if(!rect||!rect.width||!rect.height)return;
 const shot=await sessionCall('Page.captureScreenshot',{format:'png',captureBeyondViewport:true,clip:{...rect,scale:1}});
 const buf=Buffer.from(shot.data,'base64');
 const file=`section-${name}-${width}.png`;
 await writeFile(resolve(output,file),buf);
 captureManifest.captures.push({file,sha256:createHash('sha256').update(buf).digest('hex'),width,section:name});
};
await mkdir(output,{recursive:true});
const profile=resolve(output,'chrome-profile');
await mkdir(resolve(profile,'Default'),{recursive:true});
if(mode==='zoom')await writeFile(resolve(profile,'Default/Preferences'),JSON.stringify({partition:{default_zoom_level:{x:Math.log(4)/Math.log(1.2)}}}));
const chrome=spawn(process.env.CHROME_PATH||'/usr/bin/google-chrome',['--headless=new','--no-sandbox','--disable-gpu','--disable-background-networking','--disable-component-update','--no-first-run','--no-default-browser-check','--window-size=1440,1000',`--user-data-dir=${profile}`,'--remote-debugging-port=0','about:blank'],{stdio:['ignore','ignore','pipe']});
let ws;
try{
 const endpoint=await new Promise((res,rej)=>{let text='';const timer=setTimeout(()=>rej(Error('Chrome startup timeout')),20000);chrome.stderr.on('data',x=>{text+=x;const m=text.match(/DevTools listening on (ws:\/\/\S+)/);if(m){clearTimeout(timer);res(m[1]);}});chrome.on('error',rej);});
 ws=new WebSocket(endpoint);await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
 let id=0;const pending=new Map(),requests=[],errors=[],downloads=[];
 ws.onmessage=({data})=>{const m=JSON.parse(data);if(m.id){const p=pending.get(m.id);pending.delete(m.id);m.error?p.reject(Error(JSON.stringify(m.error))):p.resolve(m.result);}else if(m.method==='Network.requestWillBeSent')requests.push(m.params.request.url);else if(m.method==='Runtime.exceptionThrown')errors.push(m.params.exceptionDetails.text);else if(m.method==='Log.entryAdded'&&m.params.entry.level==='error')errors.push(m.params.entry.text);else if(m.method==='Browser.downloadWillBegin')downloads.push(m.params.suggestedFilename);};
 const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params,...(sessionId?{sessionId}:{})}));});
 const {targetId}=await send('Target.createTarget',{url:'about:blank'});
 const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
 const call=(method,params={})=>send(method,params,sessionId);
 const evaluate=async expression=>{const r=await call('Runtime.evaluate',{expression,returnByValue:true});if(r.exceptionDetails)throw Error(r.exceptionDetails.text);return r.result.value;};
 const pause=()=>new Promise(r=>setTimeout(r,400));
 await call('Page.enable');await call('Runtime.enable');await call('Network.enable');await call('Log.enable');
 await call('Network.setBlockedURLs',{urls:['http://*','https://*']});
 await mkdir(resolve(output,'downloads'),{recursive:true});
 await send('Browser.setDownloadBehavior',{behavior:'allow',downloadPath:resolve(output,'downloads'),eventsEnabled:true});
 const measurements=[];
 for(const width of mode==='zoom'?[1440]:[1440,885,820,768,753,390,320]){
  if(mode!=='zoom')await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(resolve(artifact)).href});await pause();
  const measure=await evaluate(`(()=>{const r={width:innerWidth,outerWidth,scrollWidth:document.documentElement.scrollWidth,dpr:devicePixelRatio,injected:!!window.GROCERY_INJECTED,heading:document.querySelector('h1')?.textContent,details:document.querySelectorAll('details').length,corrections:!!document.querySelector('#correction-item')};return r})()`);
  if(measure.injected)throw Error('Hostile fixture executed');
  if(acceptance&&measure.scrollWidth>measure.width)throw Error('Collapsed viewport overflow '+JSON.stringify(measure));
  if(mode==='zoom'&&measure.dpr<3.9)throw Error('Native browser zoom preference did not take effect: '+JSON.stringify(measure));
  measure.fold=await evaluate(`(()=>{const a=document.querySelector('.today'),att=document.querySelector('.attention'),l=document.querySelector('.ledger'),fig=document.querySelector('.attention-figure'),jump=document.querySelector('.jump-link'),counts=document.querySelector('.attention-counts'),note=document.querySelector('.section-note');const r=e=>e?Math.round(e.getBoundingClientRect().top+scrollY):null;return {width:innerWidth,actionTop:r(a),attentionTop:r(att),attentionHeight:att?Math.round(att.getBoundingClientRect().height):null,jumpTop:r(jump),jumpHref:jump?jump.getAttribute('href'):null,countsText:counts?counts.textContent.trim():null,severityNote:note?note.textContent.trim():null,figureExists:!!fig,ledgerTop:r(l),hasAttention:!!att,warnTier:!!att&&att.classList.contains('warn-tier'),figureColor:fig?getComputedStyle(fig).color:null}})()`);
  if(acceptance&&measure.width>=1280&&measure.fold.actionTop!==null&&measure.fold.actionTop>=900)throw Error('One action starts below the 900px fold on cold load: '+JSON.stringify(measure.fold));
  if(acceptance&&measure.fold.warnTier&&measure.fold.figureColor!=='rgb(138, 91, 18)')throw Error('Preference warning is not wearing the ochre tier: '+JSON.stringify(measure.fold));
  if(acceptance&&measure.fold.hasAttention&&!measure.fold.warnTier&&measure.fold.figureColor&&measure.fold.figureColor!=='rgb(163, 45, 34)')throw Error('Blocking evidence is not wearing the brick uniform: '+JSON.stringify(measure.fold));
  if(acceptance&&measure.fold.figureExists&&!measure.fold.countsText)throw Error('Attention panel has no exact counts line: '+JSON.stringify(measure.fold));
  if(acceptance&&measure.fold.figureExists&&!/tier|blocked|cleared/i.test(measure.fold.severityNote||''))throw Error('Dietary severity has no text token: '+JSON.stringify(measure.fold));
  if(acceptance&&measure.fold.jumpHref){
    if(measure.fold.jumpHref!=='#today')throw Error('Jump link does not target the action: '+JSON.stringify(measure.fold));
    if(measure.fold.jumpTop>=844&&measure.fold.actionTop>=844)throw Error('No action or jump within the 844px mobile first screen: '+JSON.stringify(measure.fold));
  }
  if(acceptance){
    const lies=await evaluate(`(()=>{const out=[];for(const m of document.querySelectorAll('.mark.ok')){if(m.closest('.state-legend'))continue;if(m.dataset.result!=='safe')out.push(m.dataset.result||'no-result');}return out})()`);
    if(lies.length)throw Error('A clearance mark is not backed by a safe evaluation: '+JSON.stringify(lies));
    // One verdict authority: every surface must agree per item, and a cleared
    // token exists only with an explicit safe+current receipt.
    const authority=await evaluate(`(()=>{const marks=[...document.querySelectorAll('.mark[data-verdict][data-item]')].map(m=>({item:m.dataset.item,verdict:m.dataset.verdict,result:m.dataset.result||'',evidence:m.dataset.evidence||'',ok:m.classList.contains('ok')}));const conflicts=[];const seen=new Map();for(const m of marks){if(!m.item)continue;if(seen.has(m.item)&&seen.get(m.item)!==m.verdict)conflicts.push([m.item,seen.get(m.item),m.verdict]);else seen.set(m.item,m.verdict);}const lies=marks.filter(m=>((m.verdict==='cleared')!==m.ok)||(m.ok&&(m.result!=='safe'||m.evidence!=='current')));return {count:marks.length,conflicts,lies}})()`);
    if(authority.conflicts.length)throw Error('One item renders contradictory dietary verdicts: '+JSON.stringify(authority.conflicts));
    if(authority.lies.length)throw Error('A mark token disagrees with the authority receipt: '+JSON.stringify(authority.lies));
    // The action area must carry every blocked item, and no non-cleared row may
    // present an unqualified action.
    const actionArea=await evaluate(`(()=>{const t=document.querySelector('.today');if(!t)return null;const blocked=[...new Set([...document.querySelectorAll(".mark[data-verdict='blocked'][data-item]")].map(m=>m.dataset.item))];const text=t.textContent;const missing=blocked.filter(n=>!text.includes(n));const rows=[...t.querySelectorAll('li[data-action-item]')].map(li=>{const m=li.querySelector('.mark[data-verdict]');return {item:li.dataset.actionItem,verdict:m?m.dataset.verdict:'',qualifier:!!li.querySelector('.action-qualifier')}});return {blocked,missing,rows,unqualified:rows.filter(r=>r.verdict&&r.verdict!=='cleared'&&!r.qualifier)}})()`);
    if(actionArea&&actionArea.missing.length)throw Error('A blocked item is absent from the action area: '+JSON.stringify(actionArea));
    if(actionArea&&actionArea.unqualified.length)throw Error('A non-cleared action has no dietary qualifier: '+JSON.stringify(actionArea));
    measure.actionArea=actionArea;
    // An unpriced placeholder is not a recorded zero.
    const ledgerSpend=await evaluate(`(()=>{const rows=[...document.querySelectorAll('.ledger tbody tr')].map(r=>r.textContent.replace(/\\s+/g,' '));return {rows:rows.length,fabricated:rows.filter(t=>/No price captured/.test(t)&&/\\$0\\.00/.test(t))}})()`);
    if(ledgerSpend.fabricated.length)throw Error('Unpriced ledger row renders a fabricated $0.00: '+JSON.stringify(ledgerSpend));
  }
  const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  await writeFile(resolve(output,`dashboard-${mode==='zoom'?'native-400pct':width}.png`),Buffer.from(shot.data,'base64'));
  await evaluate(`document.querySelectorAll('details').forEach(x=>x.open=true)`);await pause();
  const expanded=await evaluate(`(()=>{const w=innerWidth;const bad=[...document.querySelectorAll('body *')].map(e=>({e,r:e.getBoundingClientRect()})).filter(x=>x.r.right>w+1&&x.r.width>0).slice(0,4).map(x=>x.e.tagName+'.'+String(x.e.className||'').slice(0,50)+' right='+Math.round(x.r.right)+' w='+Math.round(x.r.width));return {width:w,scrollWidth:document.documentElement.scrollWidth,bad,unlabelledCells:[...document.querySelectorAll('td')].filter(x=>!x.dataset.label).length,unlabelledSelects:[...document.querySelectorAll('select')].filter(x=>!document.querySelector('label[for="'+x.id+'"]')).length}})()`);
  if(acceptance&&expanded.scrollWidth>expanded.width)throw Error('Expanded viewport overflow at '+width+'px: '+JSON.stringify(expanded));
  measure.expanded=expanded;
  measure.contrast=await evaluate(`(()=>{const rgb=s=>(s.match(/[\\d.]+/g)||[]).map(Number);const luminance=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);const pairs=new Map();for(const e of document.querySelectorAll('body *')){if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())||!e.getBoundingClientRect().height)continue;const style=getComputedStyle(e);let p=e,bg;while(p){bg=rgb(getComputedStyle(p).backgroundColor);if(bg.length===3||bg[3]>0)break;p=p.parentElement;}if(!p)continue;const fg=rgb(style.color),a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);pairs.set(style.color+' / '+bg.join(','),{ratio,color:style.color,background:bg,text:e.textContent.trim().slice(0,40)});}return [...pairs.values()]})()`);
  if(acceptance&&measure.contrast.some(x=>x.ratio<4.5))throw Error('Text contrast below 4.5:1 '+JSON.stringify(measure.contrast));
  measure.graphics=await evaluate(`(()=>{const rgb=s=>(s.match(/[\\d.]+/g)||[]).map(Number);const lum=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);const ratio=(a,b)=>{const A=lum(a),B=lum(b);return (Math.max(A,B)+.05)/(Math.min(A,B)+.05)};const bg=rgb(getComputedStyle(document.body).backgroundColor);const rect=[...document.querySelectorAll('.ruler svg rect')].find(r=>getComputedStyle(r).fill==='none');const outline=document.querySelector('.legend-swatch.outline');const bar=document.querySelector('.bar');return {background:bg.join(','),ruler:rect?ratio(rgb(getComputedStyle(rect).stroke),bg):null,legend:outline?ratio(rgb(getComputedStyle(outline).borderTopColor),bg):null,bar:bar?ratio(rgb(getComputedStyle(bar).borderTopColor),bg):null}})()`);
  if(acceptance)for(const [name,value] of Object.entries({ruler:measure.graphics.ruler,legend:measure.graphics.legend,bar:measure.graphics.bar}))if(value!==null&&value<3)throw Error('Meaningful graphic '+name+' below 3:1: '+JSON.stringify(measure.graphics));
  measure.layout=await evaluate(`(()=>{const caption=document.querySelector('.table-caption');const cells=[...document.querySelectorAll('th,td')];const broken=cells.filter(c=>getComputedStyle(c).overflowWrap==='anywhere'||getComputedStyle(c).wordBreak!=='normal');const tables=[...document.querySelectorAll('table')];const overflow=tables.map(t=>({width:Math.round(t.getBoundingClientRect().width),scroll:Math.round(t.scrollWidth),parent:Math.round(t.parentElement.clientWidth)})).filter(x=>x.scroll>x.parent+1);const h2=document.querySelector('.disclosure h2');const muted=document.querySelector('.muted');const ledger=document.querySelector('.ledger');const empty=ledger&&!ledger.querySelector('table')?[...ledger.querySelectorAll('p')].map(p=>p.textContent.trim()).filter(Boolean).join(' '):null;return {overflowTables:overflow.length,overflowDetail:overflow,brokenCells:broken.length,captionWidth:caption?Math.round(caption.getBoundingClientRect().width):null,ledgerRows:document.querySelectorAll('.ledger tbody tr').length,ledgerColumns:document.querySelectorAll('.ledger th').length,emptyLedgerCopy:empty,ledgerTableWidth:ledger&&ledger.querySelector('table')?Math.round(ledger.querySelector('table').getBoundingClientRect().width):null,disclosureHeadingPx:h2?parseFloat(getComputedStyle(h2).fontSize):null,mutedColor:muted?getComputedStyle(muted).color:null,bodyColor:getComputedStyle(document.body).color}})()`);
  if(acceptance){const l=measure.layout;if(l.overflowTables)throw Error('Table overflows its container: '+JSON.stringify(l));if(l.brokenCells)throw Error('Cells still break words mid-word: '+JSON.stringify(l));if(l.ledgerColumns&&l.ledgerColumns!==5)throw Error('Ledger is not five columns: '+JSON.stringify(l));if(!l.ledgerColumns&&!l.emptyLedgerCopy)throw Error('Empty ledger state has no copy to verify: '+JSON.stringify(l));if(l.ledgerColumns&&!l.ledgerRows)throw Error('Ledger table has no rows: '+JSON.stringify(l));if(l.disclosureHeadingPx!==null&&l.disclosureHeadingPx>18)throw Error('Disclosure heading is not on the design scale: '+JSON.stringify(l));if(l.mutedColor===l.bodyColor)throw Error('.muted does not mute: '+JSON.stringify(l));if(measure.width>=768&&l.captionWidth!==null&&l.captionWidth<220)throw Error('Table caption squeezed: '+JSON.stringify(l));}
  const expandedShot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
  await writeFile(resolve(output,`expanded-${mode==='zoom'?'native-400pct':width}.png`),Buffer.from(expandedShot.data,'base64'));
  if(mode==='capture'&&(width===1440||width===390)){
    const full=Buffer.from(expandedShot.data,'base64');
    const fullFile=`full-${width}.png`;
    await writeFile(resolve(output,fullFile),full);
    captureManifest.captures.push({file:fullFile,sha256:createHash('sha256').update(full).digest('hex'),width,section:'full-page'});
    for(const [name,selector] of [['attention','.attention'],['action','.today'],['runway','.runway'],['ledger','.ledger']]){
      await captureSection(call,evaluate,name,selector,width);
    }
    if(await evaluate(`!!document.querySelector('.ledger tbody tr')`)){
      await captureSection(call,evaluate,'ledger-row','.ledger tbody tr:first-child',width);
    }
  }
  await evaluate(`document.querySelector('a.skip-link')?.focus()`);
  const trace=[];
  for(let i=0;i<6;i++){await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});trace.push(await evaluate(`(()=>{const e=document.activeElement,s=getComputedStyle(e);return {tag:e.tagName,text:e.textContent.slice(0,80),outline:s.outlineStyle,width:s.outlineWidth}})()`));}
  measure.keyboard=trace;
  if(acceptance&&trace.filter(x=>x.tag!=='BODY').some(x=>x.outline==='none'||x.width==='0px'))throw Error('Missing keyboard focus');
  const correction=await evaluate(`(()=>{const b=document.querySelector('button[data-signal]');if(!b)return null;b.click();return document.querySelector('#correction-count').textContent})()`);
  if(correction&&correction!=='1 captured')throw Error('Correction action blocked');
  measure.correction=correction;
  await evaluate(`document.querySelector('#buy-list-download')?.click();document.querySelector('#correction-download')?.click()`);await pause();
  // Anchor jumps must land below the sticky status banner (r7 major: the 128px
  // banner covered a 88px offset, and the skip target had no offset at all).
  const jumpLink=await evaluate(`(()=>{const l=document.querySelector('a.jump-link');if(!l)return null;l.click();return true})()`);
  if(jumpLink){await pause();
    const jump=await evaluate(`(()=>{const b=document.querySelector('.masthead-status'),t=document.querySelector('#today');const rb=b.getBoundingClientRect(),rt=t.getBoundingClientRect();return {targetTop:Math.round(rt.top),bannerBottom:Math.round(rb.bottom),bannerPosition:getComputedStyle(b).position,scrollMargin:getComputedStyle(t).scrollMarginTop}})()`);
    measure.jump=jump;
    if(acceptance&&jump.targetTop<jump.bannerBottom)throw Error('Action jump lands under the sticky status banner: '+JSON.stringify(jump));
  }
  const skipLink=await evaluate(`(()=>{const l=document.querySelector('a.skip-link');if(!l)return null;l.focus();l.click();return true})()`);
  if(skipLink){await pause();
    const skip=await evaluate(`(()=>{const b=document.querySelector('.masthead-status'),t=document.querySelector('#household-review');const rb=b.getBoundingClientRect(),rt=t.getBoundingClientRect();return {targetTop:Math.round(rt.top),bannerBottom:Math.round(rb.bottom),scrollMargin:getComputedStyle(t).scrollMarginTop}})()`);
    measure.skip=skip;
    if(acceptance&&skip.targetTop<skip.bannerBottom)throw Error('Skip link lands under the sticky status banner: '+JSON.stringify(skip));
  }
  measurements.push(measure);
 }
 const external=requests.filter(x=>/^https?:/.test(x));
 if(external.length||errors.length)throw Error(JSON.stringify({external,errors}));
 const planFile=resolve(output,'downloads/buy-list.json');let exported=null;
 try{exported=JSON.parse(await readFile(planFile,'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
 if(exported&&(exported.approval_required!==true||exported.checkout_available!==false))throw Error('Unsafe export');
 if(exported&&acceptance){
   // The draft is an artifact the household reads; its top-level items[] is the
   // page's action list. The engine cart plan is reference data under engine_plan
   // (r7 blocker: four engine rows restocked an uncleared item and the held row
   // was absent while a second mirror list looked correct).
   if(String(exported.schema||'')!=='grocery-flywheel.dashboard-draft/2')throw Error('Export is not the action-list draft schema: '+exported.schema);
   const buyInstruction=value=>/^(?!(?:do not|hold)\b).*\b(?:restock|rotate|buy|purchase)\b/i.test(String(value||''));
   const list=exported.items;
   if(!Array.isArray(list))throw Error('Export has no top-level items[] action list');
   if(!exported.engine_plan||!Array.isArray(exported.engine_plan.items))throw Error('Export does not preserve the engine plan under engine_plan');
   const pageRows=(measurements[measurements.length-1].actionArea||{}).rows||[];
   if(!pageRows.length)throw Error('No rendered action rows to bind the export to');
   if(list.length!==pageRows.length)throw Error('Exported items[] has '+list.length+' rows; page renders '+pageRows.length);
   for(const row of pageRows){
     const entry=list.find(x=>x.item===row.item);
     if(!entry)throw Error('Exported items[] omits a rendered row: '+row.item);
     if(entry.state!==row.verdict)throw Error('Exported state '+entry.state+' disagrees with rendered '+row.verdict+' for '+row.item);
     if(entry.cleared!==(row.verdict==='cleared'))throw Error('Exported cleared flag disagrees with the rendered mark for '+row.item);
     if(entry.hold!==!entry.cleared)throw Error('Exported hold flag does not mark every non-cleared row: '+row.item);
     if(!entry.cleared&&buyInstruction(entry.display_action))throw Error('Export carries a buy instruction on a non-cleared item: '+row.item);
     if(!entry.cleared&&!entry.qualifier)throw Error('Export drops the dietary qualifier for '+row.item);
     if(entry.held_out_of_plan&&(entry.cleared||entry.state!=='blocked'))throw Error('Exported held_out_of_plan is not a blocked row: '+JSON.stringify(entry));
   }
   // Every action-bearing entry outside the reference-only engine plan must obey
   // the same rule; a second instruction collection cannot drift (r7 blocker).
   const instructionScope=Object.fromEntries(Object.entries(exported).filter(([key])=>key!=='engine_plan'));
   const bad=[];
   const walk=(node,path)=>{
     if(!node||typeof node!=='object')return;
     if(Array.isArray(node)){node.forEach((value,index)=>walk(value,path+'['+index+']'));return;}
     if(typeof node.display_action==='string'&&buyInstruction(node.display_action)&&node.cleared!==true)bad.push(path+':'+node.display_action);
     for(const [key,value] of Object.entries(node))walk(value,path+'.'+key);
   };
   walk(instructionScope,'export');
   if(bad.length)throw Error('A buy instruction appears on a non-cleared entry: '+JSON.stringify(bad));
   const context=exported.dietary_context||{};
   const contextNames=(context.items||[]).map(x=>x.item);
   for(const row of pageRows)if(!contextNames.includes(row.item))throw Error('Dietary context omits an action row: '+row.item);
   if((context.action_items_total??-1)!==list.length)throw Error('dietary_context.action_items_total does not count the action list: '+context.action_items_total+' vs '+list.length);
   if((context.engine_plan_items_total??-1)!==exported.engine_plan.items.length)throw Error('dietary_context.engine_plan_items_total does not count the engine plan');
   if(!String(exported.items_note||'').includes('hold=true'))throw Error('Export does not explain its hold flag');
   if(!String(context.state_legend?.not_evaluated?.meaning||'').includes('named no item on this page'))throw Error('Export legend conflates not-evaluated with the clearance wording');
 }
 const report={ok:true,mode,acceptance,artifactSha256,requests,errors,downloads,exported,measurements};
 await writeFile(resolve(output,'browser-report.json'),JSON.stringify(report,null,2));
 if(mode==='capture')await writeFile(resolve(output,'capture-manifest.json'),JSON.stringify(captureManifest,null,2));
 console.log(JSON.stringify({ok:true,mode,acceptance,viewports:measurements.length,externalRequests:external.length,errors:errors.length,downloaded:downloads}));
 await send('Browser.close');
}finally{ws?.close();if(chrome.exitCode===null)chrome.kill('SIGTERM');}
