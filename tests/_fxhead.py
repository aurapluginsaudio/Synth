import json,math,sys
from playwright.sync_api import sync_playwright
INIT="""
window.__inp={name:'SMK',onmidimessage:null};
navigator.requestMIDIAccess=async()=>({inputs:new Map([['1',window.__inp]]),onstatechange:null});
window.__send=(a)=>window.__inp.onmidimessage({data:new Uint8Array(a)});
try{localStorage.clear()}catch(e){}
window.__buf=[]; window.__fr=[];
const oc=AudioNode.prototype.connect;
AudioNode.prototype.connect=function(d,...r){ const res=oc.call(this,d,...r);
  try{ if(d instanceof AudioDestinationNode && !this.ctx_tapped){ const c=this.context; if(!c.__spp){ const sp=c.createScriptProcessor(2048,1,1); sp.onaudioprocess=e=>{ window.__buf.push(...e.inputBuffer.getChannelData(0)); if(window.__buf.length>400000) window.__buf.splice(0,100000); }; const z=c.createGain(); z.gain.value=0; z.ctx_tapped=1; sp.connect(z); z.connect(c.destination); c.__spp=sp; }
      oc.call(this,c.__spp); this.ctx_tapped=1; } }catch(e){}
  return res; };
const sv=AudioParam.prototype.setValueAtTime;
AudioParam.prototype.setValueAtTime=function(v,t){ if(this.maxValue===20000 && this.minValue===1) window.__fr.push(v); return sv.call(this,v,t); };
"""
