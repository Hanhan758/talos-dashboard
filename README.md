<div align="center">

# TALOS Dashboard

### 超级大脑早期交互探索 · 已停止维护的 Obsidian 仪表盘

<p>
  <a href="#-快速开始">快速开始</a> ·
  <a href="docs/CUSTOMIZE.md">自定义</a> ·
  <a href="docs/ARCHITECTURE.md">架构</a> ·
  <a href="docs/BUILD_TUTORIAL.md">构建教程</a> ·
  <a href="CHANGELOG.md">更新日志</a>
</p>

![TALOS Dashboard](screenshots/hero.png)

<p>
  <img alt="License" src="https://img.shields.io/badge/license-AGPL--3.0-blue.svg">
  <img alt="Dependencies" src="https://img.shields.io/badge/dependencies-zero-green.svg">
  <img alt="Obsidian" src="https://img.shields.io/badge/Obsidian-1.5%2B-purple.svg">
</p>

</div>

---

> [!IMPORTANT]
> **项目状态：最终版本 / 停止维护。**
> 这是早期「超级大脑」的插件雏形，也是开始尝试数据统计与前端交互时的创意项目。
> 当前维护者后续不会继续功能开发或日常维护；仓库保留最后版本与历史资料。
> 欢迎有能力的开发者基于 AGPL-3.0 fork、研究并继续维护，但请自行验证兼容性、依赖、
> 数据安全与后续改动。

**TALOS Dashboard** 是最早期的超级大脑插件想法之一。它尝试把知识库、项目和系统状态
从文件结构转换成可见、可浏览、可交互的前端界面，也是后来 TALOS 插件方向的早期雏形。

这个项目投入的时间和精力有限，没有发展成持续维护的成熟产品。它不是当前完整 TALOS，
也不是现行产品架构或数据模型；它的主要价值是记录数据统计如何成为产品入口，并为总览、
模块切换、局部特写和响应式布局提供前端交互思路。

## 与当前 TALOS 的关系

当前 TALOS 围绕个人与企业的数据管理、学习路径和大模型实际应用演进。首版以规范方案包与 Obsidian 插件配套，完整产品仍在建设与验证。

