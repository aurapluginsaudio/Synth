import json,sys
from playwright.sync_api import sync_playwright
URL='http://localhost:8765/index.html'
def P(name,**k): d={'name':name,'wave':'triangle','lvl':0.6,'l2':0,'sub':0,'nz':0,'cut':0.7,'res':0,'fenv':0,'kt':0,'drv':0,'oct':-1,'a':0.002,'d':2,'s':1,'r':0.05,'fa':0.002,'fd':2,'fs':1,'fr':0.05,'vol':1.2,'leg':0}; d.update(k); return d
PRE=[P('T_BASE'),
 P('T_O3',l3=0.6,w3='square',o3=1),
 P('T_WHITE',lvl=0,nz=1,cut=1,nc=0), P('T_PINK',lvl=0,nz=1,cut=1,nc=1),
 P('T_OVL0',wave='sawtooth',cut=0.35,res=0.4), P('T_OVL8',wave='sawtooth',cut=0.35,res=0.4,ovl=0.8),
 P('T_LFO0',lp=0), P('T_RAND',lp=3,lsr=2,lr=8), P('T_O3LFO',lp=3,lsr=1,lr=6,k3=0,l3=0),
 P('T_DLY0',r=0.02,fr=0.02,dm=0), P('T_DLY',r=0.02,fr=0.02,dm=0.9,dt=0.12,df=0.5),
 P('T_EXP',d=1.0,s=0.3,fd=1,fs=0.3,wave='sawtooth',cut=0.9), P('T_LIN',d=1.0,s=0.3,fd=1,fs=0.3,wave='sawtooth',cut=0.9,ec=1),
 P('T_FILT',wave='sawtooth',cut=0.25,vol=1.0)]
