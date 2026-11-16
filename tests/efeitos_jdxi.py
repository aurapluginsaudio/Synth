exec(open('tests/_fxhead.py').read())
import numpy as np
from playwright.sync_api import sync_playwright
def rms(a): a=np.array(a,dtype=float); return float(np.sqrt((a**2).mean())) if len(a) else 0
def spec(a,sr,lo,hi):
    a=np.array(a[-16384:],dtype=float); F=np.abs(np.fft.rfft(a*np.hanning(len(a)))); f=np.fft.rfftfreq(len(a),1/sr); m=(f>=lo)&(f<hi); return float(F[m].sum())
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(600)
    pg.click('#oled'); pg.keyboard.press('Escape'); pg.mouse.click(640,600); pg.wait_for_timeout(800)
    sr=pg.evaluate("window.__fx.fx.o1.context.sampleRate"); print('sr',sr,'engine',pg.evaluate('window.__auraEngine'))
    def note(on,dur=700):
        pg.evaluate("window.__send([0x90,45,100])"); pg.wait_for_timeout(dur); 
    def grab(setup,dur=900):
        pg.evaluate("window.__send([0x80,45,0]); window.__buf.length=0"); pg.evaluate(setup); pg.wait_for_timeout(300)
        pg.evaluate("window.__buf.length=0; window.__send([0x90,45,100])"); pg.wait_for_timeout(dur)
        a=pg.evaluate("window.__buf.slice()"); pg.evaluate("window.__send([0x80,45,0])"); pg.wait_for_timeout(100); return a
    base="Object.assign(window.__fx.FX,{d:0,m:0,rv:0});window.__fx.fxApply()"
    a0=grab(base); print('base rms',rms(a0))
    a1=grab("Object.assign(window.__fx.FX,{d:1,dr:0.8,dl:0.7});window.__fx.fxApply()"); print('dist rms',rms(a1),'HF ratio base/dist',spec(a0,sr,1500,8000)/spec(a0,sr,50,300),spec(a1,sr,1500,8000)/spec(a1,sr,50,300))
    a2=grab("Object.assign(window.__fx.FX,{d:3,cr:0.8,cb:0.9,dl:0.7});window.__fx.fxApply()"); print('crush rms',rms(a2),'HF',spec(a2,sr,1500,8000)/spec(a2,sr,50,300))
    a3=grab("Object.assign(window.__fx.FX,{d:0,m:1,mb:1});window.__fx.fxApply()"); print('chorus rms',rms(a3),'max',float(np.abs(a3).max()))
    a4=grab("Object.assign(window.__fx.FX,{m:3,mb:1,md:0.8});window.__fx.fxApply()"); print('phaser rms',rms(a4))
    a5=grab("Object.assign(window.__fx.FX,{m:4,mb:1,rf:0.6});window.__fx.fxApply()"); print('ring rms',rms(a5),'HF',spec(a5,sr,1500,8000)/spec(a5,sr,50,300))
    a6=grab("Object.assign(window.__fx.FX,{m:2,mb:0.8,mf:0.7});window.__fx.fxApply()"); print('flanger rms',rms(a6))
    # reverb: cauda depois de soltar
    pg.evaluate("Object.assign(window.__fx.FX,{d:0,m:0,rv:1,rt:4,rl:0.6});window.__fx.fxApply()"); pg.wait_for_timeout(1500)
    pg.evaluate("window.__send([0x90,45,100])"); pg.wait_for_timeout(600); pg.evaluate("window.__send([0x80,45,0]); window.__buf.length=0"); pg.wait_for_timeout(1200)
    tail=pg.evaluate("window.__buf.slice()"); print('reverb tail rms 0.3-1.2s após soltar',rms(tail), 'sem reverb: ', 0)
    pg.evaluate("Object.assign(window.__fx.FX,{rv:0,m:0,d:0});window.__fx.fxApply()")
    mx=lambda a: float(np.abs(np.array(a)).max())
    for lab,js in [('uni0',"Object.assign(window.__fx.P,{rg:0,un:0})"),('uni3',"Object.assign(window.__fx.P,{rg:0,un:3,ud:0.8})"),('ring osc',"Object.assign(window.__fx.P,{rg:1,un:0,l2:0.8,w2:'square',o2:1})")]:
        a=grab(js+";window.__fx.applyAll()"); print(lab,'rms',rms(a),'max',mx(a),'HF',spec(a,sr,1500,8000)/spec(a,sr,40,400))
    print('erros',errs); b.close()
