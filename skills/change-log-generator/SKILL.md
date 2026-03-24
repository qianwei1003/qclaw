---
name: "change-log-generator"
description: "生成改动档案（Markdown）：读取当前分支与 git diff（基线可选），输出改动文件、行号范围、commit 摘要与占位的测试要点与建议项。用在需要把一次开发/修复的改动记录成可检索文档时。"
---

技能：生成改动档案（change-log）

用途
- 当需要把当前分支/commit-range 的改动整理为一份可检索的“改动档案”时使用。
- Skill 会读取 git 仓库信息、commit log 与 diff，生成 docs/change-logs/*.md（默认），并在控制台输出摘要路径。

触发条件
- 使用者请求“生成改动档案”或需要将一次改动写成可追溯文档。

主要资源
- scripts/gen_change_log.py — 生成脚本（Python）
- README.md — 使用说明示例

注意
- 本 skill 仅生成文件，不自动提交或修改代码。
- 默认基线为 origin/main（可通过 --base 覆盖）。