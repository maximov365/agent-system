import net from 'node:net';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
import {run} from '../../tools/visual/run.mjs';

export async function grade(project, output) {
  const socket = net.createServer();
  await new Promise(resolve => socket.listen(0, '127.0.0.1', resolve));
  const port = socket.address().port;
  await new Promise(resolve => socket.close(resolve));
  return run({schema_version: 1, baseURL: `http://127.0.0.1:${port}`,
    server: {command: [process.execPath, 'server.mjs'], env: {PORT: String(port)}},
    locale: 'en-US', reducedMotion: 'reduce',
    viewports: [{name: 'desktop', width: 1440, height: 900},
      {name: 'mobile', width: 390, height: 844, mobile: true}],
    journeys: [{id: 'library', steps: [
      {type: 'expectCount', selector: '#results li', count: 3},
      {type: 'expectText', selector: '#results', contains: 'Paper & <ink>'},
      {type: 'capture', name: 'initial'},
      {type: 'fill', selector: '#query', value: ' MARKET '},
      {type: 'expectCount', selector: '#results li', count: 1},
      {type: 'expectText', selector: '#count', contains: '1'},
      {type: 'fill', selector: '#query', value: 'КАРТА'},
      {type: 'press', selector: '#query', key: 'Enter'},
      {type: 'expectCount', selector: '#results li', count: 1},
      {type: 'expectText', selector: '#results', contains: 'Карта маршрутов'},
      {type: 'capture', name: 'filtered'},
      {type: 'fill', selector: '#query', value: 'not in library'},
      {type: 'expectCount', selector: '#results li', count: 0},
      {type: 'waitFor', selector: '#empty'},
      {type: 'capture', name: 'empty'},
      {type: 'click', selector: '#clear'},
      {type: 'expectCount', selector: '#results li', count: 3},
      {type: 'expectCount', selector: '#empty:visible', count: 0},
      {type: 'press', selector: ':focus', key: 'm'},
      {type: 'expectCount', selector: '#results li', count: 1},
      {type: 'expectText', selector: '#results', contains: 'Market notes'},
      {type: 'capture', name: 'keyboard'}
    ]}]}, {project, output});
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const report = await grade(path.resolve(process.argv[2]), path.resolve(process.argv[3]));
  console.log(JSON.stringify({checks_passed: report.checks_passed, visual_review: report.visual_review}));
  process.exitCode = report.checks_passed ? 0 : 1;
}
