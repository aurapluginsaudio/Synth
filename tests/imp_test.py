import json
from playwright.sync_api import sync_playwright
src=open('/tmp/feat_test.py').read(); exec(src.split("res={}; errs=[]")[0])
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT); pg.goto(URL); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(900)
    pg.set_input_files('#fileIn',['/tmp/TESTE_OSC3.mdp','/home/claude/TAURUS.mdp']); pg.wait_for_timeout(800)
    u=pg.evaluate("JSON.parse(localStorage.getItem('aura_user_presets_v1'))")
    for x in u:
        if x['name'].startswith('TESTE') : print({k:x[k] for k in ('name','l3','w3','o3','d3','k3','nc','ovl','lsr','lp','lf','pa','pd','dm','dt','df','lr','lwv')})
        if x['name'].startswith('TAURUS'): print('TAURUS importado: l3',x['l3'],'nc',x['nc'],'ovl',x['ovl'],'dm',x['dm'],'lsr',x['lsr'])
    # aprendizado de HOLD pelo controlador
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mLearn'); pg.wait_for_timeout(200); pg.click('#lHold'); pg.wait_for_timeout(100)
    pg.evaluate('__send([0xB0,22,127])'); pg.wait_for_timeout(200); pg.click('#lArp'); pg.evaluate('__send([0xB0,23,127])'); pg.wait_for_timeout(200); pg.click('#learnDone')
    pg.evaluate('__send([0xB0,22,127])'); pg.wait_for_timeout(150); print('após CC22:',pg.inner_text('#oSub'))
    pg.evaluate('__send([0xB0,22,0])'); pg.evaluate('__send([0xB0,23,127])'); pg.wait_for_timeout(200); print('após CC23 (arp):',pg.inner_text('#oSub'))
    pg.evaluate('__send([0xB0,23,0])'); pg.evaluate('__send([0xB0,23,127])'); pg.wait_for_timeout(200); print('CC23 de novo:',pg.inner_text('#oSub'))
    # edição do delay marca o preset como alterado
    pg.click('#menuBtn'); pg.wait_for_timeout(200); pg.click('#mDly'); pg.wait_for_timeout(200); pg.fill('#dlyBody .fxrow:nth-child(3) input','500'); pg.dispatch_event('#dlyBody .fxrow:nth-child(3) input','input'); pg.wait_for_timeout(150)
    print('visor após mexer no delay:',pg.inner_text('#oBig'),'| status delay:',pg.evaluate("document.getElementById('mDlySt').textContent"))
    print('erros',errs); b.close()