本仓库保留早期实现和交互经验，不是新首版安装入口，也不恢复功能维护。当前方向见 [TALOS Framework](https://github.com/Hanhan758/talos-framework)；公开框架 [v0.5 正式版](https://github.com/Hanhan758/talos-framework/releases/tag/v0.5)已发布，完整软件首版仍在建设与验证。

## ✨ 特性

- **极光视觉** · 四色漂浮光球、Hero 彩虹流动描边、入场卡片上浮+数字滚动+进度条生长+折线描线动画、悬停微交互；纯 CSS/原生 JS 实现，离线可用，并自动支持 `prefers-reduced-motion` 降级。
- **Obsidian 集成** · 通过 Dataview JS + `iframe(srcdoc)` 内联，一张 HTML 始终是唯一可编辑源；卡片点击经 `postMessage` 桥接，在库内直达笔记（`.md` 新标签、`.html` 系统默认浏览器）。
- **数据动态化** · 自带 `refresh-dashboard.py` 扫描 vault，把笔记数、收件箱、待审批、偏好候选、健康分趋势、今日焦点写入 HTML 的 STATS 块；数字不再过时。
- **零依赖** · 无 npm、无 CDN、无第三方库；只需 Obsidian + Dataview + Homepage 两个社区插件。
- **完全可定制** · 全部内容（项目卡、命令路由、快捷入口、信念金句、理论入口、配色）都在 HTML 末尾的 `<script>` 数据数组里，改数组即生效。

## 🎬 Demo

![完整视图](screenshots/full-page.png)

<details>
<summary><b>📸 模块特写（点击展开）</b></summary>

| 模块 | 截图 |
|---|---|
| 侧栏 · 时钟 / 快速入口 / TELOS 目标 / 倒计时 | ![Sidebar](screenshots/sidebar.png) |
| 活跃项目卡片网格 | ![Projects](screenshots/projects.png) |
| 命令路由 + Memo | ![Commands](screenshots/commands.png) |

</details>

> 动图 demo（入场动画 + 悬停弹跳）首版待补，规格见 [`screenshots/README.md`](screenshots/README.md)。

## 📦 快速开始

**前置**：Obsidian 桌面版 + 两个社区插件（Dataview、Homepage）。

```bash
git clone https://github.com/Hanhan758/talos-dashboard.git
cd talos-dashboard
```

把 `dashboard.html` / `homepage.md` / `talos-dashboard-home.css` 复制到你的 vault，安装插件，改 4 个 JSON，重启 Obsidian。详细 5 步部署见 **[docs/DEPLOYMENT.md](docs/DEPLOYMENT.md)**。

刷新数据：

```bash
python3 refresh-dashboard.py --vault /path/to/your/vault
```

## 🎨 自定义

- 改项目卡、命令路由、快捷入口、信念金句：编辑 `dashboard.html` 末尾的 `<script>` 数据数组。
- 改全局色板、区块主题色、极光背景、彩虹流动：编辑 `<style>` 内的 `:root` 变量与各 `<section>` 内联 `--ac`。
- 改 `refresh-dashboard.py` 扫描的目录与文件：编辑脚本顶部的「配置区」。

完整指南见 **[docs/CUSTOMIZE.md](docs/CUSTOMIZE.md)**。

## 🏗 架构

| 决策 | 为什么这么做 |
|---|---|
| HTML 用 `dataviewjs` + `iframe.srcdoc` 内联 | Obsidian 阅读视图过滤 `<script>`，但 dataviewjs 用 DOM 注入的 iframe 不受过滤 |
| 卡片点击用 `postMessage` 桥接 | iframe 内跳转自定义协议不稳定；桥接后 `.md` → `openLinkText(tab)`，`.html` → `openWithDefaultApp` |
| 用 CSS 片段去外壳 + 击穿「可读行宽」 | 让 iframe 像 App 一样整页铺满，而不是被笔记主题压窄 |
| 数据用静态 STATS 块 + Python 扫描器 | iframe 内脚本无法实时读 vault 里的 `.md`，扫描器按需重生成即可 |

详见 **[docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)**。

## 📖 构建教程

「我是怎么从零造出这张仪表盘的」——三个关键工程问题的解法、视觉系统的设计逻辑、关键代码段解读、二次开发建议。

详见 **[docs/BUILD_TUTORIAL.md](docs/BUILD_TUTORIAL.md)**。

## 🙏 致谢

- 视觉与「一页式工作台」形态启发自 **[Apex Dashboard](https://github.com/PandoraReads/apex-dashboard)** by PandoraReads。
- 信念金句与项目叙事来自 **TALOS** 个人上下文操作系统理论框架。

## 🧭 维护状态

- 当前仓库是本项目的**最终历史版本**，原作者不再安排后续功能开发或日常维护。
- Issues 和 Pull Requests 不保证得到回复、审查或合并。
- 欢迎有能力的开发者 fork 后继续维护、适配新版本或探索新的交互方向。
- 继续维护者需要自行核对 Obsidian、Dataview、Homepage、Python 及其他环境兼容性。
- 公开分发、截图复用与衍生设计仍需遵守 AGPL-3.0、TALOS 品牌边界及相关第三方权利。

## 📄 License

代码以 **[AGPL-3.0](LICENSE)** 开源。

> 「TALOS」是外脑玩家 Haaper 的个人品牌名，本项目代码 AGPL-3.0 开源，但「TALOS」品牌名本身不随代码授权。你可以在自己的 vault 内自由使用，但对外公开分发或商业用途请改名。

## 👤 作者

**外脑玩家 Haaper** · AI 系统架构师 · 个人上下文主权布道者

- 公众号：**外脑玩家**（搜「外脑玩家」关注）
- X / Twitter：[@Haaper外脑玩家](https://x.com/Haaper外脑玩家)
- GitHub：[@Hanhan758](https://github.com/Hanhan758)
- 网站：待上线

---

<div align="center">

如果这张早期仪表盘启发了你，欢迎 star ⭐、分享、fork，并在自己的分支继续探索和维护。

</div>
