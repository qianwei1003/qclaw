# 配置影响地图

> 记录每个配置文件的用途、读取方、修改后的生效方式
> 最后更新：2026-03-26

---

## 🔴 系统注入文件（硬编码路径）

**修改后需重启 QClaw 生效**

| 文件 | 路径 | 用途 | 读取方 | 修改影响 |
|------|------|------|--------|----------|
| AGENTS.md | `workspace/AGENTS.md` | AI 工作规则 | System Prompt | 改后立即生效（重启后） |
| SOUL.md | `workspace/SOUL.md` | AI 人格定义 | System Prompt | 改后立即生效（重启后） |
| USER.md | `workspace/USER.md` | 用户档案 | System Prompt | 改后立即生效（重启后） |
| IDENTITY.md | `workspace/IDENTITY.md` | 身份信息 | System Prompt | 改后立即生效（重启后） |
| HEARTBEAT.md | `workspace/HEARTBEAT.md` | 定时任务定义 | System Prompt | 改后立即生效（重启后） |
| TOOLS.md | `workspace/TOOLS.md` | 工具配置 | System Prompt | 改后立即生效（重启后） |

⚠️ **关键**：这些路径是 **硬编码** 在 QClaw 应用里的，**不能移动**

---

## 🟡 OpenClaw 配置文件

**修改后需重启 Gateway 生效**

| 文件 | 路径 | 用途 | 读取方 | 修改影响 |
|------|------|------|--------|----------|
| openclaw.json | `.qclaw/openclaw.json` | 主配置（模型、渠道、Skills） | OpenClaw Gateway | 需重启 |
| qclaw.json | `.qclaw/qclaw.json` | CLI 状态 | QClaw CLI | 自动生成，勿改 |

### openclaw.json 关键字段

```json
{
  "models": {},           // ← 改模型配置
  "skills": {
    "load": {
      "extraDirs": []     // ← 改 Skills 加载路径
    }
  },
  "channels": {},         // ← 改渠道配置（微信等）
  "gateway": {}           // ← 改网关端口等
}
```

---

## 🟢 AI 读取文件（动态加载）

**修改后即时生效（下次对话）**

| 文件/目录 | 路径 | 用途 | 读取方式 | 修改影响 |
|-----------|------|------|----------|----------|
| MEMORY.md | `memory/MEMORY.md` | 记忆总览 | `read` 工具 | 即时 |
| 每日日记 | `memory/causality/*.md` | 日常记录 | `read` 工具 | 即时 |
| Skills | `workspace/skills/*/` | 自定义 Skills | `skill` 触发 | 即时 |
| 知识库 | `workspace/knowledge/*.md` | 决策规则等 | `read` 工具 | 即时 |

---

## 🔵 项目文件（按需读取）

| 文件 | 路径 | 用途 | 读取时机 |
|------|------|------|----------|
| README.md | `workspace/README.md` | 导航 | 用户询问时 |
| PROJECT_INDEX.md | `workspace/PROJECT_INDEX.md` | 项目索引 | 用户询问时 |
| 项目文档 | `workspace/*/README.md` | 项目说明 | 涉及项目时 |

---

## ⚠️ 常见错误

### 错误 1：移动系统注入文件
```
❌ 把 AGENTS.md 移到 core/AGENTS.md
✅ 必须保持在 workspace/AGENTS.md
```

### 错误 2：改完配置没重启
```
❌ 改 openclaw.json → 期望立即生效
✅ 改完必须重启 QClaw
```

### 错误 3：Skills 路径没加 extraDirs
```
❌ 创建 workspace/skills/new-skill/
✅ 还要在 openclaw.json 的 extraDirs 里添加路径
```

---

## 📝 修改检查清单

修改任何文件前，问自己：

1. **这是系统注入文件吗？** → 不能移动位置
2. **改完需要重启吗？** → openclaw.json 需要
3. **路径配置同步了吗？** → Skills 要加 extraDirs
4. **AI 能读到吗？** → 确认在正确目录

---

## 🔧 快速诊断

### 检查 System Prompt 注入
```
看对话开头的 "Project Context" 部分
确认文件是否出现在 "The following project context files have been loaded"
```

### 检查 Skills 加载
```bash
# 看 openclaw.json 的 extraDirs
gateway config.get skills.load.extraDirs
```

### 检查文件可读
```
直接用 read 工具读文件，确认路径正确
```
