#include "AuraEngine.h"
#include <cstdio>
#include <vector>
#include <functional>
using namespace aura;
std::vector<double> freqs(const std::vector<float>& b,double sr){ std::vector<double> t,f; for(size_t k=1;k<b.size();k++) if(b[k-1]<0&&b[k]>=0) t.push_back(k-1+(-b[k-1])/(b[k]-b[k-1])); for(size_t i=21;i+1<t.size();i++) f.push_back(sr/(t[i+1]-t[i])); return f; }
int main(){
  auto run=[&](std::function<void(Engine&)> cfg,double secs){ Engine e; e.prepare(48000); for(int k=0;k<NP;k++) e.p[k]=0; e.p[oct]=-1; e.p[wave]=0; e.p[lvl]=0.75f; e.p[cut]=1; e.p[pol]=4; e.p[vol]=1; e.p[s]=1; e.p[a]=0.002f; e.p[fa]=0.002f; e.p[fd]=0.3f; e.p[fs]=1; e.p[lr]=5; e.p[e1]=e.p[e2]=e.p[e3]=1; e.p[mo]=1; e.p[mf]=1; e.p[mb]=1; e.p[mx]=0.5f; e.p[r]=0.1f; e.p[d]=0.3f; e.p[fr]=0.2f; e.p[leg]=1; cfg(e); e.reset(); e.noteOn(57,100); // 220Hz*0.5=110
    std::vector<float> o((size_t)(secs*48000)); for(size_t i=0;i<o.size();i+=128) e.process(&o[i],std::min<size_t>(128,o.size()-i)); return o; };
  auto mm=[&](const char* n,std::vector<float> o){ auto f=freqs(o,48000); double mn=1e9,mx=0; for(double x:f){ mn=std::min(mn,x); mx=std::max(mx,x);} printf("%s min %.2f max %.2f\n",n,mn,mx); };
  mm("sem mm",run([](Engine& e){},1.0));
  mm("mm LFO roda 1 (103.8..116.5)",run([](Engine& e){ e.p[aura::mm]=1; e.p[mx]=1; e.mod=1; },1.0));
  mm("mm EG fs=1 mx=0 (116.5)",run([](Engine& e){ e.p[aura::mm]=1; e.p[ma]=1; e.p[mx]=0; e.mod=1; },1.0));
  mm("mm roda 0",run([](Engine& e){ e.p[aura::mm]=1; e.p[mx]=1; e.mod=0; },1.0));
  Engine e; e.prepare(48000); e.tt=1; printf("E4 pit %.2f ET %.2f | A4+100c tune: ",e.noteFreq(64)*2, Engine::mtof(64)); e.tt=0; e.tun=100; printf("%.2f\n",e.noteFreq(69)*2);
}
