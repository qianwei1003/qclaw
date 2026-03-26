# .qclaw 目录导航

> 最后更新：2026-03-26

这是 QClaw / OpenClaw 的状态目录，存放配置、运行时数据和你的工作文件。

---

## 📂 目录结构

### 系统运行时（自动生成，勿手动修改）

| 目录 | 用途 |
|------|------|
| `agents/` | 各角色会话数据 |
| `browser/` | 浏览器缓存（openclaw profile） |
| `canvas/` | Canvas 功能数据 |
| `cron/` | 定时任务配置 |
| `devices/` | 已配对设备信息 |
| `features/` | 功能模块数据 |
| `identity/` | 设备身份信息 |
| `logs/` | 运行日志 |
| `memory/` | 系统记忆（SQLite + 每日日记） |
| `plugins/` | 插件运行数据 |
| `qmemory/` | QClaw 记忆系统 |
| `subagents/` | 子代理运行数据 |
| `tools/` | 工具数据（如 GitHub MCP） |
| `weixin/` | 微信账号数据 |

### 核心配置文件

| 文件 | 用途 |
|------|------|
| `openclaw.json` | **主配置文件** — 模型、渠道、插件等 |
| `qclaw.json` | CLI 状态（端口、PID 等） |
| `clinerules.md` | Cline 规则（保留） |
| `.clineignore` | Cline 忽略规则（保留） |

### 安装的 Skills

| 目录 | 用途 |
|------|------|
| `skills/` | 从 ClawHub 安装的 Skills |

### 你的工作区 ⭐

| 目录 | 用途 |
|------|------|
| `workspace/` | **你的工作区** — 项目、配置、档案 |

---

## 📁 workspace/ 工作区详解

```
workspace/
├── SOUL.md              # AI 人格定义
├── AGENTS.md            # AI 工作规则
├── USER.md              # 你的档案
├── HEARTBEAT.md         # 定时任务定义
├── DECISION_RULES.md    # 决策规则库
├── SELF_IMPROVEMENT.md  # 自我改进记录
├── PROJECT_INDEX.md     # 项目索引
├── PLAN_TEMPLATE.md     # 计划模板
├── FILE_MANAGEMENT.md   # 文件管理规范
├── KNOWLEDGE_GRAPH.md   # 知识图谱
├── EVOLUTION_ROADMAP.md # 进化路线图
│
├── skills/              # Skills 目录
│   ├── custom/          # 你自己写的 Skills
│   │   ├── code-reviewer/
│   │   ├── explain-code/
│   │   ├── project-manager/
│   │   ├── task-dispatcher/
│   │   └── web-crawler-doc/
│   │
│   └── third-party/     # 从 ClawHub 安装的
│       ├── searching-assistant/
│       └── writing-assistant/
│
├── archive/             # 归档
│   └── cline/           # Cline 配置归档
│
└── [项目目录]/          # 你的实际项目
    ├── ai-video-editor/
    ├── video-downloader/
    └── ...
```

---

## 🔧 常用操作

### 查看配置
```bash
# 查看 openclaw.json
cat C:\Users\admin\.qclaw\openclaw.json
```

### 清理日志
```bash
# 清理日志目录
rm -r C:\Users\admin\.qclaw\logs\*
```

### 备份配置
```bash
# 备份主配置
cp C:\Users\admin\.qclaw\openclaw.json C:\Users\admin\.qclaw\openclaw.json.backup
```

---

## ⚠️ 注意事项

1. **不要删除** `openclaw.json`、`qclaw.json` — 系统无法运行
2. **不要删除** `agents/`、`devices/`、`plugins/` — 会丢失数据
3. **可以清理** `logs/`、`backups/` — 不影响运行
4. **工作文件放** `workspace/` — 不要放在 `.qclaw` 根目录

---

## 📞 相关链接

- OpenClaw 文档：`C:\Program Files\QClaw\resources\openclaw\node_modules\openclaw\docs`
- ClawHub Skills：https://clawhub.com
- OpenClaw GitHub：https://github.com/openclaw/openclaw
