# 文件管理规范

## ⚠️ 重要规则

**绝对不要把文件放在 `.openclaw` 目录下！**

`.openclaw` 是系统缓存目录，可能会被清理或覆盖。

---

## 工作区定义

### 主工作区
- **路径**: `C:\Users\60597\.qclaw\workspace`
- **用途**: 所有工作文件、配置、Skills
- **同步**: 定期推送到 GitHub

### 备份工作区
- **路径**: `C:\Users\60597\.openclaw\workspace`
- **用途**: OpenClaw 系统读取
- **同步**: 从主工作区复制

---

## 文件组织结构

```
workspace/
├── SOUL.md                    # 人格定义
├── AGENTS.md                  # 工作规则
├── USER.md                    # 用户信息
├── IDENTITY.md                # 身份信息
├── TOOLS.md                   # 工具配置
├── HEARTBEAT.md               # 心跳任务
│
├── DECISION_RULES.md          # 决策规则库
├── EVOLUTION_ROADMAP.md       # 进化路线图
├── KNOWLEDGE_GRAPH.md         # 知识图谱
├── SELF_IMPROVEMENT.md        # 自我改进记录
├── PLAN_TEMPLATE.md           # 计划模板
│
├── memory/                    # 记忆目录
│   ├── 2026-03-22.md
│   ├── 2026-03-23.md
│   └── ...
│
├── skills/                    # Skills 目录
│   ├── code-reviewer/
│   ├── explain-code/
│   ├── project-manager/
│   ├── productivity/
│   ├── searching-assistant/
│   ├── task-dispatcher/
│   ├── web-crawler-doc/
│   └── writing-assistant/
│
└── [其他项目目录]
```

---

## 文件操作规范

### 1. 创建新文件
- 确认路径正确
- 使用 `write` 工具
- 立即验证文件是否创建成功

### 2. 修改文件
- 使用 `edit` 工具（精确匹配）
- 修改前先 `read` 确认内容
- 修改后验证

### 3. 删除文件
- **禁止直接删除**
- 先列出文件
- 用户确认后再操作
- 优先使用 `trash` 而非 `rm`

### 4. 批量操作
- 先列出受影响文件
- 用户确认
- 分步执行
- 每步验证

---

## Git 操作规范

### 提交流程
```
1. git status          # 检查状态
2. git add <files>     # 添加文件
3. git commit -m "msg" # 提交
4. git push            # 推送
```

### 常见问题

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 子模块错误 | 目录是 git 子模块 | 删除 .git 文件夹 |
| 权限错误 | 文件被锁定 | 检查是否被占用 |
| 推送失败 | 网络问题 | 重试或检查网络 |

---

## 同步规范

### 主工作区 → 备份工作区
```bash
xcopy /E /I /Y C:\Users\60597\.qclaw\workspace\skills C:\Users\60597\.openclaw\workspace\skills
```

### 何时同步
- 新增 Skills 后
- 重要配置更新后
- 每天工作结束时

---

## 检查清单

每次操作前：
- [ ] 确认工作区路径
- [ ] 确认文件位置
- [ ] 确认操作类型
- [ ] 确认备份/同步需求

---

_Last updated: 2026-03-23_
