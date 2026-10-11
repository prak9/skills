// Runs the actual service-worker functions with local Chrome API doubles.
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const path = require('node:path');
const source = fs.readFileSync(path.join(__dirname, '../runtime/extension/background.js'), 'utf8');
let navigations = [];
let finalUrl = 'https://www.xiaohongshu.com/404';
const chrome = {
  alarms: {create() {}, onAlarm: {addListener() {}}},
  runtime: {onMessage: {addListener() {}}, sendMessage: async () => ({})},
  storage: {session: {set() {}}},
  tabs: {query: async () => [{id: 1}], update: async (id, info) => navigations.push(info.url),
    get: async () => ({url: finalUrl}), onUpdated: {addListener() {}, removeListener() {}}},
  scripting: {executeScript: async () => [{result: ''}]},
};
const context = vm.createContext({chrome, URL, WebSocket: class {}, console, setTimeout});
vm.runInContext(source, context);
vm.runInContext('waitForTabComplete = async () => {}', context);

(async () => {
  for (const url of ['https://example.com', 'https://xiaohongshu.com.evil.test',
    'http://www.xiaohongshu.com', 'https://user@www.xiaohongshu.com']) {
    assert.throws(() => context.validateXhsUrl(url));
  }
  await assert.rejects(context.cmdNavigate({url: 'https://www.xiaohongshu.com/explore/test'}));
  assert.equal(navigations.length, 1); // No search/home/token retry after /404.
  await assert.rejects(context.handleCommand({method: 'get_cookies'}));
  await assert.rejects(context.handleCommand({method: 'get_netlog'}));
  finalUrl = 'https://www.xiaohongshu.com/explore/test';
  await context.cmdNavigate({url: finalUrl});
  assert.equal(navigations.length, 2);
  chrome.tabs.query = async () => [{id: 1}, {id: 2}];
  await assert.rejects(context.getOrOpenXhsTab());
  console.log('Extension behavior checks passed (URL scope, blocked-page stop, no credential/log export).');
})().catch(error => { console.error(error); process.exitCode = 1; });
