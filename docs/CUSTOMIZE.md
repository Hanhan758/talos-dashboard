# 自定义指南

TALOS Dashboard 的设计原则是「一切可见内容都在数据数组里」。本指南告诉你怎么改。

---

## 1. 改数据数组（最常见的自定义）

打开 `dashboard.html`，翻到底部 `<script>` 块。所有内容都在这里：

### `quick` — 侧栏快捷入口

```js
const quick = [
  ['T', '示例：项目首页', 'example/your-project-home.md'],
  // ...
];
// 每项格式：[单字符图标, 显示名称, vault 相对路径]
```

### `commands` — 命令路由

```js
const commands = [
  ['/morning', '晨间简报与焦点启动'],
  // ...
];
// 每项格式：[斜杠命令, 说明]。点击复制到剪贴板。
```

### `projects` — 活跃项目卡

```js
const projects = [
  ['p0', 'P0 · 示例', 'TALOS 品牌发布', '描述...', 'G0 → M0', 'example/path.md', '🚀', 'linear-gradient(135deg,#0A45D6,#4D8DFF)'],
  // ...
];
// 每项格式：[优先级类, 标签, 名称, 描述, 追溯链, 笔记路径, emoji, 封面渐变 CSS]
// 优先级类：'p0'（红）/ 'p1'（黄）/ 'b'（蓝，B 端）
```

### `notes` — 理论/资产入口

```js
const notes = [
  ['TALOS 宣言', '白皮书 v0.3', 'example/notes/talos-manifesto.md'],
  // ...
];
// 每项格式：[标题, 副标, 笔记路径]
```

### `quotes` — Hero 信念金句轮播

```js
const quotes = [
  ['模型会商品化，上下文会差异化。', 'TALOS 核心主张'],
  // ...
];
// 每项格式：[金句, 出处标签]。点击 Hero 引用块切换。
```

### `seedTodos` — 初始 Todo 种子

```js
const seedTodos = [
  {text:'示例：把 dashboard.html 复制到 vault', tag:'p0', done:false},
  // ...
];
// 仅首次打开生效；用户编辑后会写 localStorage 覆盖。
```

---

## 2. v2.0 配色定制

### 全局色板

`:root` 里的 CSS 变量，改这里全部主题色一起变：

```css
:root{
  --blue:#4D8DFF;
  --cyan:#38E1FF;
  --violet:#A78BFA;
  --pink:#F472B6;
  --rose:#FB7185;
  --orange:#FB923C;
  --amber:#FBBF24;
  --green:#34D399;
}
```

### 区块主题色

每个 `<section>` 标签上的内联 `--ac` 控制该卡片的标记点、顶部光线、悬停辉光：

```html
<section class="card" style="--ac:#A78BFA">
  <!-- 这个卡片用 violet 主题色 -->
</section>
```

### 背景极光

`.orb.o1~o4` 四个径向渐变球（颜色、大小、位置、动画时长都可改）：

```css
.orb.o1{width:560px;height:560px;left:-12%;top:-18%;
  background:radial-gradient(circle,#2D62FF,transparent 65%);
  animation:drift1 26s ease-in-out infinite}
```

### 彩虹流动元素

`--rainbow` 渐变被 Hero 描边、toast 边框、eyebrow 文字共用：

```css
--rainbow:linear-gradient(90deg,#FB7185,#FB923C,#FBBF24,#34D399,#38E1FF,#4D8DFF,#A78BFA,#F472B6,#FB7185);
```

### 条形图每行颜色

`vault` 数组（在 `refresh-dashboard.py` 写入的 STATS 块中），每行末尾的两个色值控制该行渐变：

```js
const VAULT_META = {
  "Projects":  ["projects/index.md","#4D8DFF","#38E1FF"],  // start → end color
  // ...
};
```

### 嫌动画多？

删 / 注释对应 `@keyframes` 即可。已内置 `prefers-reduced-motion` 降级，用户在系统设置里关掉动画会自动静态化。

---

## 3. 添加新模块

模板（以一个简单「统计面板」为例）：

```html
<!-- 1. 在 <main class="main"> 里找个位置放进去 -->
<section class="panel" style="--ac:#38E1FF">
  <div class="section-title">
    <h2>新模块</h2>
    <small>副标</small>
  </div>
  <div id="newModule"></div>
</section>

<!-- 2. 在 <script> 里渲染 -->
<script>
const newModuleData = [
  ['item1', 100],
  ['item2', 80],
];
document.getElementById('newModule').innerHTML = newModuleData.map(([label, value]) =>
  `<div>${label}: ${value}</div>`).join('');
</script>
```

记住三件事：
- 用 `class="panel"` + `style="--ac:#xxx"` 套上主题色与卡片样式
- 标题块用 `class="section-title"`
- 内容用 `id` 锚定，JS 渲染时 `innerHTML` 进去

---

## 4. 自定义扫描规则

`refresh-dashboard.py` 顶部的「配置区」是所有扫描规则的入口：

```python
# 六大内容目录（显示名 -> 相对路径）
CONTENT_DIRS = [
    ("Projects",  "projects"),
    ("Materials", "materials"),
    # ...
]

# 排除路径片段
EXCLUDE = ("/node_modules/", "/.git/", "/.obsidian/", "/.trash/")

# 各类条目计数文件 + 标题关键字
CANDIDATES_FILE = "System/working-memory/candidates.md"
CANDIDATES_HEADER = "待确认"

APPROVALS_FILE = "System/pending-approvals.md"
APPROVALS_HEADER = "当前待审批"

HEALTH_FILE = "System/working-memory/health-log.md"
TASKS_FILE = "System/working-memory/tasks.md"
TASKS_FOCUS_HEADER = "焦点"
```

### 常见自定义场景

**「我没有 `pending-approvals.md`」**：把 `APPROVALS_FILE` 指向任何 `## 标题` 结构的 md 文件，或干脆改 `count_section_items` 调用。

**「健康分从别的文件读」**：改 `parse_health()` 的正则匹配规则。当前规则是从 `<!-- EVAL_HISTORY -->…<!-- EVAL_HISTORY_END -->` 注释块里读 markdown 表格行。

**「我想要新的统计指标（比如本周新增笔记数）」**：在 `build_stats()` 里加新字段，到 `dashboard.html` 里渲染对应位置。需要懂一点 Python + JS。

**「我的 vault 目录结构完全不同」**：只改 `CONTENT_DIRS` 就够了。

---

## 5. 改 Logo / 品牌名

Logo 是 SVG，在 Hero 区：

```html
<div class="logo" aria-label="TALOS">
  <svg viewBox="96 191 360 360" xmlns="http://www.w3.org/2000/svg">
    <path fill="#FFFFFF" d="M180 247H249V286H304V247H374..."/>
    <path fill="#7C3AED" d="M199 326H353V373H306V460H247..."/>
  </svg>
</div>
```

把 `<svg>` 内容替换成你自己的矢量图（建议 24×24 viewBox 内归一化）。

品牌名与标语在同 `<header class="hero">` 内：

```html
<div class="eyebrow">TALOS PERSONAL CONTEXT OS<span class="live"><i></i>ONLINE</span></div>
<h1>外脑玩家 Haaper 控制台</h1>
<div class="sub">AI 系统架构师 · 个人上下文主权 · C 端布道 × B 端交付</div>
```

---

## 6. 关闭某些模块

注释掉对应 `<section>` 即可。JS 里如果对应 `id` 找不到，浏览器控制台会报错但不影响其他模块。
