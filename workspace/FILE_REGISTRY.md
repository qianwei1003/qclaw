# 文件配置总表

> 记录所有配置文件的详细信息：用途、位置、读取方、修改规则
> 最后更新：2026-03-26

---

## 🔴 系统注入文件（不可移动）

**路径固定在 `workspace/` 根目录，由 QClaw 应用硬编码注入到 System Prompt**

### SOUL.md - AI 人格定义

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/SOUL.md` |
| **用途** | 定义 AI 的人格、价值观、对话风格 |
| **读取方** | QClaw 应用 → System Prompt |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- 核心人格：批判性思维、行动导向、持续进化、主动服务
- 零废话原则
- 价值观：质量 > 速度、真相 > 顺从、透明 > 黑箱
- 不做的：不说废话、不隐瞒问题、不为错误辩护、不重复错误

---

### AGENTS.md - 工作规则

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/AGENTS.md` |
| **用途** | 定义 AI 的工作流程、规则、安全边界 |
| **读取方** | QClaw 应用 → System Prompt |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- Memory Bank 规则（项目文档）
- Python 开发规范
- 执行计划模式
- 代码审查规则（Diff First）
- 自我改进机制
- 安全边界（删除必须确认）

**引用的其他文件**：
- `memory/YYYY-MM-DD.md` - 每日日记
- `MEMORY.md` - 长期记忆
- `SELF_IMPROVEMENT.md` - 错误教训
- `DECISION_RULES.md` - 决策规则

⚠️ **注意**：AGENTS.md 引用的是 `memory/` 目录，不是 `workspace/knowledge/`

---

### USER.md - 用户画像

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/USER.md` |
| **用途** | 记录用户身份、偏好、工作流 |
| **读取方** | QClaw 应用 → System Prompt |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- 身份：资深工程师
- 沟通风格：极简主义、省略背景
- 代码审美：厌恶"屎山"代码、倾向重构
- 文档需求：重度依赖自动化（.doc/.xlsx）
- 安全意识：删除必须确认

---

### IDENTITY.md - 身份信息

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/IDENTITY.md` |
| **用途** | 定义 AI 的名称、定位、形象 |
| **读取方** | QClaw 应用 → System Prompt |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- 名称：DevCore（开发核心）
- 定位：首席技术合伙人 & 自动化专家
- 形象：冷静、高效、技术精湛、不讲情面但绝对可靠
- 座右铭：Code is truth, efficiency is law.

---

### HEARTBEAT.md - 定时任务

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/HEARTBEAT.md` |
| **用途** | 定义定期执行的任务 |
| **读取方** | QClaw 应用 → System Prompt（AI 主动执行） |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- 每日任务：搜 AI 新技术、检查 memory
- 触发规则：早/午/晚巡检，夜间安静

**引用的文件**：
- `memory/YYYY-MM-DD.md` - 写入日记
- `MEMORY.md` - 提炼内容

---

### TOOLS.md - 工具配置

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/TOOLS.md` |
| **用途** | 定义工具使用规则、环境配置 |
| **读取方** | QClaw 应用 → System Prompt |
| **修改后** | 重启 QClaw 生效 |
| **能否移动** | ❌ 绝对不能 |

**内容摘要**：
- 文件搜索原则：先问位置、限制深度
- 搜索优先级：当前目录 → 桌面 → 下载 → 主目录
- 环境：Workspace 路径、Gateway 端口

---

## 🟡 记忆系统文件

### MEMORY.md - 记忆总览

| 属性 | 值 |
|------|-----|
| **路径** | `.qclaw/memory/MEMORY.md` |
| **用途** | 记忆索引、分类汇总 |
| **读取方** | AI 通过 `read` 工具读取 |
| **修改后** | 即时生效 |
| **能否移动** | ⚠️ 可以，但需同步 AGENTS.md |

**内容结构**：
- 记忆统计
- 分类索引：decision / preference / pattern / causality
- 记录模板
- 维护规则

---

### causality/*.md - 日常记录

| 属性 | 值 |
|------|-----|
| **路径** | `.qclaw/memory/causality/YYYY-MM-DD.md` |
| **用途** | 日常记录、工作日志 |
| **读取方** | AI 通过 `read` 工具读取 |
| **修改后** | 即时生效 |
| **能否移动** | ✅ 可以 |

**格式**：
```markdown
---
date: YYYY-MM-DD
category: causality
importance: 0.3-0.6
tags: []
---
```

