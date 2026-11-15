from playwright.sync_api import sync_playwright
src=open('/tmp/feat_test.py').read(); exec(src.split("res={}; errs=[]")[0])
HOOK=open('/tmp/arp_test.py').read().split('HOOK="""')[1].split('"""')[0]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT+HOOK); pg.goto(URL); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(1000)
    send=lambda a: pg.evaluate(f'__send({a})'); lg=lambda: [l[1] for l in pg.evaluate('window.__log')]
    send([0xC0,111]); pg.wait_for_timeout(200)
    def setprio(n):
        pg.click('#menuBtn'); pg.wait_for_timeout(150)
        while pg.inner_text('#mPrioSt')!=n: pg.click('#mPrio'); pg.wait_for_timeout(50)
        pg.keyboard.press('Escape'); pg.wait_for_timeout(150)
    for name in ('ÚLTIMA NOTA','MAIS GRAVE','MAIS AGUDA'):
        setprio(name); pg.evaluate('window.__log.length=0')
        send([0x90,48,100]); pg.wait_for_timeout(100); send([0x90,55,100]); pg.wait_for_timeout(100); a=lg()
        send([0x80,55,0]); pg.wait_for_timeout(100); send([0x80,48,0]); pg.wait_for_timeout(100); b2=lg()
        print(name,'→ ao tocar 48 e 55:',a,'| ao soltar:',b2[len(a):])
    print(errs); b.close()
