#include "AuraEngine.h"
#include <cstdio>
using namespace aura;
int main(){ for(int mode=0;mode<3;mode++){ Engine e; e.prepare(48000); for(int k=0;k<NP;k++) e.p[k]=0; e.p[oct]=-1; e.p[wave]=1; e.p[w2]=2; e.p[lvl]=0.75f; e.p[l2]=0.8f; e.p[cut]=1; e.p[pol]=4; e.p[vol]=1; e.p[s]=1; e.p[a]=0.002f; e.p[e1]=e.p[e2]=e.p[e3]=1; e.p[mo]=1;e.p[mf]=1;e.p[mb]=1;e.p[mx]=.5f;
  if(mode==1){ e.p[un]=3; e.p[ud]=0.8f; } if(mode==2) e.p[rg]=1; e.reset(); e.noteOn(45,100); std::vector<float> o(48000); for(size_t i=0;i<o.size();i+=128) e.process(&o[i],128); double r=0,mx=0; bool nan=false; for(float x:o){ r+=x*x; mx=std::max(mx,(double)std::fabs(x)); if(x!=x) nan=true; } printf("modo %d rms %.3f max %.3f nan %d\n",mode,std::sqrt(r/o.size()),mx,nan); } }
