# 「我是怎么造的」构建教程

> 本文写给两类人：① 想完全理解 TALOS Dashboard 工程实现的人；② 想自己造一个类似仪表盘的人。
>
> 假设你已读过 [ARCHITECTURE.md](ARCHITECTURE.md) 知道整体形态。

---

## 1. 为什么需要「个人 OS 仪表盘」

每个用 Obsidian / Notion / Roam 的人都会撞到同一个问题：**vault 越大，启动越迷茫。**

打开 Obsidian，看到的是上次打开的笔记或空标签页。要花十几秒想「我今天该干啥？最近的项目在哪？收件箱有没有积压？」。这十几秒是高频损耗。

更深层的问题是：**碎片化的笔记 ≠ 结构化的上下文**。你有 1000 篇笔记，但不打开它们你就想不起里面有什么；你想给 AI 喂「我现在在做什么」，得手动翻半天。

TALOS Dashboard 的解题思路：把整个 vault 的**态势感知**集中到一张页面——
- 你是谁（Hero + 信念金句）
- 你在做什么（活跃项目 + 今日焦点）
- 你的系统健康吗（笔记数 / 收件箱 / 待审批 / 健康趋势）
- 你常用什么入口（快捷入口 + 命令路由）

开机即看到，零决策成本进入心流。

---

## 2. 设计取法

