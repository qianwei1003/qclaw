change-log-generator

Purpose
- 生成改动档案 Markdown，记录一次功能/修复的改动范围、commit 摘要与占位的测试要点，便于后续检索与回溯。

Quick start
1. 在仓库根目录运行（确保已安装 git）：
   python skills/change-log-generator/scripts/gen_change_log.py

2. 指定基线与任务号（可选）：
   python skills/change-log-generator/scripts/gen_change_log.py --base origin/main --task ZD#1234

3. 生成文件位于：docs/change-logs/<branch-or-task>-YYYYMMDDTHHMMSS.md

Notes
- 脚本只生成文件，不会自动提交或修改代码。
- 若想在提交时自动生成，可把脚本调用放入 git hook（例如 pre-push 或 post-commit），示例见下。

Example git hook (示例，仅供参考，不自动安装)：
  #!/bin/sh
  python skills/change-log-generator/scripts/gen_change_log.py --base origin/main --task ZD#1234