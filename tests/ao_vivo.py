import sys,os,numpy as np
exec(open(os.path.join(os.path.dirname(os.path.abspath(__file__)),'_fxhead.py')).read())
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1440,'height':1200}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(700)
    pg.mouse.click(300,600); pg.wait_for_timeout(500)
    rms=lambda a: float(np.sqrt((np.array(a)**2).mean())) if len(a) else 0
    # pânico silencia nota presa
    pg.evaluate("window.__buf.length=0; window.__send([0x90,45,100])"); pg.wait_for_timeout(500)
    a=pg.evaluate("window.__buf.slice()"); print('tocando rms',round(rms(a),3))
    pg.click('#panicBtn'); pg.wait_for_timeout(900); pg.evaluate("window.__buf.length=0"); pg.wait_for_timeout(500)
    a=pg.evaluate("window.__buf.slice()"); print('após pânico rms',round(rms(a),4))
    # CC123 também
    pg.evaluate("window.__send([0x90,48,100])"); pg.wait_for_timeout(300); pg.evaluate("window.__send([0xB0,123,0])"); pg.wait_for_timeout(900); pg.evaluate("window.__buf.length=0"); pg.wait_for_timeout(400)
    print('após CC123 rms',round(rms(pg.evaluate("window.__buf.slice()")),4))
    # preset de emergência
    pg.evaluate("window.__live.safePreset()"); pg.wait_for_timeout(300)
    pg.evaluate("window.__buf.length=0; window.__send([0x90,45,100])"); pg.wait_for_timeout(600)
    print('seguro rms',round(rms(pg.evaluate("window.__buf.slice()")),3), pg.inner_text('#oSub')); pg.evaluate("window.__send([0x80,45,0])")
    # modo leve
    pg.evaluate("window.__fx.FX.rv=1;window.__fx.FX.d=1;window.__fx.fxApply();window.__live.setLite(1)"); print('leve',pg.evaluate("window.__live.liteOn()"), 'FX preservado',pg.evaluate("[window.__fx.FX.rv,window.__fx.FX.d]"))
    pg.evaluate("window.__live.setLite(0)")
    # linha de efeitos
    pg.click('#fxT1'); pg.click('#fxT2'); pg.click('#fxT3'); print('tipos',pg.evaluate("[window.__fx.FX.d,window.__fx.FX.m,window.__fx.FX.rv]"),[pg.inner_text('#fxT%d'%i) for i in (1,2,3)])
    box=pg.locator('#sec_fx1 .dial').first.bounding_box(); pg.mouse.move(box['x']+box['width']/2,box['y']+box['height']/2); pg.mouse.down(); pg.mouse.move(box['x']+box['width']/2,box['y']-60,steps=6); pg.mouse.up()
    print('drive',pg.evaluate("window.__fx.FX.dr"))
    # CC em lote: 50 mensagens seguidas -> valor final correto
    pg.evaluate("window.__fx.P.cut=0.2")
    # estado de áudio
    pg.screenshot(path='/tmp/v9_a.png'); print('scroll',pg.evaluate("[document.documentElement.scrollHeight,innerHeight]"))
    print('erros',errs); b.close()
