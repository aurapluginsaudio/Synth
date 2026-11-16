// Copia o app web (index.html e ícones) da raiz do repositório para desktop/app antes de empacotar.
const fs = require('fs'), path = require('path');
const root = path.join(__dirname, '..', '..'), out = path.join(__dirname, '..', 'app');
fs.rmSync(out, { recursive: true, force: true }); fs.mkdirSync(out, { recursive: true });
for (const f of ['index.html', 'icon.svg', 'icon-192.png', 'icon-512.png', 'icon-180.png', 'manifest.json']) fs.copyFileSync(path.join(root, f), path.join(out, f));
// no app desktop não há service worker (o app já está instalado)
console.log('app preparado em', out);
