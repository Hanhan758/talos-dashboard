# 部署手册

把 TALOS Dashboard 接入你自己的 Obsidian vault。全程离线、零外部依赖，预计 5–10 分钟。

---

## 1. 先决条件

- **Obsidian 桌面版**（macOS / Windows / Linux，1.5+）
- 两个社区插件：
  - **Dataview**（且开启 *Enable JavaScript Queries* 与 *Enable Inline JavaScript Queries*）
  - **Homepage** by novov

如果还没装，在 Obsidian 里 `设置 → 第三方插件 → 浏览` 搜索安装即可。

---

## 2. 五步部署

> `<VAULT>` 表示你的 vault 根目录绝对路径。

### Step 1 · 放置 3 个文件

把仓库里的核心文件复制进 vault：

```bash
cp dashboard.html              <VAULT>/dashboard.html
cp homepage.md                 <VAULT>/homepage.md
cp talos-dashboard-home.css    <VAULT>/.obsidian/snippets/talos-dashboard-home.css
```

> `dashboard.html` 和 `homepage.md` 放在 vault 根目录最省事；想放别处（如 `dashboard/`）也行，但下一步路径必须对得上。
>
> `.obsidian/snippets/` 目录不存在就 `mkdir -p` 创建。

### Step 2 · 安装插件

确保 `Dataview` 与 `Homepage` 已安装并启用。

### Step 3 · 编辑 4 个 JSON（改前先备份）

**① `<VAULT>/.obsidian/community-plugins.json`** — 确保数组里包含这两项：

```json
["dataview", "homepage"]
```

**② `<VAULT>/.obsidian/plugins/dataview/data.json`** — 开启 JS 查询（文件不存在就新建）：

```json
{
  "enableDataviewJs": true,
  "enableInlineDataviewJs": true,
  "prettyRenderInlineFields": true
}
```

**③ `<VAULT>/.obsidian/plugins/homepage/data.json`** — 设为开机首页、阅读视图：

```json
{
  "version": 4,
  "homepages": {
    "Main Homepage": {
      "value": "homepage",
      "kind": "File",
      "openOnStartup": true,
      "openMode": "Replace all open notes",
      "manualOpenMode": "Keep open notes",
      "view": "Reading view",
      "revertView": true,
      "openWhenEmpty": false,
      "refreshDataview": false,
      "autoCreate": false,
      "pin": false,
      "commands": [],
      "alwaysApply": false,
      "hideReleaseNotes": false
    }
  },
  "separateMobile": false
}
```

> 如果你把首页笔记改名了（比如叫 `首页.md`），把 `"value": "homepage"` 同步改掉，**不含 `.md`**。

**④ `<VAULT>/.obsidian/appearance.json`** — 启用 CSS 片段（保留其它已有项）：

```json
{ "enabledCssSnippets": ["talos-dashboard-home"] }
```

### Step 4 · 重启 Obsidian

**完全退出（macOS: `Cmd+Q` / Windows/Linux: `Ctrl+Q`）后重新打开**。若插件配置是运行中改的，退出时会被回写，故必须完全重启。

开机应直接进入控制台首页。

### Step 5 · 自检

| 检查项 | 期望状态 |
|---|---|
| 开机自动进入仪表盘 | ✓ |
| Hero / 极光背景 / 卡片入场动效 | ✓ |
| 时钟、周历、倒计时动态刷新 | ✓ |
| 点项目卡 → 跳转到对应笔记 | ✓ |
| 命令路由点击 → 复制斜杠命令到剪贴板 | ✓ |
| Todo / Memo 关掉重开内容还在 | ✓ |

---

## 3. 刷新数据

开源版默认 STATS 块是示例数据。要换成你 vault 的真实统计：

```bash
python3 refresh-dashboard.py --vault <VAULT>
```

如果默认扫描规则不匹配你的 vault 结构（绝大多数 vault 都不会完全匹配），编辑 `refresh-dashboard.py` 顶部的「配置区」即可，详见 [CUSTOMIZE.md](CUSTOMIZE.md#4-自定义扫描规则)。

**建议用 crontab / launchd / Task Scheduler 定时跑**（比如每天早上一次），让数字保持新鲜。

---

## 4. 故障排查

| 现象 | 原因 | 处理 |
|---|---|---|
| 首页空白 | Dataview JS 未开 | `设置 → Dataview` 打开 *Enable JavaScript Queries* 后重开首页 |
| 显示出笔记标题和「属性」面板、正文被压窄 | CSS 片段没生效 | `设置 → 外观 → CSS 片段` → 重新加载并打开 `talos-dashboard-home` |
| 开机没自动进首页 | Homepage 未启用 / `openOnStartup` 关 | 确认插件启用、`homepage/data.json` 里 `openOnStartup: true`；命令面板运行 `Homepage: Open homepage` 验证 |
| 点卡片没反应 | `openWithDefaultApp` 不存在 / 指向了文件夹 | 改 `data-path` 指向具体 `.md`；或把 `.html` 分支降级为 `openLinkText` |
| 卡片打开报「找不到」 | 路径写错或该笔记不存在 | 校对 `data-path` 与 vault 实际路径（注意全角冒号 `：`） |
| 数字始终是 0 | `refresh-dashboard.py` 没跑或扫描配置不对 | 重跑脚本，检查 `vault` 参数；改 `CONTENT_DIRS` 等配置 |
| 健康分折线没画出来 | `health-log.md` 不存在或没有 `EVAL_HISTORY` 注释块 | 要么按 `parse_health()` 的格式补一个，要么把图表区移除 |

---

## 5. 升级

TALOS Dashboard 还在迭代，未来发布新版时：

1. 备份你的 `dashboard.html`（你已经做的自定义都在这里）。
2. 用新版的 `dashboard.html` / `refresh-dashboard.py` 覆盖。
3. 把你的自定义改动（项目卡、命令路由、配色等）重新合并进去——建议用 Git diff 或 VS Code 比对。
4. 重跑 `refresh-dashboard.py`。

> 升级前看一眼 [CHANGELOG.md](../CHANGELOG.md)，确认有没有破坏性改动。
