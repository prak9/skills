/**
 * XHS Bridge - Background Service Worker
 *
 * 连接 Python bridge server（ws://localhost:9333），接收命令并执行：
 * - navigate / wait_for_load: chrome.tabs.update + onUpdated
 * - evaluate / has_element 等: chrome.scripting.executeScript (MAIN world)
 * - click / input 等 DOM 操作: chrome.tabs.sendMessage → content.js
 * - screenshot: chrome.tabs.captureVisibleTab
 * - No credential export or raw network logging in this adaptation.
 */

// Local adaptation: no raw network/cookie logging or credential export.

const BRIDGE_URL = "ws://localhost:9333";
let ws = null;

// 保持 service worker 存活：有开放的 WebSocket 连接时 Chrome 不会终止 SW
// 额外加 alarm 作为保底
chrome.alarms.create("keepAlive", { periodInMinutes: 0.4 });
chrome.alarms.onAlarm.addListener(() => {
  if (!ws || ws.readyState !== WebSocket.OPEN) connect();
});

// ───────────────────────── WebSocket ─────────────────────────

function setStatus(connected) {
  chrome.storage.session.set({ wsConnected: connected });
}

function broadcastStatus() {
  const status = { wsConnected: ws !== null && ws.readyState === WebSocket.OPEN };
  chrome.runtime.sendMessage({ type: "STATUS_CHANGED", status }).catch(() => {});
}

chrome.runtime.onMessage.addListener((msg, _sender, sendResponse) => {
  if (msg.type === "GET_STATUS") {
    sendResponse({success: true, status: {wsConnected: ws !== null && ws.readyState === WebSocket.OPEN}});
  } else {
    sendResponse({error: "原始网络日志与主动风控探测在此版本中禁用"});
  }
  return false;
});

function connect() {
  if (ws && (ws.readyState === WebSocket.CONNECTING || ws.readyState === WebSocket.OPEN)) return;

  ws = new WebSocket(BRIDGE_URL);

  ws.onopen = () => {
    console.log("[XHS Bridge] 已连接到 bridge server");
    ws.send(JSON.stringify({ role: "extension" }));
    setStatus(true);
    broadcastStatus();
  };

  ws.onmessage = async (event) => {
    let msg;
    try {
      msg = JSON.parse(event.data);
    } catch {
      return;
    }
    try {
      const result = await handleCommand(msg);
      ws.send(JSON.stringify({ id: msg.id, result: result ?? null }));
    } catch (err) {
      ws.send(JSON.stringify({ id: msg.id, error: String(err.message || err) }));
    }
  };

  ws.onclose = () => {
    console.log("[XHS Bridge] 连接断开，3s 后重连...");
    setStatus(false);
    broadcastStatus();
    setTimeout(connect, 3000);
  };

  ws.onerror = (e) => {
    console.error("[XHS Bridge] WS 错误", e);
  };
}

// ───────────────────────── 命令路由 ─────────────────────────

async function handleCommand(msg) {
  const { method, params = {} } = msg;

  switch (method) {
    // ── 导航 ──
    case "navigate":
      return await cmdNavigate(params);

    case "wait_for_load":
      return await cmdWaitForLoad(params);

    // ── 截图 ──
    case "screenshot_element":
      return await cmdScreenshot(params);

    case "set_file_input":
      return await cmdSetFileInputViaDebugger(params);

    case "click_element":
    case "click_nth_element":
    case "click_element_by_text":
      return await cmdClickViaDebugger(method, params);

    case "press_key":
      return await cmdPressKeyViaDebugger(params);

    case "type_text":
      return await cmdTypeTextViaDebugger(params);

    // ── NetLog 风控数据 ──
    case "get_netlog":
    case "get_netlog_enabled":
    case "analyze_risk_control":
    case "get_404_diagnostics":
    case "clear_404_diagnostics":
    case "get_cookies":
      throw new Error("原始网络日志、主动探测与凭证导出已禁用");

    // ── 在页面主 world 执行 JS（可访问 window.__INITIAL_STATE__ 等） ──
    case "evaluate":
    case "wait_dom_stable":
    case "wait_for_selector":
    case "has_element":
    case "get_elements_count":
    case "get_element_text":
    case "get_element_attribute":
    case "get_scroll_top":
    case "get_viewport_height":
    case "get_url":
    case "get_elements_info":
    case "get_iframe_text":
      return await cmdEvaluateInMainWorld(method, params);

    // ── DOM 操作（在页面 MAIN world 执行，无需 content script 就绪） ──
    default:
      return await cmdDomInMainWorld(method, params);
  }
}

