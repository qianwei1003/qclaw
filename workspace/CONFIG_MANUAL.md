# 完整配置文件手册

> 所有重要配置文件的用途、位置、格式、联动关系
> 最后更新：2026-03-26

---

## 🔴 系统注入文件（绝对不能移动）

| 文件 | 路径 | 用途 | 格式 | 联动 |
|------|------|------|------|------|
| **AGENTS.md** | `workspace/AGENTS.md` | AI工作规则 | Markdown | 引用SELF_IMPROVEMENT, DECISION_RULES, PLAN_TEMPLATE |
| **SOUL.md** | `workspace/SOUL.md` | AI人格定义 | Markdown | 独立 |
| **USER.md** | `workspace/USER.md` | 用户画像 | Markdown | 独立 |
| **IDENTITY.md** | `workspace/IDENTITY.md` | AI身份信息 | Markdown | 独立 |
| **HEARTBEAT.md** | `workspace/HEARTBEAT.md` | 定时任务定义 | Markdown | 需配合cron配置 |
| **TOOLS.md** | `workspace/TOOLS.md` | 工具配置 | Markdown | 独立 |

**修改后**：必须重启QClaw生效

---

## 🟡 OpenClaw主配置（绝对不能移动）

| 文件 | 路径 | 用途 | 关键字段 |
|------|------|------|----------|
| **openclaw.json** | `.qclaw/openclaw.json` | 主配置 | models, skills.load.extraDirs, channels, gateway |
| **qclaw.json** | `.qclaw/qclaw.json` | CLI状态 | 自动生成 |

**修改后**：重启Gateway生效

**关键联动**：
- 改`skills.load.extraDirs` → Skills加载路径
- 改`channels` → 消息渠道配置
- 改`models` → AI模型配置

---

## 🟢 记忆系统文件（可调整）

| 文件 | 路径 | 用途 | 格式 | 读取方式 |
|------|------|------|------|----------|
| **MEMORY.md** | `memory/MEMORY.md` | 记忆总览索引 | Markdown表格 | read工具 |
| **每日日记** | `memory/causality/YYYY-MM-DD.md` | 日常记录 | Markdown+YAML头 | read工具 |
| **SELF_IMPROVEMENT** | `workspace/knowledge/SELF_IMPROVEMENT.md` | 错误记录 | Markdown模板 | read工具 |
| **DECISION_RULES** | `workspace/knowledge/DECISION_RULES.md` | 决策规则 | Markdown表格 | read工具 |

**新日记格式**：
```markdown
---
date: YYYY-MM-DD
category: [decision|preference|pattern|causality]
importance: 0.0-1.0
tags: []
---
```

---

## 🔵 工作区导航文件（可调整）

| 文件 | 路径 | 用途 |
|------|------|------|
| **README.md** | `workspace/README.md` | workspace导航 |
| **CONFIG_MAP.md** | `workspace/CONFIG_MAP.md` | 配置影响地图 |
| **PROJECT_INDEX.md** | `workspace/PROJECT_INDEX.md` | 项目索引 |

---

## ⚠️ 关键结论

### 绝对不能移动的文件
```
workspace/
├── AGENTS.md      ← 系统注入
├── SOUL.md        ← 系统注入
├── USER.md        ← 系统注入
├── IDENTITY.md    ← 系统注入
├── HEARTBEAT.md   ← 系统注入
└── TOOLS.md       ← 系统注入

.qclaw/
├── openclaw.json  ← 主配置
└── qclaw.json     ← CLI状态
```

### 修改后需要重启的
1. **openclaw.json** → 重启Gateway
2. **系统注入md文件** → 重启QClaw应用

### 修改后立即生效的
- memory/下的文件
- workspace/knowledge/下的文件
- workspace/skills/下的文件（需已在extraDirs中）

### 常见错误
- ❌ 移动AGENTS.md到core/AGENTS.md
- ❌ 改openclaw.json不重启
- ❌ 新建Skills目录不加到extraDirs
