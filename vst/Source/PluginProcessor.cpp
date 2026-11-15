// AURA Synth Bass (plugin) - Copyright (c) 2026 Thiago R. Galvão. Todos os direitos reservados. ID: AURA-SB-TRG-2026
#include "PluginProcessor.h"
#include "PluginEditor.h"
using namespace juce;
using aura::kDefs; using aura::Kind;

namespace {
// valores padrão (iguais ao DEF da versão web), para presets importados que não trazem todos os campos
const float kDefault[aura::NP] = {-1,2,0.5f,0.75f,1,0.5f,0,0,0,0,0,0,0,0.5f,0,0,0,0,4,0,0,0.15f,5.5f,0,0,0,0,0.002f,0.3f,0,0.2f,0.004f,0.3f,1,0.1f,1,1.3f,0,1,0,0,1,0,0,0,0,0.3f,0.35f,0};
int waveFromVar(const var& v, int d) {
    if (v.isString()) { auto s = v.toString(); if (s == "triangle") return 0; if (s == "sawtooth") return 1; if (s == "square") return 2; }
    return v.isVoid() ? d : (int)v;
}
}

AudioProcessorValueTreeState::ParameterLayout AuraProcessor::makeLayout() {
    AudioProcessorValueTreeState::ParameterLayout L;
    for (int i = 0; i < aura::NP; i++) {
        const aura::Def& d = kDefs[i]; ParameterID pid(d.id, 1);
        switch (d.k) {
        case aura::F: { NormalisableRange<float> r(d.mn, d.mx); r.skew = 1.0f / d.ex;
                  AudioParameterFloatAttributes at;
                  if (std::string(d.id) == "cut") at = at.withStringFromValueFunction([](float v, int) { return String((int)std::round(30 * std::pow(600.0, v))) + " Hz"; });
                  L.add(std::make_unique<AudioParameterFloat>(pid, d.name, r, aura::kFactory[0].v[i], at)); break; }
        case aura::I: L.add(std::make_unique<AudioParameterInt>(pid, d.name, (int)d.mn, (int)d.mx, (int)aura::kFactory[0].v[i])); break;
        case aura::B: L.add(std::make_unique<AudioParameterBool>(pid, d.name, aura::kFactory[0].v[i] > 0.5f)); break;
        case aura::W: L.add(std::make_unique<AudioParameterChoice>(pid, d.name, StringArray{ "Triangular", "Serra", "Quadrada" }, (int)aura::kFactory[0].v[i])); break;
        case aura::LW: L.add(std::make_unique<AudioParameterChoice>(pid, d.name, StringArray{ "Triangular", "Quadrada" }, (int)aura::kFactory[0].v[i])); break;
        }
    }
    L.add(std::make_unique<AudioParameterFloat>(ParameterID("velsens", 1), "Sensibilidade ao toque", NormalisableRange<float>(0, 1), 0.75f));
    L.add(std::make_unique<AudioParameterChoice>(ParameterID("veldest", 1), "Toque age em", StringArray{ "Volume e brilho", "So volume", "So brilho" }, 0));
    L.add(std::make_unique<AudioParameterChoice>(ParameterID("prio", 1), "Prioridade de nota", StringArray{ "Ultima nota", "Mais grave", "Mais aguda" }, 0));
    L.add(std::make_unique<AudioParameterChoice>(ParameterID("atdest", 1), "Pressao de canal", StringArray{ "Desligada", "Vibrato", "Filtro", "Volume" }, 0));
    L.add(std::make_unique<AudioParameterBool>(ParameterID("hold", 1), "Hold", false));
    L.add(std::make_unique<AudioParameterBool>(ParameterID("arpon", 1), "Arpejador", false));
    L.add(std::make_unique<AudioParameterChoice>(ParameterID("arppat", 1), "Arp Padrao", StringArray{ "Sobe", "Desce", "Sobe e desce", "Aleatorio", "Ordem" }, 0));
    L.add(std::make_unique<AudioParameterChoice>(ParameterID("arpdiv", 1), "Arp Divisao", StringArray{ "1/4", "1/8", "1/8T", "1/16" }, 1));
    L.add(std::make_unique<AudioParameterInt>(ParameterID("arpoct", 1), "Arp Oitavas", 1, 3, 1));
    L.add(std::make_unique<AudioParameterFloat>(ParameterID("arpgate", 1), "Arp Duracao", NormalisableRange<float>(0.1f, 0.95f), 0.6f));
    L.add(std::make_unique<AudioParameterBool>(ParameterID("arplatch", 1), "Arp Trava", false));
    L.add(std::make_unique<AudioParameterBool>(ParameterID("arpsync", 1), "Arp Tempo do host", true));
    L.add(std::make_unique<AudioParameterFloat>(ParameterID("arpbpm", 1), "Arp Andamento", NormalisableRange<float>(40, 240, 1), 100));
    return L;
}