// ───────────────────────── 导航 ─────────────────────────

/**
 * 导航完成后立即在 MAIN world 检测页面是否为 404 / 风控拦截页。
 * 这是捕获导航级 404 的唯一可靠时机（fetch/XHR 拦截器看不到 browser navigation）。
 */
function validateXhsUrl(url) {
  const parsed = new URL(url);
  if (parsed.protocol !== "https:" || parsed.username || parsed.password ||
      (parsed.port && parsed.port !== "443") ||
      !["www.xiaohongshu.com", "xiaohongshu.com", "creator.xiaohongshu.com"].includes(parsed.hostname)) {
    throw new Error("只允许小红书页面的 HTTPS 导航");
  }
  return parsed;
}

async function cmdNavigate({ url }) {
  validateXhsUrl(url);
  const tab = await getOrOpenXhsTab();
  await chrome.tabs.update(tab.id, { url });
  await waitForTabComplete(tab.id, null, 60000);
  const finalTab = await chrome.tabs.get(tab.id);
  const finalUrl = validateXhsUrl(finalTab.url);
  if (finalUrl.pathname === "/404") {
    throw new Error("页面重定向至访问错误页；停止，不推断删除或自动换 token");
  }
  const results = await chrome.scripting.executeScript({
    target: {tabId: tab.id}, world: "MAIN",
    func: () => {
      const el = document.querySelector("#captcha-container,[class*='captcha'],.access-wrapper");
      return el && el.getBoundingClientRect().height > 0 ? (el.innerText || "需要验证") : "";
    },
  });
  if (results?.[0]?.result) {
    throw new Error("访问受限或需要验证；请用户在原浏览器处理后再明确重试");
  }
  return null;
}

async function cmdWaitForLoad({ timeout = 60000 }) {
  const tab = await getOrOpenXhsTab();
  await waitForTabComplete(tab.id, null, timeout);
  return null;
}

async function waitForTabComplete(tabId, expectedUrlPrefix, timeout) {
  return new Promise((resolve, reject) => {
    const deadline = Date.now() + timeout;

    function listener(id, info, updatedTab) {
      if (id !== tabId) return;
      if (info.status !== "complete") return;
      if (expectedUrlPrefix && !updatedTab.url?.startsWith(expectedUrlPrefix.slice(0, 20))) return;
      chrome.tabs.onUpdated.removeListener(listener);
      resolve();
    }

    chrome.tabs.onUpdated.addListener(listener);

    // 轮询兜底：若事件在监听前已触发
    const poll = async () => {
      if (Date.now() > deadline) {
        chrome.tabs.onUpdated.removeListener(listener);
        reject(new Error("页面加载超时"));
        return;
      }
      const tab = await chrome.tabs.get(tabId).catch(() => null);
      if (tab && tab.status === "complete") {
        chrome.tabs.onUpdated.removeListener(listener);
        resolve();
        return;
      }
      setTimeout(poll, 400);
    };
    setTimeout(poll, 600);
  });
}

// ───────────────────────── 截图 ─────────────────────────

async function cmdScreenshot() {
  const tab = await getOrOpenXhsTab();
  const dataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, { format: "png" });
  return { data: dataUrl.split(",")[1] };
}

// ───────────────────────── Cookies ─────────────────────────


// ───────────────────────── MAIN world JS 执行 ─────────────────────────

async function cmdEvaluateInMainWorld(method, params) {
  const tab = await getOrOpenXhsTab();
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: mainWorldExecutor,
    args: [method, params],
  });
  const r = results?.[0]?.result;
  if (r && typeof r === "object" && "__xhs_error" in r) {
    throw new Error(r.__xhs_error);
  }
  return r;
}

/**
 * 在页面主 world 运行，可访问 window.__INITIAL_STATE__ 等页面全局变量。
 * 注意：此函数被序列化后注入页面，不能引用外部变量。
 */
