#include "Fx.h"
#include <cstdio>
using namespace aura;
int main(){ Fx f; f.prepare(48000); const int N=48000; std::vector<float> in(N), L(N), R(N);
  auto rms=[&](int a,int b){ double s=0; for(int i=a;i<b;i++) s+=L[i]*L[i]; return std::sqrt(s/(b-a)); };
  for(int i=0;i<N;i++) in[i]=(i<24000)?0.5f*std::sin(6.2831853*55*i/48000.0)+0.2f*std::sin(6.2831853*110*i/48000.0):0.f;
  const char* nm[]={"off","dist","fuzz","crush"}; for(int d=0;d<4;d++){ FxParams q; q.d=d; f.prepare(48000); f.process(q,in.data(),L.data(),R.data(),N); printf("EFX1 %s rms %.3f\n",nm[d],rms(8000,20000)); }
  const char* mn[]={"off","chorus","flanger","phaser","anel"}; for(int m=0;m<5;m++){ FxParams q; q.m=m; q.mb=1; f.prepare(48000); f.process(q,in.data(),L.data(),R.data(),N); double mx=0; for(float v:L) mx=std::max(mx,(double)std::fabs(v)); printf("EFX2 %s rms %.3f max %.3f\n",mn[m],rms(8000,20000),mx); }
  for(int t=0;t<6;t++){ FxParams q; q.rv=1; q.rt=t; q.rl=0.6f; f.prepare(48000); f.process(q,in.data(),L.data(),R.data(),N); printf("reverb %d tail rms(0.6-0.9s) %.4f (0.9-1s) %.4f  nan? %d\n",t,rms(28800,43200),rms(43200,48000),(int)std::isnan(L[N-1])); }
}
