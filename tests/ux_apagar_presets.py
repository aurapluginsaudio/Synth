from playwright.sync_api import sync_playwright
import json
with sync_playwright() as p:
    b=p.chromium.launch(); pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(800)
    pg.evaluate("""()=>{const mk=n=>({name:n}); localStorage.setItem('aura_user_presets_v1',JSON.stringify(['MEU A','MEU B','MEU C'].map(mk)));
      localStorage.setItem('aura_er_cache_v1',JSON.stringify(['ER ONE','ER TWO'].map(mk)));}""")
    pg.reload(); pg.wait_for_timeout(1000)
    pg.click('#oled'); pg.wait_for_timeout(300)
    n=lambda:pg.evaluate("document.querySelectorAll('#pList .prow').length")
    print('rows',n())
    pg.click('#manage'); pg.wait_for_timeout(200)
    print('delAll', pg.evaluate("[document.getElementById('delAll').hidden,document.getElementById('delAll').textContent]"))
    pg.screenshot(path='/tmp/mng.png')
    pg.locator('#pList .prow', has_text='MEU B').locator('.star').click(); pg.locator('#pList .prow', has_text='MEU B').locator('.star').click(); pg.wait_for_timeout(200)
    print('after del B',n(), pg.evaluate("JSON.parse(localStorage.getItem('aura_user_presets_v1')).map(p=>p.name)"))
    pg.locator('#pList .prow', has_text='ER ONE').locator('.star').click(); pg.locator('#pList .prow', has_text='ER ONE').locator('.star').click(); pg.wait_for_timeout(200)
    print('after del ER',n(), pg.evaluate("JSON.parse(localStorage.getItem('aura_er_cache_v1')).map(p=>p.name)"))
    pg.fill('#pSearch','MEU'); pg.wait_for_timeout(100)
    pg.click('#delAll'); pg.click('#delAll'); pg.wait_for_timeout(200)
    print('after bulk',n(), pg.evaluate("JSON.parse(localStorage.getItem('aura_user_presets_v1')).length"), errs)
    b.close()