function mainWorldExecutor(method, params) {
  function poll(check, interval, timeout) {
    return new Promise((resolve, reject) => {
      const start = Date.now();
      (function tick() {
        const result = check();
        if (result !== false && result !== null && result !== undefined) {
          resolve(result);
          return;
        }
        if (Date.now() - start >= timeout) {
          reject(new Error("超时"));
          return;
        }
        setTimeout(tick, interval);
      })();
    });
  }

  switch (method) {
    case "evaluate": {
      try {
        // eslint-disable-next-line no-new-func
        return Function(`"use strict"; return (${params.expression})`)();
      } catch (e) {
        return { __xhs_error: `JS执行错误: ${e.message}` };
      }
    }

    case "has_element":
      return document.querySelector(params.selector) !== null;

    case "get_elements_count":
      return document.querySelectorAll(params.selector).length;

    case "get_element_text": {
      const el = document.querySelector(params.selector);
      return el ? el.textContent.trim() : null;
    }

    case "get_elements_info": {
      return Array.from(document.querySelectorAll(params.selector)).map(el => {
        const info = { text: el.textContent.trim() };
        if (params.attrs) for (const a of params.attrs) info[a] = el.getAttribute(a);
        return info;
      });
    }

    case "get_element_attribute": {
      const el = document.querySelector(params.selector);
      return el ? el.getAttribute(params.attr) : null;
    }

    case "get_scroll_top":
      return window.pageYOffset || document.documentElement.scrollTop || 0;

    case "get_viewport_height":
      return window.innerHeight;

    case "get_url":
      return window.location.href;

    case "wait_dom_stable": {
      const timeout = params.timeout || 10000;
      const interval = params.interval || 500;
      return new Promise((resolve) => {
        let last = -1;
        const start = Date.now();
        (function tick() {
          const size = document.body ? document.body.innerHTML.length : 0;
          if (size === last && size > 0) { resolve(null); return; }
          last = size;
          if (Date.now() - start >= timeout) { resolve(null); return; }
          setTimeout(tick, interval);
        })();
      });
    }

    case "wait_for_selector": {
      const timeout = params.timeout || 30000;
      return poll(
        () => document.querySelector(params.selector) ? true : false,
        200,
        timeout,
      ).catch(() => { throw new Error(`等待元素超时: ${params.selector}`); });
    }

    case "get_iframe_text": {
      return new Promise(resolve => {
        const iframe = document.querySelector(params.iframe_selector);
        if (!iframe) { resolve(null); return; }
        function tryRead() {
          try {
            const doc = iframe.contentDocument || iframe.contentWindow?.document;
            if (!doc || doc.readyState !== "complete") return false;
            const spans = doc.querySelectorAll(params.text_selector || ".textLayer span");
            if (spans.length === 0) return false;
            return Array.from(spans).map(s => s.textContent).join(" ");
          } catch (e) {
            return { __xhs_error: `iframe 访问失败: ${e.message}` };
          }
        }
        const timeout = params.timeout || 15000;
        const start = Date.now();
        (function tick() {
          const result = tryRead();
          if (result && result !== false) { resolve(result); return; }
          if (result?.__xhs_error) { resolve(result); return; }
          if (Date.now() - start >= timeout) { resolve(null); return; }
          setTimeout(tick, 300);
        })();
      });
    }

    default:
      return { __xhs_error: `未知 MAIN world 方法: ${method}` };
  }
}

// ───────────────────────── 工具函数 ──────────────────────────────────

function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

// ───────────────────────── 真实鼠标点击（chrome.debugger + CDP） ──────

// 在视口绝对坐标 (x, y) 派发真实鼠标事件序列：mouseMoved（轨迹）+ mousePressed + mouseReleased。
// 真事件走渲染层，能穿透 closed shadow DOM；JS 合成事件做不到。
async function _dispatchRealClickAt(target, x, y) {
  const startX = x - 20;
  const startY = y - 45;
  const steps = 5;
  for (let i = 1; i <= steps; i++) {
    const t = i / steps;
    await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", {
      type: "mouseMoved",
      x: Math.round(startX + (x - startX) * t),
      y: Math.round(startY + (y - startY) * t),
      button: "none", buttons: 0, modifiers: 0,
    });
    await sleep(8);
  }

  const base = { x, y, button: "left", buttons: 1, clickCount: 1, modifiers: 0 };
  await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", { ...base, type: "mousePressed" });
  await sleep(30);
  await chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", { ...base, type: "mouseReleased", buttons: 0 });
}

