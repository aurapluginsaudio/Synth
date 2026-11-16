#pragma once
// Efeitos inspirados no JD-Xi: EFX1 (distorção / fuzz / bitcrusher) -> EFX2 (chorus / flanger / phaser / anel) -> reverb.
// Mesmas faixas e nomes do app web. C++ puro (sem JUCE), para poder ser testado com g++.
#include <vector>
#include <cmath>
#include <algorithm>
#include <cstdint>
namespace aura {
struct FxParams {
    int d = 0; float dr = 0.4f, dp = 0.6f, dl = 0.7f, cr = 0.4f, cb = 0.5f;                  // EFX1: 0 off, 1 dist, 2 fuzz, 3 crush
    int m = 0; float mr = 0.3f, md = 0.5f, mf = 0.2f, mn = 0.5f, mb = 0.5f, rf = 0.35f;       // EFX2: 0 off, 1 chorus, 2 flanger, 3 phaser, 4 anel
    int rv = 0, rt = 1; float rm = 0.5f, rh = 0.7f, rl = 0.3f;                                // reverb
};
class Fx {
public:
    void prepare(double sampleRate) {
        sr = sampleRate; dline.assign((size_t)(0.06 * sr) + 8, 0.f); wpos = 0; for (auto& a : ap) a = Bq{}; hpS = 0; hpPrev = 0; lfoPh = 0; carPh = 0; crPh = 0; crHold = 0; plS = 0; fb = 0;
        // Freeverb: tamanhos de linha para 44,1 kHz, escalados para a taxa atual
        static const int cT[8] = { 1116, 1188, 1277, 1356, 1422, 1491, 1557, 1617 }, aT[4] = { 556, 441, 341, 225 };
        for (int c = 0; c < 2; c++) {
            for (int i = 0; i < 8; i++) { cb_[c][i].buf.assign((size_t)((cT[i] + c * 23) * sr / 44100.0) + 1, 0.f); cb_[c][i].pos = 0; cb_[c][i].lp = 0; }
            for (int i = 0; i < 4; i++) { ab_[c][i].buf.assign((size_t)((aT[i] + c * 23) * sr / 44100.0) + 1, 0.f); ab_[c][i].pos = 0; }
        }
        rvHpS = 0; rvHpPrev = 0;
    }
    // entrada mono -> saída estéreo (outL/outR podem ser o mesmo ponteiro de entrada só se in != outL; aqui in é copiado antes)
    void process(const FxParams& q, const float* in, float* outL, float* outR, int n) {
        const double sr_ = sr;
        const float dg = 1.f + q.dr * 3.f; const float k = 1.f + q.dr * (q.d == 1 ? 18.f : 40.f);
        const double plA = 1.0 - std::exp(-6.283185307 * (1500.0 * std::pow(14000.0 / 1500.0, q.dp)) / sr_);
        const double crRate = std::pow(0.03, (double)q.cr); const float crQ = (float)std::pow(2.0, std::max(2, (int)std::lround(16 - q.cb * 13)) - 1);
        const bool ch = q.m == 1, fl = q.m == 2, ph = q.m == 3, rg = q.m == 4;
        const double lfoInc = 0.05 * std::pow(8.0 / 0.05, (double)q.mr) / sr_;
        const double base = ch ? 0.014 : 0.0005 * std::pow(0.009 / 0.0005, (double)q.mn), lfoDepth = ch ? q.md * 0.006 : q.md * base * 0.8;
        const float wetCF = (ch || fl) ? q.mb * 0.8f : 0.f, wetPh = ph ? q.mb * 0.7f : 0.f, wetR = rg ? q.mb : 0.f;
        const float dry2 = q.m == 0 ? 1.f : (rg ? 1.f - q.mb : (ph ? 1.f - q.mb * 0.35f : 1.f));
        const float fbk = fl ? std::min(0.88f, q.mf * 0.9f) : 0.f;
        const double hpA = std::exp(-6.283185307 * (ch ? 140.0 : 80.0) / sr_);
        const double pf = 150.0 * std::pow(1800.0 / 150.0, (double)q.mn), carInc = 20.0 * std::pow(100.0, (double)q.rf) / sr_, Qp = 0.5 + q.mf * 7.0;
        const double rvFc = q.rh >= 0.99f ? 20000.0 : 200.0 * std::pow(40.0, (double)q.rh);
        // reverb: tempo do tipo (s) -> realimentação dos combs
        static const double RT[6] = { 0.5, 0.9, 1.4, 2.0, 3.0, 4.2 };
        const double rt = RT[std::max(0, std::min(5, q.rt))] * (0.5 + q.rm * 1.1);
        const double damp = 1.0 - std::exp(-6.283185307 * rvFc / sr_);
        const float rvGain = q.rv ? q.rl * 1.6f * 0.04f : 0.f;
        const double hp2 = std::exp(-6.283185307 * 150.0 / sr_);
        int sub = 0;
        for (int i = 0; i < n; i++) {
            float x = in[i];
            // ---- EFX1
            if (q.d == 1 || q.d == 2) {
                float y = x * dg; float z;
                if (q.d == 1) z = std::tanh(k * y) / std::tanh(k); else z = (std::tanh(k * y + 0.6f) - std::tanh(0.6f)) * 0.6f;
                plS += (float)plA * (z - plS); x = plS * q.dl * (q.d == 2 ? 0.7f : 0.9f);
            } else if (q.d == 3) {
                crPh += crRate; if (crPh >= 1) { crPh -= 1; crHold = std::round(x * crQ) / crQ; } x = crHold * q.dl;
            }
            // ---- EFX2
            float y2 = x * dry2;
            if (q.m) {
                lfoPh += lfoInc; if (lfoPh >= 1) lfoPh -= 1; const double lf = std::sin(6.283185307 * lfoPh);
                if (ch || fl) {
                    float hpo = (float)(hpA * (hpPrevO + x - hpPrevI)); hpPrevI = x; hpPrevO = hpo;
                    double dly = std::max(0.0001, base + lfoDepth * lf) * sr_; double rp = (double)wpos - dly; while (rp < 0) rp += (double)dline.size();
                    size_t i0 = (size_t)rp, i1 = (i0 + 1) % dline.size(); float fr = (float)(rp - (double)i0), wv = dline[i0] * (1 - fr) + dline[i1] * fr;
                    dline[wpos] = hpo + wv * fbk; wpos = (wpos + 1) % dline.size(); y2 += wv * wetCF;
                } else if (ph) {
                    if ((sub++ & 15) == 0) { const double f = std::min(0.45 * sr_, pf * std::pow(2.0, lf * q.md * 2.0)); for (auto& a : ap) a.set(f, Qp, sr_); }
                    float v = x; for (auto& a : ap) v = a.run(v); y2 += v * wetPh;
                } else if (rg) {
                    carPh += carInc; if (carPh >= 1) carPh -= 1; y2 += x * (float)std::sin(6.283185307 * carPh) * wetR;
                }
            }
            outL[i] = outR[i] = y2;
            // ---- reverb (paralelo)
            if (q.rv) {
                float r = (float)(hp2 * (rvHpPrev + y2 - rvHpIn)); rvHpIn = y2; rvHpPrev = r;
                float inp = r * 0.015f * 4.f;   // normalização da entrada dos combs
                for (int c = 0; c < 2; c++) {
                    float acc = 0;
                    for (int t = 0; t < 8; t++) { auto& cb = cb_[c][t]; float o = cb.buf[cb.pos]; cb.lp += (float)damp * (o - cb.lp);
                        const double len = (double)cb.buf.size() / sr_; const float fbf = (float)std::pow(10.0, -3.0 * len / rt);
                        cb.buf[cb.pos] = inp + cb.lp * fbf; if (++cb.pos >= cb.buf.size()) cb.pos = 0; acc += o; }
                    for (int t = 0; t < 4; t++) { auto& a = ab_[c][t]; float b = a.buf[a.pos]; float o = -acc + b; a.buf[a.pos] = acc + b * 0.5f; if (++a.pos >= a.buf.size()) a.pos = 0; acc = o; }
                    (c ? outR : outL)[i] += acc * rvGain * 8.f;
                }
            }
        }
    }
private:
    struct Bq { double b0 = 1, b1 = 0, b2 = 0, a1 = 0, a2 = 0, z1 = 0, z2 = 0;
        void set(double f, double Q, double sr) { double w = 6.283185307 * f / sr, al = std::sin(w) / (2 * Q), c = std::cos(w), a0 = 1 + al; b0 = (1 - al) / a0; b1 = -2 * c / a0; b2 = (1 + al) / a0; a1 = -2 * c / a0; a2 = (1 - al) / a0; }
        float run(float x) { double y = b0 * x + z1; z1 = b1 * x - a1 * y + z2; z2 = b2 * x - a2 * y; return (float)y; } };
    struct Comb { std::vector<float> buf; size_t pos = 0; float lp = 0; };
    struct Allp { std::vector<float> buf; size_t pos = 0; };
    double sr = 44100; std::vector<float> dline; size_t wpos = 0; Bq ap[4];
    double hpS = 0, hpPrev = 0, hpPrevI = 0, hpPrevO = 0, lfoPh = 0, carPh = 0, crPh = 0, rvHpPrev = 0, rvHpIn = 0, rvHpS = 0; float crHold = 0, plS = 0, fb = 0;
    Comb cb_[2][8]; Allp ab_[2][4];
};
}
