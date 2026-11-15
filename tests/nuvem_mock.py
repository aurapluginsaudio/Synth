import json
from playwright.sync_api import sync_playwright
INIT="""try{localStorage.clear()}catch(e){}"""
log=[]; rows=[{'name':'NUVEM1','data':{'name':'NUVEM1','cut':0.3,'wave':'sawtooth'}},{'name':'ER_X','data':{'name':'ER_X','cut':0.6,'er':True}}]
def route(r):
    u=r.request.url; m=r.request.method; log.append((m,u.split('supabase.co')[1][:70],(r.request.post_data or '')[:80]))
    if 'grant_type=password' in u: r.fulfill(status=200,content_type='application/json',body=json.dumps({'access_token':'a','refresh_token':'r','expires_in':3600}))
    elif m=='GET': r.fulfill(status=200,content_type='application/json',body=json.dumps(rows))
    elif m=='POST': r.fulfill(status=201,body='')
    else: r.fulfill(status=204,body='')
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(INIT); pg.route('**/*.supabase.co/**',route)
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(500)
    n0=pg.evaluate("document.querySelectorAll('#pList .prow').length") if False else None
    pg.click('#menuBtn'); pg.click('#mCloud'); pg.fill('#cEmail','a@b.c'); pg.fill('#cPass','x'); pg.click('#cLogin'); pg.wait_for_timeout(800)
    print(pg.inner_text('#cloudSt')); pg.screenshot(path='/tmp/cloud.png')
    pg.evaluate("document.getElementById('dlgCloud').classList.remove('open')")
    pg.click('#oled'); pg.fill('#pSearch','NUVEM'); print('NUVEM1 na lista:',pg.evaluate("document.querySelectorAll('#pList .prow').length")); pg.fill('#pSearch','ER_X'); print('ER_X:',pg.evaluate("document.querySelectorAll('#pList .prow').length"))
    pg.evaluate("document.getElementById('dlgList').classList.remove('open')")
    # salvar novo preset -> envia
    pg.click('#mSave') if False else None
    pg.click('#menuBtn'); pg.click('#mSave'); pg.fill('#pName','TESTE UP'); pg.click('#dNew'); pg.wait_for_timeout(2200)
    # excluir
    pg.click('#menuBtn'); pg.click('#mSave'); pg.click('#dDel'); pg.click('#dDel'); pg.wait_for_timeout(2200)
    for l in log: print(l)
    print('errs',errs); b.close()
