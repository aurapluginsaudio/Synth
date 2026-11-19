// Gera vst/Source/Presets.h a partir dos presets de fábrica do index.html.
// O app web é a fonte: mexeu num preset lá, rode este script e o plugin acompanha.
//   node vst/gerar-presets.js
const fs = require('fs');
const path = require('path');
const raiz = path.join(__dirname, '..');
const html = fs.readFileSync(path.join(raiz, 'index.html'), 'utf8');

// Pega do próprio index.html os pedaços de que precisamos, sem rodar a página inteira
function trecho(marca, fim) {
  const i = html.indexOf(marca);
  if (i < 0) throw new Error('não achei ' + marca);
  const j = html.indexOf(fim, i);
  return html.slice(i, j + fim.length);
}
const defs = [
  trecho('const DEF = {', '};'),
  trecho('const LIM = {', '};'),
  trecho('const LIMI = {', '};'),
  trecho('const WAVES=', '];'),
  trecho('const ENUM = {', '};'),
  trecho('const FXD={', '};'),
  'const PKEYS = Object.keys(DEF);',
].join('\n');
const fnNorm = trecho('function norm(p){', '\n  }');
const fabrica = trecho('const FACTORY = [', '\n  ];');

const ctx = {};
new Function('C', defs + '\n' + fnNorm + '\n' + 'const F = p => Object.assign(norm(p), {factory:true});\n' + fabrica +
  '\nC.PKEYS = PKEYS; C.FACTORY = FACTORY; C.FXD = FXD;')(ctx);

// A ordem das ondas no plugin é outra: lá a lista começa na triangular
const ORDEM_ONDA = { triangle: 0, sawtooth: 1, square: 2, rsaw: 3, tsaw: 4 };
const ORDEM_LFO = { triangle: 0, square: 1 };
const FX_IDS = ['d', 'm', 'rv', 'rt', 'dr', 'dp', 'dl', 'cr', 'cb', 'mr', 'md', 'mf', 'mn', 'mb', 'rf', 'rm', 'rh', 'rl'];

const num = (k, v) => {
  if (k === 'wave' || k === 'w2' || k === 'w3') return ORDEM_ONDA[v];
  if (k === 'lwv') return ORDEM_LFO[v];
  return +v;
};
const f = v => (Number.isInteger(v) ? v.toFixed(1) : String(+v.toFixed(6))) + 'f';

// Arpejador que viaja com o preset: on, padrão, divisão, oitavas, duração, swing, andamento
const ARP_PADRAO = { pat: 0, div: 1, oct: 1, gate: 0.6, sw: 0, bpm: 100 };
const linhas = ctx.FACTORY.map(p => {
  const vals = ctx.PKEYS.map(k => f(num(k, p[k]))).join(',');
  const fx = p.efx ? FX_IDS.map(k => f(k in p.efx ? +p.efx[k] : ctx.FXD[k])).join(',') : '';
  const A = p.arp ? Object.assign({}, ARP_PADRAO, p.arp) : null;
  const arp = A ? [A.on === 0 ? 0 : 1, A.pat, A.div, A.oct, A.gate, A.sw, A.bpm].map(x => f(+x)).join(',') : '';
  return `{"${p.name}",{${vals}},${p.efx ? 'true' : 'false'},{${fx}},${A ? 'true' : 'false'},{${arp}}}`;
});

const saida = `// Gerado por vst/gerar-presets.js a partir dos presets de fábrica do index.html.
// NÃO edite à mão: mexa no index.html e rode o script de novo.
// Autor: Thiago R. Galvão (AURA-SB-TRG-2026)
#pragma once
namespace aura {
static const int kNumParams = ${ctx.PKEYS.length};
static const char* const kParamIds[kNumParams] = {${ctx.PKEYS.map(k => `"${k}"`).join(',')}};
// Alguns presets trazem os próprios efeitos. Os que não trazem deixam
// temFx em false e os efeitos continuam como o usuário deixou.
static const int kNumFx = 18;
static const char* const kFxIds[kNumFx] = {${FX_IDS.map(k => `"fx${k}"`).join(',')}};
// Sub Arp e Sub Agro Arp ligam o arpejador; ao trocar para um preset sem arpejo, o plugin desliga o que o preset ligou.
static const int kNumArp = 7;
static const char* const kArpIds[kNumArp] = {"arpon","arppat","arpdiv","arpoct","arpgate","arpsw","arpbpm"};
struct FactoryPreset { const char* name; float v[kNumParams]; bool temFx; float fx[kNumFx]; bool temArp; float arp[kNumArp]; };
static const int kNumFactory = ${linhas.length};
static const FactoryPreset kFactory[kNumFactory] = {
${linhas.join(',\n')}
};
}
`;
fs.writeFileSync(path.join(__dirname, 'Source', 'Presets.h'), saida);
console.log(`Presets.h: ${linhas.length} presets, ${ctx.PKEYS.length} parâmetros`);
