#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
refresh-dashboard.py — TALOS 控制台数据刷新脚本（开源版）

扫描你的 Obsidian vault，把真实统计写进同目录 dashboard.html 的 STATS 块
（/*STATS:START*/ ... /*STATS:END*/），让仪表盘数字不再过时。

统计口径（默认）：
- 知识笔记 = CONTENT_DIRS 配置的目录下 .md 文件数（排除以 `_` 开头的内部文件 / EXCLUDE 路径片段）。
- 收件箱 / 待审批 / 偏好候选 / 健康分趋势 / 今日焦点
  分别从 INBOX_DIR / APPROVALS_FILE / CANDIDATES_FILE / HEALTH_FILE / TASKS_FILE 读取。

如果你的 vault 结构与默认不一致（绝大多数都不一致），改下方「=== 配置区 ===」即可，不必改逻辑。

用法：
    python3 refresh-dashboard.py                  # 自动推断 vault（取本脚本父目录的上一级）
    python3 refresh-dashboard.py --vault /path    # 显式指定 vault 路径
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Iterable


# ==================== 配置区（按需修改） ====================

# 默认 vault 路径：本脚本放在 talos-dashboard/ 内，假设 vault 是它的父目录。
# 如果你的 vault 在别处，用 `--vault /path/to/vault` 覆盖。
DEFAULT_VAULT = Path(__file__).resolve().parents[1]

# dashboard.html 路径（本脚本同目录）。
DASHBOARD = Path(__file__).resolve().parent / "dashboard.html"

# 六大内容目录：显示名 -> 目录相对路径（用于知识库分布条形图 + 点击跳转）。
# 这是示例配置——改成你自己的 vault 目录结构。路径相对 vault 根。
# 显示名会出现在仪表盘上，可中文可英文；建议短而清晰。
CONTENT_DIRS: list[tuple[str, str]] = [
    ("Projects",  "projects"),
    ("Materials", "materials"),
    ("Insights",  "insights"),
    ("Archive",   "archive"),
    ("Journal",   "journal"),
    ("Inbox",     "inbox"),
]

# 计数时排除的路径片段（相对 vault 路径里出现的子串）。
EXCLUDE: tuple[str, ...] = (
    "/node_modules/",
    "/.git/",
    "/.obsidian/",
    "/.trash/",
)

# 收件箱目录的显示名（从 CONTENT_DIRS 中匹配此标签的目录单独算作 inbox 计数）。
INBOX_LABEL = "Inbox"

# 以下三项是「按 ## 标题区统计条目数」的文件 + 关键字。
# 如果你的 vault 没有这些文件，对应字段会返回 0，仪表盘对应位置显示 0。
CANDIDATES_FILE = "System/working-memory/candidates.md"
CANDIDATES_HEADER = "待确认"

APPROVALS_FILE = "System/pending-approvals.md"
APPROVALS_HEADER = "当前待审批"

# 健康分趋势从 health-log.md 的 EVAL_HISTORY 注释块读取。
HEALTH_FILE = "System/working-memory/health-log.md"

# 今日焦点从 tasks.md 的「## 焦点」区读取，匹配 `- 🔴/🟡/🟢 **标题** — 描述` 格式。
TASKS_FILE = "System/working-memory/tasks.md"
TASKS_FOCUS_HEADER = "焦点"
TASKS_FOCUS_LIMIT = 3

# ==================== 配置区结束 ====================


def count_md(vault: Path, rel_dir: str) -> int:
    """统计目录下 .md 数量。
    排除：以 `_` 开头的内部文件（如 `_README.md`、`_template.md`）+ EXCLUDE 命中的路径。
    如需更改排除规则，改 EXCLUDE 或在此函数里调整。
    """
    base = vault / rel_dir
    if not base.exists():
        return 0
    n = 0
    for p in base.rglob("*.md"):
        if p.name.startswith("_"):
            continue
        sp = "/" + str(p.relative_to(vault)).replace("\\", "/")
        if any(x in sp for x in EXCLUDE):
            continue
        n += 1
    return n


def count_section_items(vault: Path, file_rel: str, header_kw: str) -> int:
    """统计某 ## 标题区到下一个 ## 之间的条目数（- 开头），「（无）/（空）」记 0。"""
    f = vault / file_rel
    if not f.exists():
        return 0
    lines = f.read_text(encoding="utf-8").splitlines()
    inside, count = False, 0
    for ln in lines:
        if ln.startswith("## "):
            inside = header_kw in ln
            continue
        if not inside:
            continue
        s = ln.strip()
        if s.startswith("- ") and "（无）" not in s and "（空）" not in s:
            count += 1
    return count


