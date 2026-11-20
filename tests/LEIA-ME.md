# Testes do AURA

Requisitos: Python com Playwright (Chromium) e um servidor local na raiz do repositório (`python3 -m http.server 8765`).

- `calibra_presets.py SAIDA.json`: toca os 111 presets e grava pico e RMS de cada um (versão web).
- `motor_cpp_presets.cpp`: faz a mesma medição no motor C++ do plugin
  (`g++ -O2 -std=c++17 -Ivst/Source tests/motor_cpp_presets.cpp -o t && ./t cpp.json`). Compare os dois JSON: a diferença média deve ficar perto de 0 dB.
- `ux_setlist_categorias.py`, `feat_test.py`, `arp_test.py`, `prio_test.py`, `imp_test.py`, `final_test.py`: testes funcionais da interface.

## Paridade web e plugin
O motor existe em dois lugares: `index.html` (AudioWorklet `AuraVoice`/`AuraComp`) e `vst/Source/AuraEngine.h`. Qualquer mudança de som precisa ser feita nos dois e conferida com a comparação acima.

## Rodar tudo antes de publicar
`tests/rodar_tudo.sh` executa os testes do motor (Node e C++) e da interface (Playwright) e mostra um resumo. `tests/ao_vivo.py` cobre o botão de pânico, o preset de emergência, o modo leve e a linha de efeitos do painel.


## Novidades (presets, exportação, plugin)
- `tests/novidades.py`: exportação .syx/.mdp (ida e volta e bloqueio no teste e na demonstração), arpejo ligado pelo preset, aviso de som bloqueado e lista de presets por família com busca.
- `tests/plugin_presets.js`: Presets.h tem de ser igual ao gerado a partir do index.html, com os mesmos 33 nomes na mesma ordem, e o plugin tem de aplicar e desligar o arpejo do preset.
- `tests/motor_cpp_presets_arp.cpp`: os 33 presets tocam no motor do plugin (sem mudo, sem NaN) e o arpejador do plugin toca no andamento do Sub Arp e do Sub Agro Arp.
- `.github/workflows/testes-plugin.yml` roda o Node e o C++ a cada push.

- `orientacao.py` — celular e tablet em pé mostram o aviso "Gire o aparelho"; deitados e no computador funcionam; teclas com nome; ids únicos; registro de erros.
- `../tools/versionar_sw.py` — carimba o cache do service worker com o conteúdo dos arquivos (o `rodar_tudo.sh` roda sozinho; o CI usa `--check`).