async function cmdClickViaDebugger(method, { selector, index, text }) {
  const tab = await getOrOpenXhsTab();
  const target = { tabId: tab.id };

  // 按调用方式构造元素查找表达式
  let findExpr;
  if (method === "click_nth_element") {
    findExpr = `document.querySelectorAll(${JSON.stringify(selector)})[${index}] || null`;
  } else if (method === "click_element_by_text") {
    findExpr = `Array.from(document.querySelectorAll(${JSON.stringify(selector)})).find(e => e.textContent.includes(${JSON.stringify(text)})) || null`;
  } else {
    findExpr = `document.querySelector(${JSON.stringify(selector)})`;
  }

  // 防御性 detach：清掉残留 attach 状态
  await chrome.debugger.detach(target).catch(() => {});
  await chrome.debugger.attach(target, "1.3");
  try {
    // 先滚动元素到视口中心，再取坐标
    const evalResult = await chrome.debugger.sendCommand(target, "Runtime.evaluate", {
      expression: `(() => {
        const el = ${findExpr};
        if (!el) return null;
        el.scrollIntoView({ block: "center", behavior: "instant" });
        const r = el.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      })()`,
      returnByValue: true,
    });

    const pos = evalResult?.result?.value;
    if (!pos) throw new Error(`元素不存在: ${JSON.stringify({ selector, index, text })}`);

    await _dispatchRealClickAt(target, pos.x, pos.y);
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
  return null;
}

// ─────── 真实键盘（chrome.debugger + CDP Input.dispatchKeyEvent） ──────

async function cmdPressKeyViaDebugger({ key }) {
  const tab = await getOrOpenXhsTab();

  // 检查当前焦点是否在 contenteditable
  const ceResult = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: () => document.activeElement?.isContentEditable ?? false,
  });
  const inCE = ceResult?.[0]?.result;

  if (inCE) {
    // contenteditable: execCommand 产生 isTrusted input 事件
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      world: "MAIN",
      func: (k) => {
        if (k === "Enter") {
          document.execCommand("insertParagraph", false, null);
        } else if (k === "ArrowDown") {
          const active = document.activeElement;
          const sel = window.getSelection();
          if (sel && active.childNodes.length) {
            sel.selectAllChildren(active);
            sel.collapseToEnd();
          }
        } else if (k === "Backspace") {
          document.execCommand("delete", false, null);
        }
      },
      args: [key],
    });
    return null;
  }

  // 非 contenteditable: debugger Input.dispatchKeyEvent（isTrusted: true）
  const KEY_MAP = {
    Enter:      { key: "Enter",      code: "Enter",      windowsVirtualKeyCode: 13 },
    Tab:        { key: "Tab",        code: "Tab",        windowsVirtualKeyCode: 9  },
    Backspace:  { key: "Backspace",  code: "Backspace",  windowsVirtualKeyCode: 8  },
    Delete:     { key: "Delete",     code: "Delete",     windowsVirtualKeyCode: 46 },
    Escape:     { key: "Escape",     code: "Escape",     windowsVirtualKeyCode: 27 },
    ArrowDown:  { key: "ArrowDown",  code: "ArrowDown",  windowsVirtualKeyCode: 40 },
    ArrowUp:    { key: "ArrowUp",    code: "ArrowUp",    windowsVirtualKeyCode: 38 },
    ArrowLeft:  { key: "ArrowLeft",  code: "ArrowLeft",  windowsVirtualKeyCode: 37 },
    ArrowRight: { key: "ArrowRight", code: "ArrowRight", windowsVirtualKeyCode: 39 },
    Space:      { key: " ",          code: "Space",      windowsVirtualKeyCode: 32 },
  };
  const info = KEY_MAP[key] || { key, code: `Key${key.toUpperCase()}`, windowsVirtualKeyCode: key.charCodeAt(0) };

  const target = { tabId: tab.id };
  await chrome.debugger.attach(target, "1.3");
  try {
    const base = { modifiers: 0, ...info };
    await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", { ...base, type: "keyDown" });
    await sleep(30);
    await chrome.debugger.sendCommand(target, "Input.dispatchKeyEvent", { ...base, type: "keyUp" });
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
  return null;
}

// ─────── 真实文字输入（chrome.debugger + CDP Input.insertText） ──────

