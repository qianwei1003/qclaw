改动档案（change-logs）目录

用途
- 存放由 gen_change_log.py 生成的改动档案（Markdown），用于长期检索与问题回溯。

文件命名
- {task-or-branch}-{YYYYMMDDTHHMMSS}.md
  例：ZD#1234-20260324T152300.md 或 feature/add-search-20260324T152300.md

模板（示例）
请参考生成文件头，补充以下内容：
- 改动原因（必须）
- 关联任务 / Issue / 禅道号（可选）
- 改动文件（类型 / 路径 / 行号范围）
- 测试要点
- 被检测但跳过的建议（记录但不自动修改）

检索
- 可使用 VSCode 全局搜索或 ripgrep 搜索关键词或任务号：
  rg "ZD#1234" docs/change-logs

手动提交建议
- 生成改动档案后请手动 review 并提交到仓库以便长期保存。