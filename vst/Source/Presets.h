// Gerado a partir dos presets de fábrica do AURA Synth Bass. Autor: Thiago R. Galvão (AURA-SB-TRG-2026)
#pragma once
namespace aura {
static const int kNumParams = 59;
static const char* const kParamIds[kNumParams] = {"oct","wave","pw1","lvl","w2","pw2","l2","d2","o2","sync","sub","sw","nz","cut","res","fenv","kt","drv","pol","glide","pa","pd","lr","lwv","lp","lf","lw","fa","fd","fs","fr","a","d","s","r","leg","vol","l3","w3","o3","d3","k3","nc","ovl","lsr","ec","dt","df","dm","mm","ma","mb","mx","mo","mf","e1","e2","e3","kts"};
struct FactoryPreset { const char* name; float v[kNumParams]; };
static const int kNumFactory = 2;
static const FactoryPreset kFactory[kNumFactory] = {
{"CHURCH SYNTH BASS",{-2.0f,2.0f,0.5f,1.0f,1.0f,0.5f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.0f,0.056f,0.0f,1.04f,0.667f,0.0f,4.0f,0.0f,0.0f,0.15f,5.5f,0.0f,0.0f,0.0f,0.0f,0.002f,0.25f,0.6f,0.25f,0.002f,0.25f,0.6f,0.25f,1.0f,1.69f,0.0f,1.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,0.3f,0.35f,0.0f,0.0f,0.0f,1.0f,0.5f,1.0f,1.0f,1.0f,1.0f,1.0f,0.0f}},
{"DEEP SUB BASS",{-1.0f,2.0f,0.5f,0.75f,1.0f,0.5f,0.0f,0.0f,0.0f,0.0f,0.35f,0.0f,0.0f,0.41f,0.0f,0.8f,0.0f,0.0f,4.0f,0.03f,0.0f,0.15f,5.5f,0.0f,0.0f,0.0f,0.0f,0.008f,0.295f,0.59f,0.19f,0.008f,0.295f,0.59f,0.19f,1.0f,1.57f,0.0f,1.0f,0.0f,0.0f,1.0f,0.0f,0.0f,0.0f,0.0f,0.3f,0.35f,0.0f,0.0f,0.0f,1.0f,0.5f,1.0f,1.0f,1.0f,1.0f,1.0f,0.0f}},
};
}