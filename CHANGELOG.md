# Changelog

本项目遵循 [Semantic Versioning](https://semver.org/)。

## [1.0.0] — 2026-06-17

**开源首版。**

- 将库内自用的 TALOS 控制台整理为独立可分发的开源仓库。
- 三件套脱敏：`apex-*` 命名残留统一改 `talos-*`；STATS 块清零为示例数据；`quick` / `commands` / `projects` / `notes` 路径改占位符 + 注释；今日焦点、Hero 状态卡、倒计时改为通用示例。
- `refresh-dashboard.py` 改造为可配置：支持 `--vault` / `--dashboard` 参数；目录映射、文件路径、关键字全部抽到顶部「配置区」。
- 新增 `README.md` / `LICENSE`（AGPL-3.0）/ `.gitignore`。
- 新增 `docs/DEPLOYMENT.md` / `docs/CUSTOMIZE.md` / `docs/ARCHITECTURE.md` / `docs/BUILD_TUTORIAL.md`。
- 首页笔记英文化为 `homepage.md`，加顶部部署注释。

## [0.4.0] — 2026-06-15

**数据动态化。**

- 仪表盘统计从硬编码改为脚本生成。
- 新增 `refresh-dashboard.py`：扫描六大内容目录笔记数、收件箱、待审批（`pending-approvals`）、偏好候选（`candidates`）、健康分趋势（`health-log`）、今日焦点（`tasks.md`），写入 `dashboard.html` 的 `/*STATS:START*/…/*STATS:END*/` 块。
- 修复旧版数据过时与内部矛盾（原显示笔记 1548/收件箱 7，实为 705/61；「共 1548 篇」标签与条形和 793 不符）。
- 现知识库分布标签 = 条形之和，全口径一致。

## [0.3.0] — 2026-06-10

**v2.0 多彩极光动画版。**

- 深色「多彩极光动画」主题：四色极光球漂浮背景、Hero 彩虹流动描边、渐变流动标题/时钟/健康分、每个区块独立主题色。
- 入场动效：卡片逐个上浮、数字滚动计数、进度条生长、折线描线绘出。
- 悬停微交互：位移、发光、图标弹跳。
- 自动支持 `prefers-reduced-motion` 降级为静态。
- 功能逻辑与 localStorage 键自 v1.0 起保持兼容。

## [0.2.0] — 2026-06-10

**深色指挥中心改版。**

- 浅色蓝白 → 深蓝黑底 + 电光蓝/青色高亮 + 发光数据 + 等宽数字字体。
- 布局微调：今日焦点与 Todo 上移至 hero 下方第一行；命令路由与 Memo 合并为一行。
- 全部功能逻辑与 localStorage 键不变。

## [0.1.0] — 2026-06-05

**初始版本。**

- 单文件 HTML 控制台作为 Obsidian 启动首页。
- 模块：Hero + 侧栏 + 项目/Todo/命令/Memo + 主题化界面。
- 通过 Homepage 插件 + `dataviewjs` 注入 `iframe(srcdoc)`；卡片可点击经 `postMessage` 桥接宿主 `openLinkText` / `openWithDefaultApp`。
- CSS 片段去外壳、击穿可读行宽、满宽铺满。
