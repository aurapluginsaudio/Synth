# Celular e tablet só funcionam na horizontal; em pé aparece o aviso. Também confere nome das teclas, ids únicos e registro de erros.
import re,os,sys
from playwright.sync_api import sync_playwright
URL='http://localhost:8765/index.html'; falhas=[]
def ok(c,m):
    print(('  ok ' if c else '  FALHA ')+m); 
    if not c: falhas.append(m)
raiz=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..')
ids=re.findall(r'\bid="([^"]+)"',open(os.path.join(raiz,'index.html'),encoding='utf-8').read())
dup=sorted({i for i in ids if ids.count(i)>1}); ok(not dup,'nenhum id repetido no HTML %s'%dup)
with sync_playwright() as p:
    b=p.chromium.launch()
    def pagina(vw,vh,toque):
        c=b.new_context(viewport={'width':vw,'height':vh},has_touch=toque,is_mobile=toque); pg=c.new_page(); erros=[]; pg.on('pageerror',lambda e:erros.append(str(e))); pg.goto(URL); pg.wait_for_timeout(1000); return c,pg,erros
    est=lambda pg:pg.evaluate("()=>({rot:document.documentElement.classList.contains('rot'),aviso:getComputedStyle(document.getElementById('girar')).display,painel:getComputedStyle(document.querySelector('.synth')).visibility})")
    for nome,vw,vh in [('celular em pé',390,844),('tablet em pé',820,1180)]:
        c,pg,e=pagina(vw,vh,True); r=est(pg); ok(r['rot'] and r['aviso']=='flex' and r['painel']=='hidden','%s: mostra o aviso e esconde o painel'%nome); ok(not e,'%s: sem erro de script'%nome); c.close()
    for nome,vw,vh in [('celular deitado',844,390),('tablet deitado',1180,820)]:
        c,pg,e=pagina(vw,vh,True); r=est(pg); ok(not r['rot'] and r['aviso']=='none' and r['painel']=='visible','%s: mostra o painel'%nome); ok(not e,'%s: sem erro de script'%nome); c.close()
    c,pg,e=pagina(700,900,False); r=est(pg); ok(not r['rot'],'janela estreita no computador não é bloqueada'); c.close()
    c,pg,e=pagina(390,844,True); pg.set_viewport_size({'width':844,'height':390}); pg.wait_for_timeout(800); ok(not est(pg)['rot'],'girar para deitado remove o aviso'); pg.set_viewport_size({'width':390,'height':844}); pg.wait_for_timeout(800); ok(est(pg)['rot'],'girar para em pé volta o aviso'); c.close()
    c,pg,e=pagina(1280,800,False)
    n=pg.evaluate("()=>[...document.querySelectorAll('.k')].filter(k=>!k.getAttribute('aria-label')).length"); ok(n==0,'todas as teclas têm nome (%d sem)'%n)
    nm=pg.evaluate("()=>[document.querySelectorAll('.k')[0].getAttribute('aria-label'),document.querySelectorAll('.k')[1].getAttribute('aria-label')]"); ok(nm[0].startswith('Dó ') and 'sustenido' in nm[1],'nomes em português: %s'%nm)
    ok(pg.evaluate("typeof window.auraDbg==='function' && (window.auraDbg(new Error('teste')), window.__auraErros.pop()==='teste')"),'erros são registrados em vez de sumir')
    ok(pg.evaluate("document.getElementById('lArpLed')!==document.getElementById('lArp')"),'lâmpada ARP e botão ARP do modo aprender são elementos diferentes')
    c.close(); b.close()
print('Resultado:', 'FALHOU' if falhas else 'tudo certo'); sys.exit(1 if falhas else 0)
