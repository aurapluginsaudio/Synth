#!/usr/bin/env python3
"""Carimba o nome do cache do service worker (sw.js) com um resumo do conteúdo dos arquivos guardados.
Uso:  python3 tools/versionar_sw.py          -> atualiza o sw.js
      python3 tools/versionar_sw.py --check  -> só confere (sai com erro se o sw.js estiver velho; usado no CI)
Assim ninguém precisa lembrar de trocar 'aura-vNN' à mão: mudou o app, o nome do cache muda junto."""
import hashlib, os, re, sys
raiz = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')
sw = os.path.join(raiz, 'sw.js')
txt = open(sw, encoding='utf-8').read()
m = re.search(r"const CACHE='[^']*', FILES=\[([^\]]*)\]", txt)
if not m: sys.exit('sw.js: linha CACHE/FILES não encontrada')
arquivos = [a.strip().strip("'") for a in m.group(1).split(',')]
h = hashlib.sha256()
for a in arquivos:
    caminho = os.path.join(raiz, 'index.html' if a == './' else a)
    h.update(a.encode()); h.update(open(caminho, 'rb').read())
nome = 'aura-' + h.hexdigest()[:10]
novo = txt.replace(m.group(0), m.group(0).replace(re.search(r"CACHE='([^']*)'", m.group(0)).group(0), "CACHE='%s'" % nome), 1)
if '--check' in sys.argv:
    if novo != txt: sys.exit('sw.js desatualizado: rode  python3 tools/versionar_sw.py  e faça commit (esperado %s)' % nome)
    print('sw.js ok:', nome)
else:
    open(sw, 'w', encoding='utf-8').write(novo); print('sw.js ->', nome)
