import http from 'node:http';
import fs from 'node:fs';
const files = new Set(['index.html', 'app.mjs', 'data.mjs', 'filter.mjs', 'style.css']);
http.createServer((req, res) => {
  const name = new URL(req.url, 'http://localhost').pathname.slice(1) || 'index.html';
  if (!files.has(name)) { res.writeHead(404); res.end(); return; }
  res.setHeader('Content-Type', name.endsWith('.mjs') ? 'text/javascript' : name.endsWith('.css') ? 'text/css' : 'text/html');
  res.end(fs.readFileSync(new URL(name, import.meta.url)));
}).listen(Number(process.env.PORT || 4322), '127.0.0.1');
