const fs=require('fs');
const html=fs.readFileSync(__dirname+'/../index.html','utf8');
const a=html.indexOf('const WORKLET = `')+'const WORKLET = `'.length, b=html.indexOf('`;',a);
const src=html.slice(a,b).replace(/\\\\/g,'\\');
global.sampleRate=48000; global.AudioWorkletProcessor=class{ constructor(){ this.port={}; } };
const procs={}; global.registerProcessor=(n,c)=>{ procs[n]=c; };
eval(src);
function run(cfg,secs,pr0){
  const v=new procs['aura-voice'](); Object.assign(v.c,cfg);
  const N=128, total=Math.floor(secs*48000/N), out=[];
  for(let blk=0;blk<total;blk++){
    const t0=blk*N; const pr={freq:[110],detune:[0],pitch:[0],cutoff:[12000],cutmod:[0],pwmod:[0],fe:[0],lfoin:new Float32Array(N)};
    for(let i=0;i<N;i++) pr.lfoin[i]=Math.sin(2*Math.PI*5*(t0+i)/48000);
    if(pr0) Object.assign(pr,pr0(blk));
    const o=[new Float32Array(N)]; v.process([[]],[o],pr); out.push(...o[0]);
  }
  return out;
}
function freqs(buf){ const t=[]; for(let k=1;k<buf.length;k++) if(buf[k-1]<0&&buf[k]>=0) t.push(k-1+(-buf[k-1])/(buf[k]-buf[k-1])); return t.slice(1).map((x,i)=>48000/(x-t[i])); }
const base={w1:0,w2:1,l1:.75,l2:0,ls:0,nz:0,res:0,drv:0,pol:4,l3:0,w3:1,r3:1,k3:1};
const f0=freqs(run(Object.assign({},base,{mm:0}),0.8)).slice(20); console.log('sem mm',Math.min(...f0).toFixed(2),Math.max(...f0).toFixed(2));
const f1=freqs(run(Object.assign({},base,{mm:1,mb:1,mx:1,md:0}),0.8)).slice(20); console.log('mm md=0',Math.min(...f1).toFixed(2),Math.max(...f1).toFixed(2));
const f2=freqs(run(Object.assign({},base,{mm:1,mb:1,mx:1,md:1,mo:1}),0.8)).slice(20); console.log('mm md=1 (esperado 110*2^(±100/1200)=103.8..116.6)',Math.min(...f2).toFixed(2),Math.max(...f2).toFixed(2));
const f3=freqs(run(Object.assign({},base,{mm:1,mb:1,mx:1,md:1,mo:0}),0.8)).slice(20); console.log('mm md=1 mo=0',Math.min(...f3).toFixed(2),Math.max(...f3).toFixed(2));
// filtro EG como fonte A, fe=1 constante, mx=0: pitch +100c
const f4=freqs(run(Object.assign({},base,{mm:1,ma:1,mx:0,md:1,mo:1}),0.8,()=>({fe:[1]}))).slice(20); console.log('EG=1 mx=0 -> +100c esperado 116.5',Math.min(...f4).toFixed(2),Math.max(...f4).toFixed(2));
