# Screenshots

本目录存放 README 顶部 Hero 图、各模块特写、动图 demo。首版开源可推空仓库占位，截图由作者补齐后第二次 commit。

## 需要的截图清单

| 文件名 | 内容 | 推荐规格 |
|---|---|---|
| `hero.png` | 首屏完整视图（Hero + 侧栏上半 + 今日焦点/Todo） | 2880×1800，PNG |
| `full-page.png` | 整页滚动截图（侧栏到底 + 主区所有模块） | 2880×4200 左右，PNG |
| `sidebar.png` | 侧栏特写：时钟/快捷入口/目标进度/上下文健康/待审批 | 1440×1800，PNG |
| `projects.png` | 活跃项目卡片网格（封面渐变 + 优先级 tag） | 2880×1200，PNG |
| `charts.png` | 知识库分布条形图 + 健康分趋势折线 | 2880×900，PNG |
| `commands.png` | 命令路由 + Memo 区 | 2880×800，PNG |
| `demo.gif` | 动图：入场动效（卡片上浮+数字滚动+进度条生长+折线描线）+ 悬停弹跳 + 金句切换 | 1920×1200，10–15s，GIF / MP4 |

## 拍摄建议

- 在 Obsidian 内打开首页，全屏（`Cmd/Ctrl+P` → "Toggle fullscreen"）。
- 关闭左侧文件树、右侧属性面板，让 iframe 占满窗口宽度。
- macOS：`Cmd+Shift+4` + 空格点击窗口，得到带阴影整窗截图。
- 动图：用 [ScreenToGif](https://www.screentogif.com/)（Win）或 [Kap](https://getkap.co/)（macOS）录制；先重开首页让动效从头播放。
- 导出前压一遍（[TinyPNG](https://tinypng.com/) / [Squoosh](https://squoosh.app/)），避免仓库膨胀。

## 在 README 中的引用方式

```markdown
![TALOS Dashboard](screenshots/hero.png)
![Projects Grid](screenshots/projects.png)
```

动图：

```markdown
![Demo](screenshots/demo.gif)
```
