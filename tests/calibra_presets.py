import json,re,sys
from playwright.sync_api import sync_playwright
IDX='/home/claude/synthbass/index.html'; APPLY=len(sys.argv)>1 and sys.argv[1]=='apply'
INIT="""window.__inp={name:'SMK',onmidimessage:null};
  navigator.requestMIDIAccess=async()=>({inputs:new Map([['1',window.__inp]]),onstatechange:null});
  window.__send=(a)=>window.__inp.onmidimessage({data:new Uint8Array(a)});
  try{localStorage.clear()}catch(e){}
  const _AC=window.AudioContext; window.AudioContext=function(o){const c=new _AC(o); const ca=c.createAnalyser.bind(c); c.createAnalyser=()=>{const a=ca(); window.__an=a; return a;}; return c;};"""
res={}
OUT=sys.argv[1]
with sync_playwright() as p:
    b=p.chromium.launch(args=['--autoplay-policy=no-user-gesture-required'])
    pg=b.new_page(viewport={'width':1280,'height':800}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.add_init_script(INIT); pg.goto('http://localhost:8765/index.html'); pg.wait_for_timeout(200); pg.click('.brand'); pg.wait_for_timeout(900)
    print('engine',pg.evaluate('window.__auraEngine'))
    n=pg.evaluate("document.scripts[document.scripts.length-1].textContent.match(/^    F\\(\\{/gm).length")
    for i in range(n):
        pg.evaluate(f"__send([0xC0,{i}])"); pg.wait_for_timeout(200); pk=0; rs=0
        for note in (48,55):
            pg.evaluate(f"__send([0x90,{note},100])")
            m=pg.evaluate("""async()=>{let m=0,s=0,c=0;const b=new Float32Array(1024);for(let i=0;i<45;i++){__an.getFloatTimeDomainData(b);for(const v of b){const a=Math.abs(v); if(!(a<=1e9)) return [-1,0]; if(a>m)m=a; if(i>20){s+=v*v;c++}}await new Promise(r=>setTimeout(r,12));}return [m,Math.sqrt(s/Math.max(c,1))]}""")
            pg.evaluate(f"__send([0x80,{note},0])"); pg.wait_for_timeout(450); pk=max(pk,m[0]); rs=max(rs,m[1])
        res[pg.inner_text('#oBig').split(' ',1)[1]]=[round(pk,4),round(rs,4)]
    b.close()
json.dump(res,open(OUT,'w')); print(len(res),'presets',errs)
