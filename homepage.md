---
title: TALOS 仪表盘首页
date: 2026-06-17
tags: [仪表盘, 首页, TALOS]
status: active
type: system
summary: "Obsidian 启动首页：用 Dataview JS 内联 TALOS 控制台，整页铺满、卡片点击经 postMessage 在库内直达笔记。"
cssclasses: [dashboard-home]
---

<!--
  这是「首页包装笔记」：本身没有可见正文，靠下方 dataviewjs 代码块读取 dashboard.html
  并以 iframe(srcdoc) 内联渲染。Homepage 插件会把它设为开机首页，CSS 片段去掉笔记外壳
  让 iframe 整页铺满。

  部署步骤：
  1. 复制本文件到 vault 根目录（或任意位置，但下一步路径要对得上）
  2. 复制 dashboard.html 到 vault 内任意位置（建议与首页同级或就近）
  3. 把下方 `const path = "..."` 改成 dashboard.html 在你 vault 内的相对路径
  4. 安装 Homepage 插件，把本笔记设为开机首页（详见 docs/DEPLOYMENT.md）
-->

```dataviewjs
// === 导航桥：iframe 内卡片点击 → 在 Obsidian 内打开对应笔记/文件 ===
if (!window.__talosNavInstalled) {
  window.__talosNavInstalled = true;
  window.addEventListener("message", async (ev) => {
    const d = ev.data;
    if (!d || d.type !== "talos-open" || !d.path) return;
    const p = d.path;
    try {
      if (p.toLowerCase().endsWith(".html") && app.openWithDefaultApp) {
        app.openWithDefaultApp(p);            // HTML 用系统/内置浏览器打开
      } else {
        await app.workspace.openLinkText(p, "", "tab"); // md 等在新标签打开，保留工作台
      }
    } catch (err) {
      try { await app.workspace.openLinkText(p, "", "tab"); }
      catch (e2) { console.error("talos-open 失败:", p, e2); }
    }
  });
}

// === 实时读取仪表盘 HTML 并注入 iframe ===
// 改成你 vault 内 dashboard.html 的相对路径（相对 vault 根，不含前导 /）。
const path = "dashboard.html";
try {
  const html = await app.vault.adapter.read(path);
  const iframe = document.createElement("iframe");
  iframe.srcdoc = html;
  iframe.style.cssText = "width:100%;height:96vh;min-height:600px;border:0;display:block;";
  iframe.setAttribute("allow", "clipboard-write");
  dv.container.style.padding = "0";
  dv.container.style.margin = "0";
  dv.container.appendChild(iframe);
} catch (e) {
  dv.paragraph("⚠️ 无法加载 " + path + "：" + e.message + "\n请确认文件存在，且 Dataview 已开启 *Enable JavaScript Queries*。");
}
```