async function cmdTypeTextViaDebugger({ text, delayMs = 50 }) {
  const tab = await getOrOpenXhsTab();

  // 检查当前焦点是否在 contenteditable
  const ceResult = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: () => document.activeElement?.isContentEditable ?? false,
  });
  const inCE = ceResult?.[0]?.result;

  if (inCE) {
    // contenteditable: 逐字 execCommand("insertText")，单次 executeScript 避免 IPC 开销
    await chrome.scripting.executeScript({
      target: { tabId: tab.id },
      world: "MAIN",
      func: async (chars, delay) => {
        function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }
        for (const char of chars) {
          document.execCommand("insertText", false, char);
          await sleep(delay);
        }
      },
      args: [[...text], delayMs],
    });
    return null;
  }

  // 非 contenteditable: 逐字 Input.insertText（isTrusted: true）
  const target = { tabId: tab.id };
  await chrome.debugger.attach(target, "1.3");
  try {
    for (const char of text) {
      await chrome.debugger.sendCommand(target, "Input.insertText", { text: char });
      await sleep(delayMs);
    }
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
  return null;
}

// ───────────────────────── 文件上传（chrome.debugger + CDP） ─────────

async function cmdSetFileInputViaDebugger({ selector, files }) {
  const tab = await getOrOpenXhsTab();
  const target = { tabId: tab.id };

  await chrome.debugger.attach(target, "1.3");
  try {
    const { root } = await chrome.debugger.sendCommand(target, "DOM.getDocument", { depth: 0 });
    const { nodeId } = await chrome.debugger.sendCommand(target, "DOM.querySelector", {
      nodeId: root.nodeId,
      selector,
    });
    if (!nodeId) throw new Error(`文件输入框不存在: ${selector}`);
    await chrome.debugger.sendCommand(target, "DOM.setFileInputFiles", {
      nodeId,
      files,  // 本地文件路径数组，由 Python 侧提供
    });
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
  return null;
}

// ───────────────────────── DOM 操作（MAIN world） ────────────────────

async function cmdDomInMainWorld(method, params) {
  const tab = await getOrOpenXhsTab();
  const results = await chrome.scripting.executeScript({
    target: { tabId: tab.id },
    world: "MAIN",
    func: domExecutor,
    args: [method, params],
  });
  const r = results?.[0]?.result;
  if (r && typeof r === "object" && "__xhs_error" in r) {
    throw new Error(r.__xhs_error);
  }
  return r ?? null;
}

/**
 * DOM 操作执行器，在页面 MAIN world 运行。
 * 不能引用外部变量，所有逻辑自包含。
 */
function domExecutor(method, params) {
  function sleep(ms) { return new Promise(r => setTimeout(r, ms)); }

  function requireEl(selector) {
    const el = document.querySelector(selector);
    if (!el) return { __xhs_error: `元素不存在: ${selector}` };
    return el;
  }

  switch (method) {
    case "input_text": {
      const el = requireEl(params.selector);
      if (el.__xhs_error) return el;
      el.focus();
      el.value = params.text;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
      return null;
    }

    case "input_content_editable": {
      return new Promise(async (resolve) => {
        const el = document.querySelector(params.selector);
        if (!el) { resolve({ __xhs_error: `元素不存在: ${params.selector}` }); return; }
        el.focus();
        document.execCommand("selectAll", false, null);
        document.execCommand("delete", false, null);
        await sleep(80);
        const lines = params.text.split("\n");
        for (let i = 0; i < lines.length; i++) {
          if (lines[i]) document.execCommand("insertText", false, lines[i]);
          if (i < lines.length - 1) {
            // insertParagraph 才能在 contenteditable 里真正插入换行
            document.execCommand("insertParagraph", false, null);
            await sleep(30);
          }
        }
        resolve(null);
      });
    }

    case "set_file_input": {
      return new Promise((resolve) => {
        const el = document.querySelector(params.selector);
        if (!el) { resolve({ __xhs_error: `文件输入框不存在: ${params.selector}` }); return; }

        function makeFiles() {
          const dt = new DataTransfer();
          for (const f of params.files) {
            const bytes = Uint8Array.from(atob(f.data), c => c.charCodeAt(0));
            dt.items.add(new File([bytes], f.name, { type: f.type }));
          }
          return dt;
        }

        // 方法1: 覆盖 files 属性 + change 事件（标准 file input）
        try {
          const dt = makeFiles();
          Object.defineProperty(el, "files", { value: dt.files, configurable: true, writable: true });
          el.dispatchEvent(new Event("change", { bubbles: true }));
          el.dispatchEvent(new Event("input", { bubbles: true }));
        } catch (e) {}

        // 方法2: drag-drop 到上传区域（XHS 主要监听 drop 事件）
        const dropTarget =
          el.closest('[class*="upload"]') ||
          el.closest('[class*="Upload"]') ||
          el.parentElement;
        if (dropTarget) {
          try {
            const dt2 = makeFiles();
            dropTarget.dispatchEvent(new DragEvent("dragenter", { bubbles: true, cancelable: true, dataTransfer: dt2 }));
            dropTarget.dispatchEvent(new DragEvent("dragover",  { bubbles: true, cancelable: true, dataTransfer: dt2 }));
            dropTarget.dispatchEvent(new DragEvent("drop",      { bubbles: true, cancelable: true, dataTransfer: dt2 }));
          } catch (e) {}
        }

        resolve(null);
      });
    }

    case "scroll_by":
      window.scrollBy(params.x || 0, params.y || 0); return null;
    case "scroll_to":
      window.scrollTo(params.x || 0, params.y || 0); return null;
    case "scroll_to_bottom":
      window.scrollTo(0, document.body.scrollHeight); return null;

    case "scroll_element_into_view": {
      const el = document.querySelector(params.selector);
      if (el) el.scrollIntoView({ behavior: "smooth", block: "center" });
      return null;
    }
    case "scroll_nth_element_into_view": {
      const els = document.querySelectorAll(params.selector);
      if (els[params.index]) els[params.index].scrollIntoView({ behavior: "smooth", block: "center" });
      return null;
    }

    case "dispatch_wheel_event": {
      const target = document.querySelector(".note-scroller") ||
        document.querySelector(".interaction-container") || document.documentElement;
      target.dispatchEvent(new WheelEvent("wheel", { deltaY: params.deltaY || 0, deltaMode: 0, bubbles: true, cancelable: true }));
      return null;
    }

    case "mouse_move":
      document.dispatchEvent(new MouseEvent("mousemove", { clientX: params.x, clientY: params.y, bubbles: true }));
      return null;

    case "mouse_click": {
      const el = document.elementFromPoint(params.x, params.y);
      if (el) {
        ["mousedown", "mouseup", "click"].forEach(t =>
          el.dispatchEvent(new MouseEvent(t, { clientX: params.x, clientY: params.y, bubbles: true }))
        );
      }
      return null;
    }

    case "remove_element": {
      const el = document.querySelector(params.selector);
      if (el) el.remove();
      return null;
    }

    case "hover_element": {
      const el = document.querySelector(params.selector);
      if (el) {
        const rect = el.getBoundingClientRect();
        const x = rect.left + rect.width / 2, y = rect.top + rect.height / 2;
        el.dispatchEvent(new MouseEvent("mouseover", { clientX: x, clientY: y, bubbles: true }));
        el.dispatchEvent(new MouseEvent("mousemove", { clientX: x, clientY: y, bubbles: true }));
      }
      return null;
    }

    case "select_all_text": {
      const el = document.querySelector(params.selector);
      if (el) { el.focus(); if (el.select) el.select(); else document.execCommand("selectAll"); }
      return null;
    }

    default:
      return { __xhs_error: `未知 DOM 命令: ${method}` };
  }
}

// ───────────────────────── Tab 管理 ─────────────────────────

async function getOrOpenXhsTab() {
  const tabs = await chrome.tabs.query({
    url: [
      "https://www.xiaohongshu.com/*",
      "https://xiaohongshu.com/*",
      "https://creator.xiaohongshu.com/*",
    ],
  });
  if (tabs.length > 1) {
    throw new Error("存在多个小红书标签页，无法确定操作对象；请先在此 Chrome 配置中只保留目标标签页");
  }
  if (tabs.length === 1) return tabs[0];
  // 没有已打开的 XHS 页面，新建一个
  const tab = await chrome.tabs.create({ url: "https://www.xiaohongshu.com/" });
  await waitForTabComplete(tab.id, null, 30000);
  return tab;
}

// ───────────────────────── 启动 ─────────────────────────

connect();
