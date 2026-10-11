function renderStatus(wsConnected) {
  set("bridge-status", "bridge-dot", "bridge-text", wsConnected, wsConnected ? "已连接" : "未连接");
  set("ext-status",   "ext-dot",   "ext-text",   true, "运行中");
  document.getElementById("hint").textContent = wsConnected
    ? "连接已就绪；这不代表账号已登录。"
    : "请按 Skill 的 setup.md 启动本地 Bridge 服务。";
}

function set(badgeId, dotId, textId, ok, label) {
  const cls = ok ? "ok" : "err";
  document.getElementById(badgeId).className  = `badge ${cls}`;
  document.getElementById(dotId).className    = `dot ${cls}`;
  document.getElementById(textId).textContent = label;
}

// 初始化：拉取当前状态
try {
  chrome.runtime.sendMessage({ type: "GET_STATUS" }, (resp) => {
    if (chrome.runtime.lastError || !resp?.success) {
      renderStatus(false);
      return;
    }
    renderStatus(resp.status.wsConnected);
  });
} catch (e) {
  renderStatus(false);
}

// 实时监听状态变化（background 主动推送）
chrome.runtime.onMessage.addListener((msg) => {
  if (msg.type === "STATUS_CHANGED") {
    renderStatus(msg.status.wsConnected);
  }
});
