---
name: python-dev-standards
description: Python 开发规范与质量门槛。触发条件：写任何 Python 代码、审查/重构 Python 代码、创建 Python 项目、调用 subprocess/FFmpeg、用户说"按规范写"。
---

# python-dev-standards

## 触发时机

写任何 Python 代码时必须使用。

## 快速场景路由

| 场景 | 读这个 |
|------|--------|
| 写新代码 | `references/python-patterns.md` |
| 调用 FFmpeg | `references/ffmpeg-conventions.md` |
| 设计错误处理 | `references/error-design.md` |
| 参考完整示例 | `references/example-complete.md` |
| 提交前自审 | `references/quality-gate/review-checklist.md` |
| 代码质量问题 | `references/quality-gate/rewrite-signals.md` |
| 遇到模糊概念 | `references/quality-gate/ambiguity-answers.md` |

## 执行流程

1. 按场景读对应 reference
2. 写代码
3. 按 `review-checklist.md` 自审
4. 有歧义查 `ambiguity-answers.md`

## 核心原则

1. 宁可少写，不要乱写
2. 做一件事只有一种方法
3. 错误信息是代码的一部分
4. 边界条件是需求的一部分，不是"特殊处理"

## 快速判断：是否需要重写？

满足以下任一 → 推翻重来，不修补：
1. 同一类错误出现 2 次以上
2. 路径用字符串拼接
3. 正则表达式 ≥3 个
4. subprocess 没有 timeout
5. 错误信息没有具体值

详见 `references/quality-gate/rewrite-signals.md`

## 参考文档

| 文件 | 内容 |
|------|------|
| `references/python-patterns.md` | 命名、模块、路径、subprocess、typing |
| `references/ffmpeg-conventions.md` | FFmpeg 命令结构、seek、退出码、滤镜 |
| `references/error-design.md` | 异常类、异常链、错误信息 |
| `references/example-complete.md` | 综合所有规范的完整示例 |
| `references/quality-gate/review-checklist.md` | 提交前自审清单 |
| `references/quality-gate/rewrite-signals.md` | 触发重写的判断标准 |
| `references/quality-gate/ambiguity-answers.md` | 模糊概念的判断标准 |
