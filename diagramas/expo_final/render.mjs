// Renderiza html/*.html a png/*.png (3840x2160). Uso: node render.mjs <ruta browser.mjs> [nombre...]
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
const aqui = path.dirname(fileURLToPath(import.meta.url));
const [lib, ...solo] = process.argv.slice(2);
const { launch, sleep, serveDir } = await import(lib);
const srv = await serveDir(aqui);
fs.mkdirSync(path.join(aqui, 'png'), { recursive: true });
const b = await launch({ width: 1920, height: 1080, scale: 2 });
for (const f of fs.readdirSync(path.join(aqui, 'html')).filter((f) => f.endsWith('.html')).sort()) {
  const n = f.replace('.html', '');
  if (solo.length && !solo.includes(n)) continue;
  await b.call('Page.navigate', { url: `${srv.base}/html/${f}` });
  await sleep(900);
  const { data } = await b.call('Page.captureScreenshot', { format: 'png' });
  fs.writeFileSync(path.join(aqui, 'png', `${n}.png`), Buffer.from(data, 'base64'));
  console.log('png', n);
}
srv.close();
process.exit(0);
