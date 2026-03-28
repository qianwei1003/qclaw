# 当前上下文

## 当前焦点
V4 设计：Pipeline 执行引擎重构

核心问题：Executor 从"命令路由器"变成"Pipeline 执行引擎"

## 最近变更
- 2026-03-28：发现 memory-bank 是项目专用文档系统，不应删除
- 2026-03-28：更新 V4 架构设计（Pipeline + Planner）

## 下一步
1. V4 Step 1：设计 Pipeline 架构
2. V4 Step 2：实现 PipelineExecutor 类

## 待定决策
- Pipeline 决策层：规则引擎 vs LLM？

## 当前阻塞
无。

## 重要教训
⚠️ memory-bank 是项目专用文档系统，不能随便删除！
详见 workspace/SELF_IMPROVEMENT.md

## memory-bank 文档索引

| 文件 | 内容 |
|------|------|
| `projectbrief.md` | 项目目标、范围、成功标准 |
| `productContext.md` | 用户问题、目标用户、设计目标 |
| `techContext.md` | 技术栈，开发环境、约束 |
| `progress.md` | V1-V4 路线图、里程碑 |
| `systemPatterns.md` | 架构图、模块职责、数据流 |
| `activeContext.md` | 当前焦点、最近变更、下一步 |
| `aiContext.md` | AI 如何使用本工具 |
| `api-reference.md` | 完整操作参数表、返回值结构 |
| `design-decisions.md` | 架构设计、核心决策 |
| `error-handling.md` | 错误处理规范 |
| `test-strategy.md` | 测试策略 |
