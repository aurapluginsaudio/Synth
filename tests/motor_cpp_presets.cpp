#include "AuraEngine.h"
#include "Presets.h"
#include <cstdio>
#include <cstring>
int main(int argc,char**argv){
  FILE* fo=fopen(argv[1],"w"); fprintf(fo,"{");
  for(int pi=0;pi<aura::kNumFactory;pi++){
    double pk=0,rs=0;
    for(int note: {48,55}){
      aura::Engine e; e.prepare(48000); for(int k=0;k<aura::NP;k++) e.p[k]=aura::kFactory[pi].v[k]; e.reset();
      e.noteOn(note,100);
      double m=0,s=0; int c=0; const int N=128;
      float buf[N]; double rms=0;
      for(int b=0;b<(int)(0.54*48000/N);b++){ e.process(buf,N); for(int i=0;i<N;i++){ double v=e.preOut; (void)v; } 
        // preOut is last only; recompute per-sample by calling with N=1
      }
      aura::Engine f; f.prepare(48000); for(int k=0;k<aura::NP;k++) f.p[k]=aura::kFactory[pi].v[k]; f.reset(); f.noteOn(note,100);
      float o; int total=(int)(0.54*48000);
      for(int i=0;i<total;i++){ f.process(&o,1); double v=std::fabs(f.preOut); if(v>m)m=v; if(i>0.25*48000){s+=v*v;c++;} }
      if(m>pk)pk=m; double r=std::sqrt(s/c); if(r>rs)rs=r;
    }
    fprintf(fo,"%s\"%s\":[%.4f,%.4f]",pi?",":"",aura::kFactory[pi].name,pk,rs);
  }
  fprintf(fo,"}"); fclose(fo);
}