AuraProcessor::AuraProcessor()
    : AudioProcessor(BusesProperties().withOutput("Output", AudioChannelSet::stereo(), true)),
      apvts(*this, nullptr, "AURA", makeLayout()) {
    for (int i = 0; i < aura::NP; i++) raw[i] = apvts.getRawParameterValue(kDefs[i].id);
    auto g = [this](const char* id) { return apvts.getRawParameterValue(id); };
    pVelSens = g("velsens"); pVelDest = g("veldest"); pPrio = g("prio"); pAtDest = g("atdest"); pHold = g("hold");
    pArpOn = g("arpon"); pArpPat = g("arppat"); pArpDiv = g("arpdiv"); pArpOct = g("arpoct"); pArpGate = g("arpgate"); pArpLatch = g("arplatch"); pArpSync = g("arpsync"); pArpBpm = g("arpbpm");
    engine.prepare(44100);
}

void AuraProcessor::prepareToPlay(double sr, int) {
    for (int i = 0; i < aura::NP; i++) engine.p[i] = raw[i]->load();
    engine.prepare(sr); arp.clear();
}

const String AuraProcessor::getProgramName(int i) {
    if (i >= 0 && i < aura::kNumFactory) return String(aura::kFactory[i].name);
    i -= aura::kNumFactory; if (i >= 0 && i < (int)user.size()) return user[(size_t)i].name + " (meu)";
    return {};
}

void AuraProcessor::applyValues(const float* v) {
    for (int i = 0; i < aura::NP; i++)
        if (auto* p = apvts.getParameter(kDefs[i].id)) { p->beginChangeGesture(); p->setValueNotifyingHost(p->convertTo0to1(v[i])); p->endChangeGesture(); }
}

void AuraProcessor::setCurrentProgram(int idx) {
    if (idx < 0 || idx >= getNumPrograms()) return;
    program = idx;
    if (idx < aura::kNumFactory) applyValues(aura::kFactory[idx].v); else applyValues(user[(size_t)(idx - aura::kNumFactory)].v);
}

void AuraProcessor::saveUserPreset(const String& nameIn) {
    String name = nameIn.trim().toUpperCase().substring(0, 18); if (name.isEmpty()) name = "SEM NOME";
    UserPreset u; u.name = name;
    for (int i = 0; i < aura::NP; i++) u.v[i] = raw[i]->load();
    int at = -1; for (size_t k = 0; k < user.size(); k++) if (user[k].name == name) at = (int)k;
    if (at >= 0) user[(size_t)at] = u; else { user.push_back(u); at = (int)user.size() - 1; }
    program = aura::kNumFactory + at;
    updateHostDisplay(); if (onPresetsChanged) onPresetsChanged();
}

int AuraProcessor::importJson(const File& f) {
    auto j = JSON::parse(f); auto* arr = j.getProperty("presets", var()).getArray(); int n = 0;
    if (!arr) return 0;
    for (auto& e : *arr) {
        if (!e.isObject() || !e.hasProperty("name")) continue;
        UserPreset u; u.name = e["name"].toString().trim().toUpperCase().substring(0, 18); if (u.name.isEmpty()) continue;
        for (int i = 0; i < aura::NP; i++) {
            const auto id = kDefs[i].id; float v = kDefault[i];
            if (e.hasProperty(id)) {
                if (kDefs[i].k == aura::W) v = (float)waveFromVar(e[id], (int)v);
                else if (kDefs[i].k == aura::LW) v = e[id].toString() == "square" ? 1.0f : 0.0f;
                else v = (float)(double)e[id];
            }
            v = jlimit(kDefs[i].mn, kDefs[i].mx, v); u.v[i] = v;
        }
        if (!e.hasProperty("fa")) { u.v[aura::fa] = u.v[aura::a]; u.v[aura::fd] = u.v[aura::d]; u.v[aura::fs] = u.v[aura::s]; u.v[aura::fr] = u.v[aura::r]; }
        int at = -1; for (size_t k = 0; k < user.size(); k++) if (user[k].name == u.name) at = (int)k;
        if (at >= 0) user[(size_t)at] = u; else user.push_back(u);
        n++;
    }
    if (n) { updateHostDisplay(); if (onPresetsChanged) onPresetsChanged(); }
    return n;
}

bool AuraProcessor::exportJson(const File& f) const {
    Array<var> list;
    static const char* wn[3] = { "triangle", "sawtooth", "square" };
    for (auto& u : user) {
        auto* o = new DynamicObject(); o->setProperty("name", u.name);
        for (int i = 0; i < aura::NP; i++) {
            const auto id = kDefs[i].id;
            if (kDefs[i].k == aura::W) o->setProperty(id, String(wn[jlimit(0, 2, (int)u.v[i])]));
            else if (kDefs[i].k == aura::LW) o->setProperty(id, String(u.v[i] > 0.5f ? "square" : "triangle"));
            else o->setProperty(id, (double)u.v[i]);
        }
        list.add(var(o));
    }
    auto* root = new DynamicObject(); root->setProperty("aura", 1); root->setProperty("origem", "AURA-SB-TRG-2026 (c) 2026 Thiago R. Galvao"); root->setProperty("presets", list);
    return f.replaceWithText(JSON::toString(var(root)));
}

