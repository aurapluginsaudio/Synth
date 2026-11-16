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
def zc(buf,sr,w=0,hop=0):
    t=[]
    for k in range(1,len(buf)):
        if buf[k-1]<0<=buf[k]: t.append(k-1+(-buf[k-1])/(buf[k]-buf[k-1]))
    return [sr/(t[i+1]-t[i]) for i in range(len(t)-1)] or [0]
def zc_old(buf,sr,w=1440,hop=720):
    out=[]
    for i in range(0,len(buf)-w,hop):
        seg=buf[i:i+w]; c=0
        for k in range(1,len(seg)):
            if seg[k-1]<0<=seg[k]: c+=1
        out.append(c*sr/w)
    return out
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(900)
    print('engine',pg.evaluate("window.__auraEngine"))
    def adv(): pg.click('#menuBtn'); pg.click('#mAdv')
    def chip(label,txt): pg.click(f'#advBody .fxrow:has(span:text-is("{label}")) button:text-is("{txt}")')
    def close(): pg.evaluate("document.getElementById('dlgAdv').classList.remove('open')")
    # 1) A-440
    adv(); chip('TOM A-440','LIGADO'); pg.wait_for_timeout(600); buf=pg.evaluate("window.__buf.slice(-8192)"); f=zc(buf,48000,4096,4096); print('A440 zc',f[-1]); chip('TOM A-440','DESLIGADO'); close()
    # 2) escala: nota A4 (69) oct=0 -> medir pelos setValueAtTime da frequência
    pg.evaluate("window.__fr.length=0"); 
    for tt,name in [(0,'IGUAL'),(1,'PITAGÓRICA'),(2,'CARLOS')]:
        adv(); chip('ESCALA',name); close()
        pg.evaluate("window.__fr.length=0"); pg.evaluate("__send([0x90,64,100])"); pg.wait_for_timeout(120); fr=pg.evaluate("window.__fr.slice()"); pg.evaluate("__send([0x80,64,0])"); pg.wait_for_timeout(100)
        print(name,'E4 freq oct-1 ->',[round(x,2) for x in fr[-2:]], 'esperado ET', round(329.6276/2,2))
    adv(); chip('ESCALA','IGUAL'); close()
    # 3) tune +100 cents
    adv()
    pg.eval_on_selector('#advBody .fxrow:has(span:text-is("TUNE")) input','e=>{e.value=1000;e.dispatchEvent(new Event("input"))}'); close()
    pg.evaluate("window.__fr.length=0"); pg.evaluate("__send([0x90,69,100])"); pg.wait_for_timeout(120); fr=pg.evaluate("window.__fr.slice()"); pg.evaluate("__send([0x80,69,0])"); print('A4 oct-1 +100c ->',[round(x,2) for x in fr[-2:]],'esperado',round(220*2**(100/1200)/2,2))
    adv(); pg.eval_on_selector('#advBody .fxrow:has(span:text-is("TUNE")) input','e=>{e.value=500;e.dispatchEvent(new Event("input"))}'); close()
    # 4) MOD MIX: vibrato por LFO com roda cheia
    adv(); chip('MOD MIX','LIGADO'); chip('FONTE B','LFO'); pg.eval_on_selector('#advBody .fxrow:has(span:text-is("MIX A ↔ B")) input','e=>{e.value=1000;e.dispatchEvent(new Event("input"))}')
    chip('OSC 1','TRI'); close()
    pg.evaluate("window.__buf.length=0"); pg.evaluate("__send([0xB0,1,0])"); pg.evaluate("__send([0x90,45,100])"); pg.wait_for_timeout(1500)
    buf=pg.evaluate("window.__buf.slice(-48000)"); f0=zc(buf,48000); print('sem roda: min/max',round(min(f0),1),round(max(f0),1))
    pg.evaluate("__send([0xB0,1,127])"); pg.wait_for_timeout(1200); buf=pg.evaluate("window.__buf.slice(-48000)"); f1=zc(buf,48000); print('roda cheia: min/max',round(min(f1),1),round(max(f1),1))
    pg.evaluate("__send([0x80,45,0])"); pg.wait_for_timeout(200)
    print('errs',errs); b.close()
