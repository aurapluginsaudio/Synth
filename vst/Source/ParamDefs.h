// Definição dos parâmetros do plugin (mesma ordem de aura::P). (c) 2026 Thiago R. Galvão
#pragma once
#include "AuraEngine.h"
namespace aura {
enum Kind { F, I, B, W, LW };
struct Def { const char* id; const char* name; float mn, mx, ex; Kind k; };
// mesma ordem de aura::P
static const Def kDefs[aura::NP] = {
 {"oct","Oitava",-3,1,1,I},{"wave","Osc 1 Onda",0,2,1,W},{"pw1","Osc 1 Largura",0.05f,0.5f,1,F},{"lvl","Osc 1 Nivel",0,1,1,F},
 {"w2","Osc 2 Onda",0,2,1,W},{"pw2","Osc 2 Largura",0.05f,0.5f,1,F},{"l2","Osc 2 Nivel",0,1,1,F},{"d2","Osc 2 Detune (st)",-7,7,1,F},
 {"o2","Osc 2 Oitava",-2,3,1,I},{"sync","Osc 2 Sync",0,1,1,B},{"sub","Sub Nivel",0,1,1,F},{"sw","Sub Quadrada",0,1,1,B},{"nz","Ruido Nivel",0,1,1,F},
 {"cut","Filtro Cutoff",0,1,1,F},{"res","Filtro Ressonancia",0,1,1,F},{"fenv","Filtro Env Amt (oit)",0,4,1,F},{"kt","Filtro Teclado",0,1,1,F},
 {"drv","Filtro Drive",0,1,1,F},{"pol","Filtro Polos",1,4,1,I},{"glide","Glide (s)",0,0.4f,2,F},{"pa","Pitch Env Quant (st)",0,48,2,F},
 {"pd","Pitch Env Decay (s)",0.01f,1.5f,2,F},{"lr","LFO Rate (Hz)",0.1f,30,2,F},{"lwv","LFO Onda",0,1,1,LW},{"lp","LFO Afinacao (st)",0,12,2,F},
 {"lf","LFO Filtro (oit)",0,3,1,F},{"lw","LFO Largura",0,1,1,F},{"fa","Filtro Attack (s)",0.002f,1,3,F},{"fd","Filtro Decay (s)",0.02f,2,2,F},
 {"fs","Filtro Sustain",0,1,1,F},{"fr","Filtro Release (s)",0.02f,2,2,F},{"a","Volume Attack (s)",0.002f,1,3,F},{"d","Volume Decay (s)",0.02f,2,2,F},
 {"s","Volume Sustain",0,1,1,F},{"r","Volume Release (s)",0.02f,2,2,F},{"leg","Legato",0,1,1,B},{"vol","Volume",0,3,1,F},
 {"l3","Osc 3 Nivel",0,1,1,F},{"w3","Osc 3 Onda",0,2,1,W},{"o3","Osc 3 Oitava",-3,3,1,I},{"d3","Osc 3 Detune (st)",-7,7,1,F},
 {"k3","Osc 3 Segue Teclado",0,1,1,B},{"nc","Ruido Rosa",0,1,1,B},{"ovl","Overload",0,1,1,F},{"lsr","LFO Fonte (0 LFO, 1 Osc3, 2 Rand)",0,2,1,I},
 {"ec","Envelopes Lineares",0,1,1,B},{"dt","Delay Tempo (s)",0.02f,1,1,F},{"df","Delay Repeticoes",0,0.9f,1,F},{"dm","Delay Mix",0,1,1,F}};

}