IDX={p['name']:111+i for i,p in enumerate(PRE)}
INIT="""window.__inp={name:'SMK',onmidimessage:null};
 navigator.requestMIDIAccess=async()=>({inputs:new Map([['1',window.__inp]]),onstatechange:null});
 window.__send=(a)=>window.__inp.onmidimessage({data:new Uint8Array(a)});
 try{localStorage.clear(); localStorage.setItem('aura_user_presets_v1',JSON.stringify(%s));}catch(e){}
 const _AC=window.AudioContext; window.AudioContext=function(o){const c=new _AC(o); const ca=c.createAnalyser.bind(c); c.createAnalyser=()=>{const a=ca(); if(!window.__an){window.__an=a; const a2=ca(); a2.fftSize=8192; a.connect(a2); window.__an2=a2;} return a;}; return c;};
 window.rms=()=>{const a=window.__an2,b=new Float32Array(a.fftSize);a.getFloatTimeDomainData(b);let s=0,m=0;for(const v of b){s+=v*v;m=Math.max(m,Math.abs(v))}return [Math.sqrt(s/b.length),m]};
 window.pitch=()=>{const a=window.__an2,N=a.fftSize,b=new Float32Array(N);a.getFloatTimeDomainData(b);let e=0;for(const v of b)e+=v*v;if(Math.sqrt(e/N)<0.01)return 0;const sr=a.context.sampleRate,lo=Math.floor(sr/500),hi=Math.floor(sr/30);let best=-1,bi=0;for(let l=lo;l<=hi;l++){let s=0;for(let i=0;i<N-hi;i+=2)s+=b[i]*b[i+l];if(s>best){best=s;bi=l}}return sr/bi};
 window.hf=()=>{const a=window.__an2,b=new Float32Array(a.frequencyBinCount);a.getFloatFrequencyData(b);const sr=a.context.sampleRate,f=i=>i*sr/a.fftSize;let lo=0,hi=0,nl=0,nh=0;b.forEach((v,i)=>{const p=Math.pow(10,v/10);if(f(i)>100&&f(i)<1000){lo+=p;nl++}if(f(i)>6000&&f(i)<12000){hi+=p;nh++}});return 10*Math.log10((lo/nl)/(hi/nh))};
"""%json.dumps(PRE)
res={}; errs=[]
def run():
  with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.add_init_script(INIT); pg.goto(URL); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(1000)
    assert pg.evaluate('window.__auraEngine')=='worklet'
    send=lambda a: pg.evaluate(f'__send({a})')
    def pre(n): send([0xC0,IDX[n]]); pg.wait_for_timeout(150)
    def hold_note(n,ms=600,note=48):
        send([0x90,note,100]); pg.wait_for_timeout(ms); r=pg.evaluate('rms()'); return r
    def off(note=48): send([0x80,note,0]); pg.wait_for_timeout(500)
    # osc3
    pre('T_BASE'); a=hold_note('T_BASE'); off(); pre('T_O3'); c=hold_note('T_O3'); off()
    res['osc3 RMS base→com osc3']=(round(a[0],3),round(c[0],3))
    # ruído
    pre('T_WHITE'); send([0x90,48,100]); pg.wait_for_timeout(500); w=pg.evaluate('hf()'); off(); pre('T_PINK'); send([0x90,48,100]); pg.wait_for_timeout(500); k=pg.evaluate('hf()'); off()
    res['ruído graves/agudos dB (branco, rosa)']=(round(w,1),round(k,1))
    # overload
    pre('T_OVL0'); o0=hold_note('x'); off(); pre('T_OVL8'); o8=hold_note('x'); send([0x80,48,0]); pg.wait_for_timeout(1500); tail=pg.evaluate('rms()'); 
    res['overload RMS 0 / 0.8 / pico / cauda após soltar']=(round(o0[0],3),round(o8[0],3),round(o8[1],2),round(tail[1],4))
    # LFO fontes: variação de afinação
    def pv(n,N=14,gap=60):
        pre(n); send([0x90,48,100]); pg.wait_for_timeout(300); v=[]; 
        for i in range(N): v.append(pg.evaluate('pitch()')); pg.wait_for_timeout(gap)
        off(); v=[x for x in v if x>0]; return (round(min(v),1),round(max(v),1)) if v else None
    res['afinação min/max: sem LFO | RAND | OSC3-LFO']=(pv('T_LFO0'),pv('T_RAND'),pv('T_O3LFO'))
    # delay
    def tail_after(n):
        pre(n); send([0x90,48,100]); pg.wait_for_timeout(400); send([0x80,48,0]); pg.wait_for_timeout(180); r=pg.evaluate('rms()'); pg.wait_for_timeout(500); return round(r[0],3)
    res['delay: RMS logo após soltar (sem / com)']=(tail_after('T_DLY0'),tail_after('T_DLY'))
    # curva de envelope
    def env(n):
        pre(n); send([0x90,48,100]); v=[]
        for t in (150,350,700,900,1300):
            pg.wait_for_timeout(t-(0 if not v else prev[0])); prev=[t]; v.append(round(pg.evaluate('rms()')[0],3))
        off(); return v
    res['envelope RMS em 150/350/700/900/1300ms: exp']=env('T_EXP'); res['… linear']=env('T_LIN')
    # prioridade de nota
    pre('T_BASE'); pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mPrio'); pg.wait_for_timeout(100); st=pg.inner_text('#mPrioSt'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    send([0x90,48,100]); pg.wait_for_timeout(250); send([0x90,55,100]); pg.wait_for_timeout(400); f1=pg.evaluate('pitch()'); send([0x80,48,0]); pg.wait_for_timeout(500); f2=pg.evaluate('pitch()'); off(55)
    res['prioridade '+st+': com 48+55 soando / só 55 depois de soltar 48 (Hz)']=(round(f1,1),round(f2,1))
    # aftertouch
    pre('T_FILT'); send([0x90,48,100]); pg.wait_for_timeout(500); base=pg.evaluate('rms()')[0]
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mAt'); pg.click('#mAt'); st2=pg.inner_text('#mAtSt'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    send([0xD0,127]); pg.wait_for_timeout(500); atf=pg.evaluate('rms()')[0]; send([0xD0,0]); off()
    res['aftertouch '+st2+': RMS sem / com pressão']=(round(base,3),round(atf,3))
    # hold
    pre('T_BASE'); pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mHold'); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    send([0x90,48,100]); pg.wait_for_timeout(300); send([0x80,48,0]); pg.wait_for_timeout(500); h1=pg.evaluate('rms()')[0]
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mHold'); pg.keyboard.press('Escape'); pg.wait_for_timeout(700); h2=pg.evaluate('rms()')[0]
    res['hold: RMS com hold depois de soltar / depois de desligar hold']=(round(h1,3),round(h2,4))
    # arpejador
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mArp'); pg.wait_for_timeout(200)
    pg.click('#arpBody .chips >> nth=0 >> text="LIGADO"'); pg.wait_for_timeout(100); pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    send([0x90,48,100]); send([0x90,52,100]); send([0x90,55,100]); seq=[]
    for i in range(10): pg.wait_for_timeout(300 if i else 150); seq.append(round(pg.evaluate('pitch()')))
    send([0x80,48,0]); send([0x80,52,0]); send([0x80,55,0]); pg.wait_for_timeout(500); sil=pg.evaluate('rms()')[1]
    res['arpejador (Hz a cada 300 ms) e pico após soltar']=(seq,round(sil,4))
    pg.screenshot(path='/tmp/feat_end.png'); b.close()
run()
for k,v in res.items(): print(k,'→',v)
print('erros:',errs)