视觉与「一页式工作台」形态启发自 [Apex Dashboard](https://github.com/PandoraReads/apex-dashboard) by PandoraReads——一个基于 CSS 一页式仪表盘的项目。TALOS Dashboard 在它基础上的改造：

| 维度 | Apex | TALOS |
|---|---|---|
| 部署 | 独立 HTML | 嵌入 Obsidian 首页 |
| 数据 | 硬编码 | vault 扫描器动态生成 |
| 交互 | 自身页面跳转 | postMessage 桥接宿主 |
| 视觉 | 蓝白浅色 | 极光深色 + 多彩流动 |
| 内容 | 通用 demo | 个人上下文 OS 范式 |

---

## 3. 三个关键工程问题及解法

### 问题 1：Obsidian 阅读视图过滤 `<script>`

**现象**：在 Markdown 笔记里写 `<script>alert(1)</script>`，阅读视图渲染时会被剥掉。Obsidian 出于安全考虑默认不让笔记执行任意 JS。

**尝试**：
- 用 Markdown 里的 HTML 代码块 → 被过滤
- 用 Dataview 的 `dv.paragraph()` 输出 HTML → 输出后被过滤
- 用 Dataview 的 DQL 查询 → 不够灵活，无法渲染复杂 HTML

**解法**：开启 Dataview 的 **Enable JavaScript Queries**，用 `dataviewjs` 代码块 + `dv.container.appendChild()` 直接操作 DOM。

```js
```dataviewjs
const iframe = document.createElement("iframe");
iframe.srcdoc = "<h1>Hello</h1><script>alert('hi')</script>";
dv.container.appendChild(iframe);
```
```

**为什么有效**：`dataviewjs` 是 Dataview 提供的 JS 沙盒，相当于「用户授权执行的 JS」。它操作 DOM 注入的元素不被阅读视图的过滤流程影响。`iframe.srcdoc` 内的内容在 iframe 自己的上下文里执行，跟宿主隔离但可以正常跑。

### 问题 2：iframe 内点击不能直接跳转到 Obsidian 笔记

**现象**：iframe 里写 `<a href="obsidian://open?vault=xxx&file=yyy">` 不稳定，自定义协议在 iframe 内行为不一致。

**解法**：`postMessage` 桥接。

**iframe 内（dashboard.html）**：

```js
const openPath = path => window.parent && window.parent !== window
  ? window.parent.postMessage({type:'talos-open', path}, '*')
  : window.open(path, '_blank');

document.addEventListener('click', e => {
  const el = e.target.closest('[data-path]');
  if (!el) return;
  e.preventDefault();
  openPath(el.dataset.path);
});
```

每个卡片带 `data-path="..."` 属性，点击时通过 `postMessage` 通知父窗口。

**宿主（homepage.md）**：

```js
if (!window.__talosNavInstalled) {
  window.__talosNavInstalled = true;
  window.addEventListener("message", async (ev) => {
    const d = ev.data;
    if (!d || d.type !== "talos-open" || !d.path) return;
    const p = d.path;
    if (p.toLowerCase().endsWith(".html") && app.openWithDefaultApp) {
      app.openWithDefaultApp(p);
    } else {
      await app.workspace.openLinkText(p, "", "tab");
    }
  });
}
```

宿主用 Obsidian 的 `app.workspace.openLinkText(path, "", "tab")` API 在新标签打开 `.md`，`app.openWithDefaultApp` 用系统默认程序打开 `.html`。

**幂等保护**：`__talosNavInstalled` 防止 listener 被重复注册（每次 homepage 重新渲染都会再跑一次 dataviewjs）。

### 问题 3：静态 HTML 数据会过时

**现象**：仪表盘上写「笔记 717 篇」，过几天 vault 涨到 725 了，HTML 不更新。

**尝试**：
- 在 dataviewjs 里实时统计 → 每次打开首页都全盘扫描，性能差
- 在 iframe 内 JS 主动读 vault → srcdoc 内的 JS 没有 `app.vault` 访问权
- 写个 daemon 持续监听文件变化 → 太重

**解法**：分层数据。

- **高频动态**（时钟、周历、倒计时、Todo、Memo）：iframe 内 JS 实时计算或读 localStorage
- **低频态势**（笔记数、收件箱、待审批、健康趋势、今日焦点）：标记 `/*STATS:START*/…/*STATS:END*/`，由 `refresh-dashboard.py` 定期重写

```html
<script>
/*STATS:START*/
/* 自动生成，请勿手改。最后更新：2026-06-17 */
const STATS = { "totalNotes": 0, ... };
/*STATS:END*/

// 后续 JS 直接读 STATS.xxx
document.getElementById('statNotes').dataset.count = STATS.totalNotes;
</script>
```

`refresh-dashboard.py` 用正则替换整个 STATS 块：

```python
html = re.sub(
    r"/\*STATS:START\*/.*?/\*STATS:END\*/",
    lambda _: new_block,
    html,
    flags=re.S,
)
```

跑一次成本：< 1 秒（普通 vault 1000~5000 篇 md）。建议挂在 crontab / launchd 每天跑。

---

## 4. 视觉系统设计

### 极光背景

四个径向渐变球 + 90px blur + screen 混合模式，营造「极光漂浮」氛围：

```css
.orb{position:absolute;border-radius:50%;filter:blur(90px);opacity:.5;mix-blend-mode:screen}
.orb.o1{background:radial-gradient(circle,#2D62FF,transparent 65%);animation:drift1 26s ease-in-out infinite}
```

每个球独立的 `drift` 动画（不同时长、不同方向、不同缩放），叠加出有机的流动感。

### 彩虹描边

Hero 卡片的边框是流动的彩虹，用 `conic-gradient` + `mask-composite` 技巧实现：

```css
.hero{padding:22px;overflow:hidden;border:none}
.hero:before{
  content:"";position:absolute;inset:0;border-radius:inherit;padding:1.5px;
  background:conic-gradient(#FB7185,#FB923C,#FBBF24,#34D399,#38E1FF,#4D8DFF,#A78BFA,#F472B6,#FB7185);
  -webkit-mask:linear-gradient(#fff 0 0) content-box,linear-gradient(#fff 0 0);
  -webkit-mask-composite:xor;mask-composite:exclude;
  animation:hue 7s linear infinite;pointer-events:none;
}
```

原理：把渐变画在伪元素的整个区域，用 mask 把中间挖空，只留下 1.5px 的边框。`hue-rotate` 让颜色循环。

### 入场动效

三套独立动效叠加：

1. **卡片上浮**：每个卡片 `animation: rise .55s`，按 `nth-child` 顺序延迟 `.05s`、`.12s`、`.19s`...，形成从上到下的瀑布感。
2. **数字滚动**：每个 `<b data-count="N">` 元素，JS 用 `requestAnimationFrame` 做 1.1s 的 ease-out 计数动画。
3. **进度条生长 + 折线描线**：进度条 `width` 从 0 过渡到目标值；折线用 `stroke-dasharray + stroke-dashoffset` 从满到 0 的描线动画。

```js
// 折线描线
const len = hl.getTotalLength();
hl.style.strokeDasharray = len;
hl.style.strokeDashoffset = len;
hl.style.transition = 'stroke-dashoffset 1.6s cubic-bezier(.2,.7,.2,1) .3s';
requestAnimationFrame(() => requestAnimationFrame(() => { hl.style.strokeDashoffset = '0'; }));
```

双 `requestAnimationFrame` 是为了等浏览器先把初始状态画出来，再触发过渡——单层 raf 有时不生效。

### 悬停微交互

每个卡片悬停时 `transform: translateY(-2px)`、边框变亮、辉光扩散。项目卡封面 emoji 用 `pop` 动画轻微弹跳旋转。所有微交互都 `transition: .18s ease`，跟手不黏滞。

### 无障碍降级

```css
@media (prefers-reduced-motion:reduce){
  *,*:before,*:after{animation:none !important;transition:none !important}
  .bar i,.bwrap i{width:var(--w,100%) !important}
}
```

用户在系统设置里关掉动画时，仪表盘自动降级为静态——所有进度条直接显示终值，没有动效。

---

## 5. 关键代码段解读

### `dashboard.html` 的数据数组

所有可见内容都在底部 `<script>` 里的常量数组：

```js
const quick = [...];      // 侧栏入口
const commands = [...];   // 命令路由
const projects = [...];   // 活跃项目
const notes = [...];      // 理论入口
const quotes = [...];     // 信念金句
const seedTodos = [...];  // 初始 Todo
```

这些数组用 `.map().join('')` 渲染成 HTML 字符串，`innerHTML` 进对应容器。这是最简单也最有效的「数据驱动视图」模式——不需要 React/Vue。

### `refresh-dashboard.py` 的扫描逻辑

核心是三个函数：

```python
def count_md(vault, rel_dir):
    """rglob('*.md')，排除以 _ 开头的内部文件 + EXCLUDE 路径"""

def count_section_items(vault, file_rel, header_kw):
    """读 md 文件，找 '## 关键字' 区，数 '- ' 开头的行"""

def parse_focus(vault, n=3):
    """读 tasks.md 的 ## 焦点 区，正则匹配 emoji + **标题** + 描述"""
```

每个函数都有 fallback（文件不存在返回 0 / []），所以哪怕你的 vault 没有某些文件也不会崩。

---

## 6. 二次开发建议

1. **不要引入打包工具**。仪表盘的「离线可用 + 零依赖」是核心卖点。引入 npm/webpack 会让部署复杂度爆炸。
2. **保持数据数组在底部**。新人改内容时一眼能看到，不需要在 800 行 HTML 里翻找。
3. **新模块先写在 HTML 里**，能用了再考虑抽到 refresh.py 的 STATS 里。不要过早数据化。
4. **改完先在浏览器直接打开 dashboard.html 看视觉**，确认无 JS 错误再进 Obsidian 测试。浏览器的 devtools 比 Obsidian 的好使。
5. **样式用 CSS 变量**。`--ac` 这个变量被一个卡片内的多个元素共用（标记点、顶部光线、悬停辉光），改一处全联动。

---

## 7. 下一步

- 看一遍 [dashboard.html](../dashboard.html) 的源码，从 `<!-- ===== 极光背景 ===== -->` 开始。
- 想加新模块？[CUSTOMIZE.md §3](CUSTOMIZE.md#3-添加新模块)。
- 想改数据源？[CUSTOMIZE.md §4](CUSTOMIZE.md#4-自定义扫描规则)。
- 想懂整体流程？[ARCHITECTURE.md](ARCHITECTURE.md)。

如果这张仪表盘帮到了你，欢迎在 GitHub 给个 star，或在你的内容里提一下 TALOS ——让更多人意识到「上下文主权」这件事。
