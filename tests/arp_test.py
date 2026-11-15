import json
from playwright.sync_api import sync_playwright
src=open('/tmp/feat_test.py').read()
exec(src.split("res={}; errs=[]")[0])
HOOK="""window.__log=[];const _s=AudioParam.prototype.setValueAtTime;AudioParam.prototype.setValueAtTime=function(v,t){if(v>40&&v<200)window.__log.push([Math.round(performance.now()),+v.toFixed(1)]);return _s.call(this,v,t)};
const _t=AudioParam.prototype.setTargetAtTime;AudioParam.prototype.setTargetAtTime=function(v,t,c){if(v>40&&v<200)window.__log.push([Math.round(performance.now()),+v.toFixed(1)]);return _t.call(this,v,t,c)};"""
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT+HOOK); pg.goto(URL); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(1000)
    send=lambda a: pg.evaluate(f'__send({a})')
    send([0xC0,111]); pg.wait_for_timeout(200)
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mArp'); pg.wait_for_timeout(200)
    for t in ('LIGADO',): pg.click(f'#arpBody .fxrow:first-child .chips >> text="{t}"')
    pg.keyboard.press('Escape'); pg.wait_for_timeout(200)
    pg.evaluate('window.__log.length=0')
    send([0x90,48,100]); send([0x90,52,100]); send([0x90,55,100]); pg.wait_for_timeout(2500)
    log=pg.evaluate('window.__log'); print('freq logadas:',[(l[0]-log[0][0],l[1]) for l in log][:20])
    send([0x80,48,0]); send([0x80,52,0]); send([0x80,55,0]); pg.wait_for_timeout(400)
    n=len(pg.evaluate('window.__log')); pg.wait_for_timeout(800); print('eventos novos depois de soltar (deve ser 0):',len(pg.evaluate('window.__log'))-n,errs)
    b.close()
