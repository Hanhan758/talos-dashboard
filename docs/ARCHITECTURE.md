# 架构与设计决策

本文解释 TALOS Dashboard 的关键工程决策、数据流、实现历程。理解这些有助于二次开发与排障。

---

## 1. 形态总览

```
┌─────────────────────────────────────────────────────────┐
│  Obsidian 启动                                            │
│     ↓                                                     │
│  Homepage 插件 → 自动打开 homepage.md                     │
│     ↓                                                     │
│  homepage.md 的 dataviewjs 读取 dashboard.html            │
│     ↓                                                     │
│  iframe(srcdoc=html) 内联渲染                              │
│     ↓                                                     │
│  CSS 片段 talos-dashboard-home.css 击穿外壳，iframe 满宽    │
│     ↓                                                     │
│  dashboard.html 内 <script> 渲染所有模块                   │
│     ↓                                                     │
│  数据从 STATS 块读取（refresh-dashboard.py 写入）           │
│     ↓                                                     │
│  用户点卡片 → postMessage(talos-open) → 宿主打开笔记        │
└─────────────────────────────────────────────────────────┘
```

---

## 2. 关键技术决策

| 决策 | 为什么这么做 | 代价 |
|---|---|---|
| HTML 用 `dataviewjs` + `iframe.srcdoc` 内联 | Obsidian 阅读视图过滤 `<script>` 与 `srcdoc`，但 **dataviewjs 用 DOM 注入的 iframe 不受过滤**，脚本可运行；`srcdoc` 与宿主同源，localStorage 正常；HTML 始终是单一可编辑源，改完无需重新生成笔记 | 必须装 Dataview + Homepage 两个插件 |
| 卡片点击用 `postMessage` 桥接 | iframe 内跳转自定义协议不稳定。卡片带 `data-path`，点击 `postMessage` 给宿主；宿主 dataviewjs 监听后 `.md` → `openLinkText(..,'tab')`，`.html` → `openWithDefaultApp` | 需要在 homepage.md 里写一段导航桥监听代码 |
| 用 CSS 片段去外壳 + 击穿「可读行宽」 | 默认会显示笔记标题/属性面板，且主题把正文压窄居中。片段隐藏这些并强制满宽，使其像独立 App | 片段路径固定，迁机器要重指 |
| 部分指标（笔记数/收件箱/审批/健康/焦点）为**静态 STATS 块** | `srcdoc` 内的脚本无法实时读 vault 里的 `.md`。这些数字写死在 HTML 里，由 `refresh-dashboard.py` 按需重生成（时钟/周历/倒计时是动态计算的） | 数据有延迟，需要定期跑脚本 |
| 图表用纯 SVG/CSS，不引第三方库 | 离线可用、体积小、渲染稳定、易定制 | 折线图、柱状图得手写，复杂图表不适用 |
| localStorage 存 Todo / Memo | 本机持久、零依赖、隐私可控 | 不跨设备同步，清缓存会丢 |

---

## 3. 数据流

```
vault 目录文件
   │
   ├── *.md × N        ──┐
   ├── candidates.md     │
   ├── pending-...md     ├──→ refresh-dashboard.py
   ├── health-log.md     │       扫描 + 解析
   ├── tasks.md          │       ↓
   │                  ───┘   STATS = { ... }
   │                          
   ↓                          
dashboard.html 的 /*STATS:START*/ 块
   ↓
浏览器渲染时 JS 读 STATS，填充各模块
```

**更新周期**：手动 / 定时任务。**不在每次打开仪表盘时实时扫描**——这是性能权衡（避免每次打开都全盘 `rglob`）。

---

## 4. 文件职责

| 文件 | 职责 | 改动频率 |
|---|---|---|
| `dashboard.html` | 仪表盘本体（结构 + 样式 + 数据数组 + 渲染逻辑） | 高（自定义内容） |
| `refresh-dashboard.py` | 数据扫描器（vault → STATS 块） | 中（自定义扫描规则时改） |
| `homepage.md` | 首页包装笔记（dataviewjs + 导航桥监听） | 极低（部署时改一次） |
| `talos-dashboard-home.css` | 去外壳 + 满宽片段 | 极低（除非 Obsidian 升级改了 DOM） |

---

## 5. localStorage 键

| 键 | 内容 | 清除时机 |
|---|---|---|
| `talos_console_memo` | Memo 文本 | 用户手动清 / 浏览器清缓存 |
| `talos_console_todos` | Todo 数组（用户编辑后覆盖 seedTodos） | 同上 |

跨设备不同步，迁机器会丢——这是设计取舍（不引入云同步依赖）。

---

## 6. 实现历程（10 步迭代）

1. **调研一页式工作台形态** → 选定「单文件 HTML 仪表盘」路线，结合 TELOS 身份系统填充真实内容。
2. **搭主体**：Hero + 侧栏 + 项目/Todo/命令/Memo + 主题。
3. **接 Obsidian 首页**：用 Homepage 插件 + `dataviewjs` 注入 `iframe(srcdoc)`；踩坑「Dataview JS 默认关闭导致空白」「阅读视图过滤 srcdoc」。
4. **整页化**：CSS 片段去外壳、击穿可读行宽、满宽铺满（踩坑「`height:100%` 链 + `overflow:hidden` 导致塌缩空白」，回退为 `96vh`）。
5. **卡片可点击**：`postMessage` 桥接 → 宿主 `openLinkText`/`openWithDefaultApp`，项目卡指向各项目入口笔记。
6. **视觉与品牌**：替换为 TALOS 矢量 Logo、放大姓名主标题。
7. **增模块**：项目卡领域配色封面；新增今日焦点、待审批、知识库分布条形图、健康分趋势折线。
8. **版式微调**：今日焦点 ↔ 活跃项目、Memo ↔ Todo 位置互换。
9. **v2 改版**（2026-06-10）：浅色蓝白 → 深色「指挥中心」风格；布局微调（今日焦点+Todo 上移至首屏，命令路由+Memo 合并一行）。
10. **v2.0 极光版**（2026-06-10）：叠加多彩动画——极光漂浮背景、彩虹流动描边、渐变流动文字、入场/数字滚动/进度条生长/折线描线动画、区块独立主题色、悬停微交互；加入 `prefers-reduced-motion` 降级。

详细日期见 [CHANGELOG.md](../CHANGELOG.md)。

---

## 7. 二次开发指引

**想加新模块**：见 [CUSTOMIZE.md §3 添加新模块](CUSTOMIZE.md#3-添加新模块)。

**想换数据源**：改 `refresh-dashboard.py` 的 `build_stats()`。

**想做主题变体**：复制一份 `dashboard.html`，改 `:root` 变量；考虑用 CSS 自定义属性切换器（v1.2 计划）。

**想做插件化**（npm 风格）：不建议。仪表盘本质是「一张 HTML + 一段 JS」，引入打包工具会让离线可用、零依赖这两个核心卖点受损。要做就另起 fork。
