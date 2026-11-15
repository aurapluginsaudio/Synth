from playwright.sync_api import sync_playwright
src=open('/tmp/cal_all.py').read(); INIT=src.split('INIT="""')[1].split('"""')[0]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m: errs.append(m.text) if m.type=='error' else None)
    pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(200); pg.click('.brand'); pg.wait_for_timeout(900)
    print('motor',pg.evaluate('window.__auraEngine'),'comp',pg.evaluate('window.__auraComp'))
    # latência do disparo: tempo até o analisador ver sinal depois do noteOn
    r=pg.evaluate("""async()=>{const b=new Float32Array(256);const t0=performance.now();__send([0x90,48,100]);for(let i=0;i<400;i++){__an.getFloatTimeDomainData(b);if(b.some(v=>Math.abs(v)>0.02))return performance.now()-t0;await new Promise(r=>requestAnimationFrame(r));}return -1}""")
    print('primeiro sinal após a nota (ms, inclui quadro do navegador):',round(r,1))
    pg.evaluate("__send([0x80,48,0])"); pg.wait_for_timeout(400)
    # troca de preset, legato, nota repetida: sem erro
    for i in (3,50,100):
        pg.evaluate(f"__send([0xC0,{i}])"); pg.wait_for_timeout(100); pg.evaluate("__send([0x90,45,90])"); pg.wait_for_timeout(120); pg.evaluate("__send([0x80,45,0])")
    pg.click('#menuBtn'); pg.wait_for_timeout(300); print(pg.inner_text('#engineInfo'))
    print('erros',errs); b.close()
