#!/usr/bin/env node
// Offline Chrome/CDP proof with no npm dependency or HTTP listener in the plugin.
// modes: normal (assert four widths, contrast, keyboard, exports) | baseline
// (capture only, for before/after) | zoom (native 400% browser zoom preference).
import {spawn} from 'node:child_process';
import {mkdir,writeFile,readFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [artifact,output,mode='normal']=process.argv.slice(2);
if(!artifact||!output)throw Error('Usage: node scripts/verify_hermes_dashboard.mjs file.html output [normal|baseline|zoom]');
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
 for(const width of mode==='zoom'?[1440]:[1440,768,390,320]){
  if(mode!=='zoom')await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(resolve(artifact)).href});await pause();
  const measure=await evaluate(`(()=>{const r={width:innerWidth,outerWidth,scrollWidth:document.documentElement.scrollWidth,dpr:devicePixelRatio,injected:!!window.GROCERY_INJECTED,heading:document.querySelector('h1')?.textContent,details:document.querySelectorAll('details').length,corrections:!!document.querySelector('#correction-item')};return r})()`);
  if(measure.injected)throw Error('Hostile fixture executed');
  if(mode!=='baseline'&&measure.scrollWidth>measure.width)throw Error('Collapsed viewport overflow '+JSON.stringify(measure));
  if(mode==='zoom'&&measure.dpr<3.9)throw Error('Native browser zoom preference did not take effect: '+JSON.stringify(measure));
  const shot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  await writeFile(resolve(output,`dashboard-${mode==='zoom'?'native-400pct':width}.png`),Buffer.from(shot.data,'base64'));
  await evaluate(`document.querySelectorAll('details').forEach(x=>x.open=true)`);await pause();
  const expanded=await evaluate(`({width:innerWidth,scrollWidth:document.documentElement.scrollWidth,unlabelledCells:[...document.querySelectorAll('td')].filter(x=>!x.dataset.label).length,unlabelledSelects:[...document.querySelectorAll('select')].filter(x=>!document.querySelector('label[for="'+x.id+'"]')).length})`);
  if(mode!=='baseline'&&expanded.scrollWidth>expanded.width)throw Error('Expanded viewport overflow');
  measure.expanded=expanded;
  measure.contrast=await evaluate(`(()=>{const rgb=s=>(s.match(/[\\d.]+/g)||[]).map(Number);const luminance=c=>c.slice(0,3).map(x=>{x/=255;return x<=.04045?x/12.92:((x+.055)/1.055)**2.4}).reduce((v,x,i)=>v+x*[.2126,.7152,.0722][i],0);const pairs=new Map();for(const e of document.querySelectorAll('body *')){if(![...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())||!e.getBoundingClientRect().height)continue;const style=getComputedStyle(e);let p=e,bg;while(p){bg=rgb(getComputedStyle(p).backgroundColor);if(bg.length===3||bg[3]>0)break;p=p.parentElement;}if(!p)continue;const fg=rgb(style.color),a=luminance(fg),b=luminance(bg),ratio=(Math.max(a,b)+.05)/(Math.min(a,b)+.05);pairs.set(style.color+' / '+bg.join(','),{ratio,color:style.color,background:bg,text:e.textContent.trim().slice(0,40)});}return [...pairs.values()]})()`);
  if(mode!=='baseline'&&measure.contrast.some(x=>x.ratio<4.5))throw Error('Text contrast below 4.5:1 '+JSON.stringify(measure.contrast));
  const expandedShot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:true});
  await writeFile(resolve(output,`expanded-${mode==='zoom'?'native-400pct':width}.png`),Buffer.from(expandedShot.data,'base64'));
  await evaluate(`document.querySelector('a.skip-link')?.focus()`);
  const trace=[];
  for(let i=0;i<6;i++){await call('Input.dispatchKeyEvent',{type:'keyDown',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});await call('Input.dispatchKeyEvent',{type:'keyUp',key:'Tab',code:'Tab',windowsVirtualKeyCode:9});trace.push(await evaluate(`(()=>{const e=document.activeElement,s=getComputedStyle(e);return {tag:e.tagName,text:e.textContent.slice(0,80),outline:s.outlineStyle,width:s.outlineWidth}})()`));}
  measure.keyboard=trace;
  if(mode!=='baseline'&&trace.filter(x=>x.tag!=='BODY').some(x=>x.outline==='none'||x.width==='0px'))throw Error('Missing keyboard focus');
  const correction=await evaluate(`(()=>{const b=document.querySelector('button[data-signal]');if(!b)return null;b.click();return document.querySelector('#correction-count').textContent})()`);
  if(correction&&correction!=='1 captured')throw Error('Correction action blocked');
  measure.correction=correction;
  await evaluate(`document.querySelector('#buy-list-download')?.click();document.querySelector('#correction-download')?.click()`);await pause();
  measurements.push(measure);
 }
 const external=requests.filter(x=>/^https?:/.test(x));
 if(external.length||errors.length)throw Error(JSON.stringify({external,errors}));
 const planFile=resolve(output,'downloads/buy-list.json');let exported=null;
 try{exported=JSON.parse(await readFile(planFile,'utf8'));}catch(e){if(e.code!=='ENOENT')throw e;}
 if(exported&&(exported.approval_required!==true||exported.checkout_available!==false))throw Error('Unsafe export');
 const report={ok:true,mode,requests,errors,downloads,exported,measurements};
 await writeFile(resolve(output,'browser-report.json'),JSON.stringify(report,null,2));
 console.log(JSON.stringify({ok:true,mode,viewports:measurements.length,externalRequests:external.length,errors:errors.length,downloaded:downloads}));
 await send('Browser.close');
}finally{ws?.close();if(chrome.exitCode===null)chrome.kill('SIGTERM');}
