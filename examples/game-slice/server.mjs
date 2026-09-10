import http from 'node:http';
import fs from 'node:fs';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const root = path.dirname(fileURLToPath(import.meta.url));
const port = Number(process.env.PORT || 4321);
const types = {'.html': 'text/html', '.css': 'text/css', '.js': 'text/javascript', '.mjs': 'text/javascript', '.png': 'image/png', '.svg': 'image/svg+xml', '.wav': 'audio/wav', '.json': 'application/json'};
http.createServer((request, response) => {
  try {
    const route = decodeURIComponent(new URL(request.url, 'http://localhost').pathname);
    const file = path.resolve(root, '.' + (route === '/' ? '/index.html' : route));
    if (!file.startsWith(root + path.sep) || !['GET', 'HEAD'].includes(request.method)) {
      response.writeHead(403).end(); return;
    }
    if (!fs.existsSync(file) || !fs.statSync(file).isFile() || !types[path.extname(file)]) {
      response.writeHead(404).end('Not found'); return;
    }
    response.writeHead(200, {'Content-Type': types[path.extname(file)], 'Cache-Control': 'no-store'});
    if (request.method === 'HEAD') response.end(); else fs.createReadStream(file).pipe(response);
  } catch { response.writeHead(400).end('Bad request'); }
}).listen(port, '127.0.0.1', () => console.log(`Lantern Market: http://127.0.0.1:${port}`));
