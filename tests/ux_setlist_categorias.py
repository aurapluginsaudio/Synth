from playwright.sync_api import sync_playwright
INIT="""window.__inp={name:'SMK',onmidimessage:null};
  navigator.requestMIDIAccess=async()=>({inputs:new Map([['1',window.__inp]]),onstatechange:null});
  window.__send=(a)=>window.__inp.onmidimessage({data:new Uint8Array(a)});try{localStorage.clear()}catch(e){}"""
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required']); pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(300); pg.click('.brand'); pg.wait_for_timeout(600)
    pg.click('#oled'); pg.wait_for_timeout(200)
    cnt=lambda: pg.evaluate("document.querySelectorAll('#pList .prow').length")
    print('todos',cnt())
    for c in ['SUB','PLUCK','LEAD','PAD','FX','MEUS']:
        pg.click(f'#pCats button:text-is("{c}")'); print(c,cnt())
    pg.click('#pCats button:text-is("TODOS")'); pg.fill('#pSearch','moog'); print('busca moog',cnt()); pg.fill('#pSearch','')
    pg.screenshot(path='/tmp/ux_list.png'); pg.keyboard.press('Escape'); pg.click('#dlgList [data-close].btn') if False else None
    pg.evaluate("document.getElementById('dlgList').classList.remove('open')")
    # setlist
    for i in (5,20,40):
        pg.evaluate(f"__send([0xC0,{i}])"); pg.wait_for_timeout(80); pg.click('#menuBtn'); pg.click('#mSet'); pg.click('#setAdd'); pg.evaluate("document.getElementById('dlgSet').classList.remove('open')")
    pg.click('#menuBtn'); pg.click('#mSet'); pg.click('#setOn'); print('setlist rows',pg.evaluate("document.querySelectorAll('#setBody .prow').length")); pg.screenshot(path='/tmp/ux_set.png')
    pg.evaluate("document.getElementById('dlgSet').classList.remove('open')")
    nm=lambda: pg.inner_text('#oBig')
    pg.evaluate("__send([0xC0,1])"); pg.wait_for_timeout(100); print('PC1 ->',nm())
    pg.click('#pNext'); print('next ->',nm()); pg.click('#pNext'); print('next ->',nm()); pg.click('#pPrev'); print('prev->',nm())
    # mapeamento
    pg.click('#menuBtn'); pg.click('#mMap'); print('map rows',pg.evaluate("document.querySelectorAll('#mapBody .mrow').length"), pg.inner_text('#mapBody')[:60])
    pg.screenshot(path='/tmp/ux_map.png'); print('errs',errs); b.close()
