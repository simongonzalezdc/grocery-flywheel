#!/usr/bin/env node
// Offline Chrome/CDP proof with no npm dependency or HTTP listener in the plugin.
import {spawn} from 'node:child_process';
import {mkdir, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
const [artifact, output] = process.argv.slice(2);
if (!artifact || !output) throw Error('Usage: node scripts/verify_hermes_dashboard.mjs artifact.html output-dir');
await mkdir(output, {recursive:true});
const chrome=spawn(process.env.CHROME_PATH || '/usr/bin/google-chrome', ['--headless=new','--no-sandbox','--disable-gpu','--disable-background-networking','--disable-component-update','--no-first-run','--no-default-browser-check',`--user-data-dir=${resolve(output,'chrome-profile')}`,'--remote-debugging-port=0','about:blank'],{stdio:['ignore','ignore','pipe']});
const endpoint=await new Promise((res,rej)=>{let text=''; const timer=setTimeout(()=>rej(Error('Chrome startup timeout')),20000);chrome.stderr.on('data',x=>{text+=x;const match=text.match(/DevTools listening on (ws:\/\/\S+)/);if(match){clearTimeout(timer);res(match[1]);}});chrome.on('error',rej);});
let ws;
try {
 ws=new WebSocket(endpoint); await new Promise((res,rej)=>{ws.onopen=res;ws.onerror=rej;});
 let id=0;const pending=new Map();const requests=[];const errors=[];
 ws.onmessage=({data})=>{const msg=JSON.parse(data);if(msg.id){const p=pending.get(msg.id);pending.delete(msg.id);if(msg.error)p.reject(Error(JSON.stringify(msg.error)));else p.resolve(msg.result);}else if(msg.method==='Network.requestWillBeSent'){requests.push(msg.params.request.url);}else if(msg.method==='Runtime.exceptionThrown'){errors.push(msg.params.exceptionDetails.text);}};
 const send=(method,params={},sessionId)=>new Promise((resolve,reject)=>{const n=++id;pending.set(n,{resolve,reject});ws.send(JSON.stringify({id:n,method,params,...(sessionId?{sessionId}:{})}));});
 const {targetId}=await send('Target.createTarget',{url:'about:blank'});
 const {sessionId}=await send('Target.attachToTarget',{targetId,flatten:true});
 const call=(method,params={})=>send(method,params,sessionId);
 await call('Page.enable');await call('Runtime.enable');await call('Network.enable');
 await call('Network.setBlockedURLs',{urls:['http://*','https://*']});
 const measurements=[];
 for(const width of [1440,390]){
  await call('Emulation.setDeviceMetricsOverride',{width,height:1000,deviceScaleFactor:1,mobile:false});
  await call('Page.navigate',{url:pathToFileURL(resolve(artifact)).href});
  await new Promise(r=>setTimeout(r,700));
  const {result}=await call('Runtime.evaluate',{expression:`JSON.stringify({title:document.title,text:document.body.innerText.slice(0,3000),width:innerWidth,scrollWidth:document.documentElement.scrollWidth,injected:!!window.GROCERY_INJECTED,headings:[...document.querySelectorAll('h1,h2,h3')].map(x=>x.innerText),scripts:document.scripts.length})`,returnByValue:true});
  const value=JSON.parse(result.value);if(value.injected||!value.text.includes('Bean and cheese burritos'))throw Error('Dashboard unreadable or injected');
  if(value.scrollWidth>value.width)throw Error('Document overflows narrow viewport');
  const interaction=await call('Runtime.evaluate',{expression:`(()=>{const b=document.querySelector('button[data-signal]');if(!b)return {present:false};b.click();return {present:true,count:document.querySelector('#correction-count').textContent};})()`,returnByValue:true});
  if(interaction.result.value.present && interaction.result.value.count!=='1 captured')throw Error('Trusted correction interaction blocked');
  value.interaction=interaction.result.value;
  const screenshot=await call('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  await writeFile(resolve(output,`dashboard-${width}.png`),Buffer.from(screenshot.data,'base64'));
  measurements.push(value);
 }
 if(requests.some(x=>/^https?:/.test(x)))throw Error('Dashboard attempted external request');
 if(errors.length)throw Error('Dashboard JavaScript error: '+errors.join(';'));
 await writeFile(resolve(output,'browser-report.json'),JSON.stringify({ok:true,requests,errors,measurements},null,2));
 console.log(JSON.stringify({ok:true,viewports:measurements.length,externalRequests:0,errors:0}));
 await send('Browser.close');
}finally{ws?.close();if(chrome.exitCode===null)chrome.kill('SIGTERM');}
