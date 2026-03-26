# Workspace 导航

> 最后更新：2026-03-26

你的工作区，存放配置、知识库、项目和 Skills。

---

## 📂 目录结构

```
workspace/
├── SOUL.md                  # AI 人格定义（根目录，系统注入）
├── AGENTS.md                # 工作规则与流程（根目录，系统注入）
├── USER.md                  # 用户档案（根目录，系统注入）
├── IDENTITY.md              # 身份信息（根目录，系统注入）
├── HEARTBEAT.md             # 定时任务定义（根目录，系统注入）
├── TOOLS.md                 # 工具配置（根目录，系统注入）
│
├── knowledge/               # 知识库
│   ├── DECISION_RULES.md    # 决策规则库
│   ├── SELF_IMPROVEMENT.md  # 自我改进记录
│   ├── KNOWLEDGE_GRAPH.md   # 知识图谱
│   └── EVOLUTION_ROADMAP.md # 进化路线图
│
├── templates/               # 模板
│   └── PLAN_TEMPLATE.md     # 计划模板
│
├── guides/                  # 规范指南
│   └── FILE_MANAGEMENT.md   # 文件管理规范
│
├── skills/                  # 自定义 Skills
│   ├── custom/              # 你自己写的
│   │   ├── code-reviewer/
│   │   ├── explain-code/
│   │   ├── project-manager/
│   │   ├── task-dispatcher/  # TODO: 待移入
│   │   └── web-crawler-doc/
│   │
│   ├── task-dispatcher/     # TODO: 待移入 custom/
│   │
│   └── third-party/         # 从 ClawHub 安装的
│       ├── searching-assistant/
│       └── writing-assistant/
│
├── archive/                 # 归档
│   ├── cline/               # Cline 配置
│   └── cline-change-log-workflow.md
│
├── memory/                  # 记忆（保留）
├── knowledge-base/          # 知识库数据
│
├── ai-video-editor/         # 你的项目
├── video-downloader/        # 你的项目
├── awesome-openclaw-agents/ # 资源集合
│
└── PROJECT_INDEX.md         # 项目索引
```

---

## 🎯 快速定位

| 想找什么 | 去这里 |
|---------|--------|
| AI 人格/规则 | 根目录 `SOUL.md` `AGENTS.md` |
| 决策/经验/知识 | `knowledge/` |
| 计划模板 | `templates/` |
| 文件规范 | `guides/` |
| 自定义 Skills | `skills/custom/` |
| 第三方 Skills | `skills/third-party/` |
| 旧文件 | `archive/` |
| 实际项目 | 根目录下的项目目录 |

---

## 📝 说明

- **根目录 md 文件**：AI 每次会话自动注入的核心配置
- **knowledge/**：积累的经验和规则，定期回顾
- **skills/**：已配置到 `openclaw.json`，AI 会自动加载
- **archive/**：不再使用但保留参考的文件

---

## 🔧 常用操作

### 查看核心配置
```bash
cat C:\Users\admin\.qclaw\workspace\AGENTS.md
cat C:\Users\admin\.qclaw\workspace\SOUL.md
```

### 查看知识库
```bash
cat C:\Users\admin\.qclaw\workspace\knowledge\DECISION_RULES.md
```

### 列出所有 Skills
```bash
ls C:\Users\admin\.qclaw\workspace\skills\custom\
ls C:\Users\admin\.qclaw\workspace\skills\third-party\
```
