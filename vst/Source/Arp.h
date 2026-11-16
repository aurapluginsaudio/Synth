// Arpejador do AURA (porte da versão web). (c) 2026 Thiago R. Galvão
#pragma once
#include <vector>
#include <algorithm>
#include <cmath>
#include <cstdlib>

namespace aura {
struct Arp {
    bool on = false, latch = false;
    int pat = 0, div = 1, oct = 1;      // pat: 0 sobe, 1 desce, 2 sobe e desce, 3 aleatório, 4 ordem
    double gate = 0.6, bpm = 100, swing = 0; int sc = 0;
    std::vector<int> notes, down;
    int k = 0, cur = -1, vel = 100;
    double toNext = 0, toOff = 0; bool running = false, offArmed = false;
    static constexpr double DIV[4] = { 1, 0.5, 1.0 / 3.0, 0.25 };

    std::vector<int> seq() const {
        std::vector<int> b = notes; if (pat != 4) std::sort(b.begin(), b.end());
        std::vector<int> o; for (int i = 0; i < oct; i++) for (int n : b) o.push_back(n + 12 * i);
        return o;
    }
    int idx(int L) {
        int kk = k++;
        if (L < 2) return 0;
        if (pat == 3) return std::rand() % L;
        if (pat == 1) return L - 1 - (kk % L);
        if (pat == 2) { int c = 2 * L - 2, j = kk % c; return j < L ? j : c - j; }
        return kk % L;
    }
    void press(int n, int v) {
        if (latch && down.empty()) notes.clear();
        if (std::find(down.begin(), down.end(), n) == down.end()) down.push_back(n);
        if (std::find(notes.begin(), notes.end(), n) == notes.end()) notes.push_back(n);
        vel = v; if (!running) { running = true; k = 0; sc = 0; toNext = 0; }
    }
    template <class Off> void release(int n, Off&& off) {
        down.erase(std::remove(down.begin(), down.end(), n), down.end());
        if (latch) return;
        notes.erase(std::remove(notes.begin(), notes.end(), n), notes.end());
        if (notes.empty()) silence(off);
    }
    template <class Off> void silence(Off&& off) { running = false; offArmed = false; toOff = 0; if (cur >= 0) { int c = cur; cur = -1; off(c); } }
    void clear() { notes.clear(); down.clear(); k = 0; cur = -1; running = false; offArmed = false; toNext = toOff = 0; }
    // amostras até o próximo evento (para dividir o bloco)
    double samplesToEvent() const {
        if (!running) return 1e18;
        double a = toNext; if (cur >= 0 && offArmed) a = std::min(a, toOff);
        return std::max(a, 0.0);
    }
    template <class On, class Off> void advance(double n, double sr, On&& onF, Off&& offF) {
        if (!running) return;
        toNext -= n; if (cur >= 0 && offArmed) toOff -= n;
        if (cur >= 0 && offArmed && toOff <= 1e-9) { int c = cur; cur = -1; offArmed = false; offF(c); }
        if (toNext <= 1e-9) {
            if (notes.empty()) { silence(offF); return; }
            auto sq = seq(); int nn = sq[idx((int)sq.size())]; double step = 60.0 / std::max(bpm, 1.0) * DIV[div] * sr * (1.0 + ((sc++ % 2 == 0) ? 1 : -1) * swing * 0.33);
            if (cur >= 0) { int c = cur; cur = -1; offF(c); }
            onF(nn, vel); cur = nn; offArmed = true; toOff = std::max(1.0, step * gate); toNext += step;
        }
    }
};
}
