# 知识图谱

## 核心架构

```
用户
  ↓
SOUL.md (人格)
  ↓
AGENTS.md (工作规则)
  ↓
Skills (技能)
  ↓
工具 (Tools)
```

---

## 工具层

### 文件操作
| 工具 | 用途 | 注意事项 |
|------|------|----------|
| read | 读取文件 | 路径支持相对/绝对 |
| write | 写入文件 | 会覆盖原文件 |
| edit | 编辑文件 | 需要精确匹配 |
| exec | 执行命令 | 注意 timeout |

### 信息获取
| 工具 | 用途 |
|------|------|
| web_search | 网页搜索 |
| web_fetch | 获取网页内容 |
| memory_search | 搜索记忆 |

### 任务管理
| 工具 | 用途 |
|------|------|
| sessions_spawn | 创建新会话 |
| subagents | 创建子代理 |
| cron | 定时任务 |

---

## 技能层

### 已安装 Skills

| Skill | 用途 | 状态 |
|-------|------|------|
| writing-assistant | 写作辅助 | ✅ |
| searching-assistant | 搜索辅助 | ✅ |
| productivity | 生产力工具 | ✅ |
| explain-code | 代码解释 | ✅ |
| task-dispatcher | 任务调度 | ✅ |
| web-crawler-doc | 网页爬虫 | ✅ |

### 待安装 Skills

| Skill | 用途 | 状态 |
|-------|------|------|
| code | 代码生成 | ⏳ |
| code-generator | 代码生成器 | ⏳ |
| meeting-assistant | 会议助手 | ⏳ |
| code-review-fix | 代码审查 | ⚠️ |

---

## 概念关系

### 执行流程
```
用户请求
  ↓
意图识别 (AGENTS.md)
  ↓
决策选择 (DECISION_RULES.md)
  ↓
工具执行
  ↓
结果反馈
  ↓
学习记录 (SELF_IMPROVEMENT.md)
```

### 记忆层级
```
短期记忆 (当前会话)
  ↓
中期记忆 (memory/YYYY-MM-DD.md)
  ↓
长期记忆 (MEMORY.md)
```

---

## 常用模式

### 1. 安装 Skill
```
inspect → 等待 → install → 验证
```

### 2. 执行复杂任务
```
计划 → 确认 → 执行 → 记录
```

### 3. 学习新技能
```
尝试 → 失败 → 分析 → 改进 → 成功 → 记录
```

---

## 经验卡片

### ClawHub 安装
- Rate Limit: 120次/窗口期
- 解决: 等待60-120秒
- 间隔: 至少30秒/次

### 文件操作
- 写前: 确认路径
- 覆盖: 先备份或确认
- 删除: 绝对禁止

### 命令执行
- 超时: 设置合理 timeout
- 失败: 检查错误信息
- 网络: 多次重试

---

_Last updated: 2026-03-22_
