# OpenClaw 配置迁移指南

## 快速开始

将 `files/` 目录中的文件复制到新环境的 `~/.qclaw/workspace/` 目录：

```bash
# Windows
cp files/* ~/.qclaw/workspace/

# macOS / Linux
cp files/* ~/.openclaw/workspace/
```

---

## 文件结构

```
workspace/
├── AGENTS.md          # AI 工作规则（必须）
├── SOUL.md            # AI 人格（必须）
├── USER.md            # 用户画像（必须）
├── IDENTITY.md        # 身份信息（必须）
├── TOOLS.md           # 工具配置（必须）
├── HEARTBEAT.md       # 定时任务（必须）
├── SELF_IMPROVEMENT.md # 教训记录（建议）
├── CONFIG_MAP.md      # 配置影响地图（参考）
├── rules/             # 按需加载规则
│   ├── code.md        # 代码审查 + Python 规范
│   ├── memory.md      # 记忆规则
│   ├── proactive.md   # 主动预判
│   ├── research.md    # 开发调研
│   ├── toolchain.md   # 工具链
│   └── rule-evolution.md # 规则自进化
└── memory/            # 记忆存储
    └── dev-feedback.md # 开发反馈
```

---

## 核心设计理念

### 1. 人格分离
- **SOUL.md**：AI 的性格、风格、原则
- **USER.md**：你的偏好、习惯、工作流
- **IDENTITY.md**：身份名称和定位

### 2. 规则分层
- **AGENTS.md**：工作流程（计划模式、开发者模式、安全边界）
- **rules/**：按需加载的专项规则
- **AGENTS.md 规则索引**：触发关键词时加载对应 rules/*.md

### 3. 自我改进
- **SELF_IMPROVEMENT.md**：记录所有错误和教训
- **memory/**：每日记录、反馈、统计数据

---

## 修改生效方式

| 文件类型 | 生效方式 |
|---------|---------|
| 系统注入文件（AGENTS.md 等 6 个） | 重启 OpenClaw/QClaw |
| rules/*.md | 下次触发关键词时生效 |
| memory/* | 即时生效 |

---

## 个性化建议

### 必改
1. **USER.md**：改成你的身份和偏好
2. **TOOLS.md**：改成你的工作目录和端口
3. **IDENTITY.md**：改成你想要的 AI 名称

### 可选
1. **SOUL.md**：改人格风格
2. **AGENTS.md**：改工作流程
3. **HEARTBEAT.md**：改定时任务

### 建议保留
- **rules/** 结构
- **SELF_IMPROVEMENT.md** 模板
- **memory/** 分层逻辑

---

## 常见问题

### Q: 文件位置能改吗？
系统注入的 6 个文件（AGENTS.md、SOUL.md、USER.md、IDENTITY.md、TOOLS.md、HEARTBEAT.md）路径是硬编码的，不能移动。

### Q: 规则怎么加？
1. 创建 `rules/xxx.md`
2. 在 AGENTS.md 的"规则索引"中添加触发关键词和路径

### Q: 记忆怎么记？
- 每日记录：`memory/YYYY-MM-DD.md`
- 教训：`SELF_IMPROVEMENT.md`
- 长期记忆：`MEMORY.md`（根目录，可选）