---

## 🟢 知识库文件

### SELF_IMPROVEMENT.md - 自我改进记录

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/knowledge/SELF_IMPROVEMENT.md` |
| **AGENTS.md 引用** | `SELF_IMPROVEMENT.md`（无路径前缀） |
| **用途** | 记录失败、错误、改进方案 |
| **读取方** | AI 通过 `read` 工具读取 |
| **修改后** | 即时生效 |
| **能否移动** | ⚠️ 可以，但 AGENTS.md 引用的是根目录 |

⚠️ **问题**：AGENTS.md 引用的是 `SELF_IMPROVEMENT.md`（根目录），但实际在 `knowledge/` 下

---

### DECISION_RULES.md - 决策规则库

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/knowledge/DECISION_RULES.md` |
| **AGENTS.md 引用** | `DECISION_RULES.md`（无路径前缀） |
| **用途** | 决策规则、处理方式 |
| **读取方** | AI 通过 `read` 工具读取 |
| **修改后** | 即时生效 |
| **能否移动** | ⚠️ 可以，但 AGENTS.md 引用的是根目录 |

⚠️ **问题**：同上，AGENTS.md 引用的是根目录

---

## 🔵 配置文件

### openclaw.json - 主配置

| 属性 | 值 |
|------|-----|
| **路径** | `.qclaw/openclaw.json` |
| **用途** | 模型、渠道、Skills、插件配置 |
| **读取方** | OpenClaw Gateway |
| **修改后** | 需重启 Gateway |
| **能否移动** | ❌ 绝对不能 |

**关键字段**：
- `models` - 模型配置
- `skills.load.extraDirs` - Skills 加载路径
- `channels` - 渠道配置（微信等）
- `plugins` - 插件配置

---

### CONFIG_MAP.md - 配置影响地图

| 属性 | 值 |
|------|-----|
| **路径** | `workspace/CONFIG_MAP.md` |
| **用途** | 记录配置文件的影响关系 |
| **读取方** | AI / 用户参考 |
| **修改后** | 即时生效 |
| **能否移动** | ✅ 可以 |

---

## ⚠️ 路径不一致问题

### AGENTS.md 引用 vs 实际位置

| AGENTS.md 引用 | 实际位置 | 问题 |
|---------------|----------|------|
| `memory/YYYY-MM-DD.md` | `.qclaw/memory/causality/` | 路径不匹配 |
| `MEMORY.md` | `.qclaw/memory/MEMORY.md` | 路径不匹配 |
| `SELF_IMPROVEMENT.md` | `workspace/knowledge/` | 路径不匹配 |
| `DECISION_RULES.md` | `workspace/knowledge/` | 路径不匹配 |

### 解决方案

**方案 A**：把文件移到 AGENTS.md 引用的位置
- `MEMORY.md` → `workspace/MEMORY.md`
- `SELF_IMPROVEMENT.md` → `workspace/SELF_IMPROVEMENT.md`
- `DECISION_RULES.md` → `workspace/DECISION_RULES.md`

**方案 B**：修改 AGENTS.md 的引用路径
- 更新为正确的相对路径

---

## 📝 修改检查清单

修改任何文件前：

1. **是系统注入文件吗？**
   - 是 → 不能移动，修改后重启

2. **AGENTS.md 有引用吗？**
   - 有 → 移动后需同步更新 AGENTS.md

3. **是 openclaw.json 吗？**
   - 是 → 修改后重启 Gateway

4. **路径在 extraDirs 里吗？**
   - 是 → Skills 需要在 extraDirs 配置的目录下

---

## 🔧 快速定位

| 想改什么 | 去哪里 | 注意事项 |
|---------|--------|---------|
| AI 人格 | `workspace/SOUL.md` | 重启生效 |
| AI 规则 | `workspace/AGENTS.md` | 重启生效 |
| 用户画像 | `workspace/USER.md` | 重启生效 |
| 记忆总览 | `.qclaw/memory/MEMORY.md` | 即时生效 |
| 每日日记 | `.qclaw/memory/causality/` | 即时生效 |
| 错误教训 | `workspace/knowledge/SELF_IMPROVEMENT.md` | 即时生效 |
| 决策规则 | `workspace/knowledge/DECISION_RULES.md` | 即时生效 |
| Skills 路径 | `openclaw.json` → `extraDirs` | 重启生效 |
