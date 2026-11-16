// Verifica no Node: modos de filtro (LP/BP/HP, ácido), LFO 2 (vibrato com atraso) e erro/FM
const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const a=html.indexOf('const WORKLET = `')+'const WORKLET = `'.length, b=html.indexOf('`;',a);
const src=html.slice(a,b).replace(/\\\\/g,'\\');
global.sampleRate=48000; global.AudioWorkletProcessor=class{ constructor(){ this.port={onmessage:null,postMessage(){}}; } };
const procs={}; global.registerProcessor=(n,c)=>{ procs[n]=c; }; eval(src);
function run(cfg,secs,cut,pre){
  const v=new procs['aura-voice'](); Object.assign(v.c,cfg); if(pre) pre(v);
  const N=128, total=Math.floor(secs*48000/N), out=[];
  for(let blk=0;blk<total;blk++){ const pr={freq:[110],detune:[0],pitch:[0],cutoff:[cut||800],cutmod:[0],pwmod:[0],fe:[0],lfoin:new Float32Array(N)}; const o=[new Float32Array(N)]; v.process([[]],[o],pr); out.push(...o[0]); }
  return out;
}
function band(buf,lo,hi){ const x=buf.slice(-8192); let e=0; for(let f=lo;f<hi;f+=55){ let re=0,im=0; for(let i=0;i<x.length;i++){ const w=0.5-0.5*Math.cos(2*Math.PI*i/x.length); re+=x[i]*w*Math.cos(2*Math.PI*f*i/48000); im+=x[i]*w*Math.sin(2*Math.PI*f*i/48000); } e+=re*re+im*im; } return Math.sqrt(e); }
const base={w1:1,w2:1,l1:.75,l2:0,ls:0,nz:0,res:0,drv:0,pol:4,l3:0,w3:1,r3:1,k3:1};
const bands=[[40,300],[300,1500],[1500,6000]];
for(const [nm,cfg] of [['LP24',{}],['LP12',{pol:2}],['BP12',{fm:1,pol:2}],['BP24',{fm:1}],['HP12',{fm:2,pol:2}],['HP24',{fm:2}],['ÁCIDO',{fk:1}],['ÁCIDO res.8',{fk:1,res:.8}]]){
  const o=run(Object.assign({},base,cfg),1,800); const mx=Math.max(...o.map(Math.abs)); console.log(nm.padEnd(12),bands.map(b=>band(o,b[0],b[1]).toFixed(1)).join(' | '),' pico',mx.toFixed(2),isFinite(mx)?'':'NaN!');
}
// LFO 2: vibrato ±100 cent com atraso 0,5 s: amplitude do desvio de pitch cresce
function zc(buf){ const t=[]; for(let k=1;k<buf.length;k++) if(buf[k-1]<0&&buf[k]>=0) t.push(k-1+(-buf[k-1])/(buf[k]-buf[k-1])); return t.slice(1).map((x,i)=>48000/(x-t[i])); }
const cfg2=Object.assign({},base,{pol:4,l2p:0.5,l2r:5,l2d:0.5,l2w:0});
for(const [lab,from,to] of [['0–0,2 s',0.05*48000,0.25*48000],['0,8–1,5 s',0.8*48000,1.5*48000]]){ const f=zc(run(cfg2,1.6,12000,v=>{v.q2t=0;}).slice(from,to)); console.log('LFO2 vibrato',lab,'min',Math.min(...f).toFixed(1),'max',Math.max(...f).toFixed(1),'(110 Hz ±100 c = 103.8..116.5)'); }
// erro aleatório: pr=+50 cent
const fe=zc(run(Object.assign({},base,{pr:50}),0.6,12000)).slice(10); console.log('pr=+50c',(fe.reduce((a,b)=>a+b)/fe.length).toFixed(2),'esperado',(110*Math.pow(2,50/1200)).toFixed(2));
if(process.argv[2]==='harm'){ for(const [nm,cfg] of [['BP12',{fm:1,pol:2}],['LP12',{pol:2}]]){ const o=run(Object.assign({},base,cfg),1,800); const x=o.slice(-9600); const r=[]; for(const n of [1,2,4,7,10,14,20,30]){ const f=110*n; let re=0,im=0; for(let i=0;i<x.length;i++){ re+=x[i]*Math.cos(2*Math.PI*f*i/48000); im+=x[i]*Math.sin(2*Math.PI*f*i/48000);} r.push(n+':'+(2*Math.hypot(re,im)/x.length).toFixed(3)); } console.log(nm,r.join(' ')); } }