void AuraProcessor::processBlock(AudioBuffer<float>& buf, MidiBuffer& midi) {
    ScopedNoDenormals nd;
    const int n = buf.getNumSamples(), nch = buf.getNumChannels();
    for (int i = 0; i < aura::NP; i++) engine.p[i] = raw[i]->load();
    engine.velSens = pVelSens->load(); engine.velDest = (int)pVelDest->load(); engine.prio = (int)pPrio->load(); engine.atDest = (int)pAtDest->load();
    if (nch < 1) return;
    // arpejador
    const bool arpOn = pArpOn->load() > 0.5f;
    arp.pat = (int)pArpPat->load(); arp.div = (int)pArpDiv->load(); arp.oct = (int)pArpOct->load(); arp.gate = pArpGate->load(); arp.latch = pArpLatch->load() > 0.5f;
    double bpm = pArpBpm->load();
    if (pArpSync->load() > 0.5f) if (auto* ph = getPlayHead()) if (auto pos = ph->getPosition()) if (auto b = pos->getBpm()) bpm = *b;
    arp.bpm = bpm;
    auto offF = [this](int note) { engine.realOff(note); };
    auto onF = [this](int note, int vel) { engine.coreOn(note, vel); };
    if (arpOn != lastArpOn) {
        lastArpOn = arpOn;
        if (arpOn) { arp.clear(); engine.allOff(); } else { arp.silence(offF); arp.clear(); engine.allOff(); }
    }
    engine.setSustain(pedal || pHold->load() > 0.5f);
    float* out = buf.getWritePointer(0);
    int pos = 0;
    const double sr = engine.sr;
    auto render = [&](int upto) {
        while (pos < upto) {
            int len = upto - pos;
            if (arpOn) { double e = arp.samplesToEvent(); if (e < len) len = std::max(1, (int)std::ceil(e)); }
            engine.process(out + pos, len); pos += len;
            if (arpOn) arp.advance(len, sr, onF, offF);
        }
    };
    for (const auto meta : midi) {
        const auto m = meta.getMessage();
        render(meta.samplePosition);
        if (m.isNoteOn()) { if (arpOn) arp.press(m.getNoteNumber(), m.getVelocity() ? m.getVelocity() : 100); else engine.noteOn(m.getNoteNumber(), m.getVelocity()); }
        else if (m.isNoteOff()) { if (arpOn) arp.release(m.getNoteNumber(), offF); else engine.noteOff(m.getNoteNumber()); }
        else if (m.isPitchWheel()) engine.bend = jlimit(-1.0f, 1.0f, (m.getPitchWheelValue() - 8192) / 8192.0f);
        else if (m.isChannelPressure()) engine.atVal = m.getChannelPressureValue() / 127.0f;
        else if (m.isController()) {
            const int c = m.getControllerNumber(), v = m.getControllerValue();
            if (c == 1) engine.mod = v / 127.0f;
            else if (c == 64) { pedal = v >= 64; engine.setSustain(pedal || pHold->load() > 0.5f); }
            else if (c == 123 || c == 120) { arp.silence(offF); arp.clear(); engine.allOff(); }
        } else if (m.isAllNotesOff() || m.isAllSoundOff()) { arp.silence(offF); arp.clear(); engine.allOff(); }
    }
    render(n);
    for (int c = 1; c < nch; c++) buf.copyFrom(c, 0, buf, 0, 0, n);
}

AudioProcessorEditor* AuraProcessor::createEditor() { return new AuraEditor(*this); }

void AuraProcessor::getStateInformation(MemoryBlock& dest) {
    auto st = apvts.copyState(); st.setProperty("program", program, nullptr);
    ValueTree us("USERPRESETS");
    for (auto& u : user) { ValueTree p("P"); p.setProperty("name", u.name, nullptr); String s; for (int i = 0; i < aura::NP; i++) s << u.v[i] << ","; p.setProperty("v", s, nullptr); us.appendChild(p, nullptr); }
    st.addChild(us, -1, nullptr);
    if (auto xml = st.createXml()) copyXmlToBinary(*xml, dest);
}
void AuraProcessor::setStateInformation(const void* data, int size) {
    if (auto xml = getXmlFromBinary(data, size)) {
        auto st = ValueTree::fromXml(*xml);
        if (!st.isValid()) return;
        user.clear();
        auto us = st.getChildWithName("USERPRESETS");
        for (auto p : us) { UserPreset u; u.name = p["name"].toString(); auto t = StringArray::fromTokens(p["v"].toString(), ",", ""); for (int i = 0; i < aura::NP; i++) u.v[i] = i < t.size() ? t[i].getFloatValue() : kDefault[i]; user.push_back(u); }
        if (us.isValid()) st.removeChild(us, nullptr);
        program = (int)st.getProperty("program", 0); st.removeProperty("program", nullptr);
        apvts.replaceState(st);
        if (onPresetsChanged) onPresetsChanged();
    }
}

AudioProcessor* JUCE_CALLTYPE createPluginFilter() { return new AuraProcessor(); }