def parse_health(vault: Path, n: int = 9) -> list[list]:
    """从 health-log.md 的 EVAL_HISTORY 取最近 n 次 [日期标签, 分数]。"""
    f = vault / HEALTH_FILE
    if not f.exists():
        return []
    text = f.read_text(encoding="utf-8")
    m = re.search(
        r"<!-- EVAL_HISTORY -->(.*?)<!-- EVAL_HISTORY_END -->", text, re.S
    )
    if not m:
        return []
    out: list[list] = []
    for row in m.group(1).splitlines():
        cells = [c.strip() for c in row.split("|") if c.strip()]
        if len(cells) < 2:
            continue
        dm = re.search(r"(\d{4})-(\d{2})-(\d{2})", cells[0])
        if not dm:
            continue
        try:
            score = int(cells[1])
        except ValueError:
            continue
        label = f"{int(dm.group(2))}/{int(dm.group(3))}"
        out.append([label, score])
    return out[-n:]


def parse_focus(vault: Path, n: int = 3) -> list[list]:
    """从 tasks.md 的「## 焦点」区取前 n 条 [level, title, desc]。"""
    f = vault / TASKS_FILE
    if not f.exists():
        return []
    lines = f.read_text(encoding="utf-8").splitlines()
    inside, out = False, []
    for ln in lines:
        if ln.startswith("## "):
            inside = TASKS_FOCUS_HEADER in ln
            continue
        if not inside:
            continue
        s = ln.strip()
        m = re.match(r"-\s*(🔴|🟡|🟢)?\s*\*\*(.+?)\*\*\s*[—-]+\s*(.*)$", s)
        if not m:
            continue
        emoji = m.group(1) or ""
        level = "hot" if emoji == "🔴" else "warn"
        title = m.group(2).strip()
        desc = m.group(3).strip()
        if len(desc) > 90:
            desc = desc[:88].rstrip() + "…"
        out.append([level, title, desc])
        if len(out) >= n:
            break
    return out


def build_stats(vault: Path) -> dict:
    """扫描 vault，组装 STATS 字典。"""
    vault_dist: list[list] = []
    for name, rel in CONTENT_DIRS:
        # 第三项是点击该目录条形图时跳转到的笔记路径（vault 相对路径）。
        # 默认指向该目录下的 index.md（如果不存在，Obsidian 点击时会报「找不到」，自行改成你的入口笔记）。
        vault_dist.append([name, count_md(vault, rel), f"{rel}/index.md"])
    total = sum(v[1] for v in vault_dist)
    inbox = next((v[1] for v in vault_dist if v[0] == INBOX_LABEL), 0)

    return {
        "generatedAt": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "totalNotes": total,
        "inbox": inbox,
        "candidates": count_section_items(vault, CANDIDATES_FILE, CANDIDATES_HEADER),
        "approvals": count_section_items(vault, APPROVALS_FILE, APPROVALS_HEADER),
        "vault": vault_dist,
        "health": parse_health(vault, 9),
        "focus": parse_focus(vault, TASKS_FOCUS_LIMIT),
    }


def render_block(stats: dict) -> str:
    """把 STATS 字典渲染为带标记的 JS 代码块。"""
    return (
        "/*STATS:START*/\n"
        "/* 由 refresh-dashboard.py 自动生成，请勿手改。"
        f"最后更新：{stats['generatedAt']} */\n"
        "const STATS = "
        + json.dumps(stats, ensure_ascii=False, indent=2)
        + ";\n"
        "/*STATS:END*/"
    )


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="刷新 dashboard.html 的 STATS 块。")
    parser.add_argument(
        "--vault",
        type=Path,
        default=DEFAULT_VAULT,
        help=f"Obsidian vault 根目录路径（默认：{DEFAULT_VAULT}）",
    )
    parser.add_argument(
        "--dashboard",
        type=Path,
        default=DASHBOARD,
        help=f"dashboard.html 路径（默认：{DASHBOARD}）",
    )
    args = parser.parse_args(list(argv) if argv is not None else None)

    vault: Path = args.vault.resolve()
    dashboard: Path = args.dashboard.resolve()

    if not dashboard.exists():
        print(f"✗ 找不到 dashboard.html：{dashboard}", file=sys.stderr)
        return 1
    if not vault.exists():
        print(f"✗ 找不到 vault 目录：{vault}", file=sys.stderr)
        return 1

    stats = build_stats(vault)
    block = render_block(stats)

    html = dashboard.read_text(encoding="utf-8")
    if "/*STATS:START*/" not in html:
        print(
            "✗ dashboard.html 中未找到 /*STATS:START*/ 标记，无法写入。",
            file=sys.stderr,
        )
        return 1
    html = re.sub(
        r"/\*STATS:START\*/.*?/\*STATS:END\*/",
        lambda _: block,
        html,
        flags=re.S,
    )
    dashboard.write_text(html, encoding="utf-8")

    print(f"✓ 已刷新 {dashboard.name} @ {stats['generatedAt']}")
    print(
        f"  vault = {vault}\n"
        f"  知识笔记 {stats['totalNotes']} · 收件箱 {stats['inbox']} "
        f"· 待审批 {stats['approvals']} · 偏好候选 {stats['candidates']}"
    )
    print(
        "  分布 "
        + " ".join(f"{n}:{c}" for n, c, _ in stats["vault"])
    )
    print(
        f"  健康分 {len(stats['health'])} 点 · 焦点 {len(stats['focus'])} 条"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
