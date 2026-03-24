# Cline Rules - 解耦的规则集

## 概述

这是解耦的 Cline Rules 规则集，每个文件专注于一个方面，简洁明了。

## 文件清单

```
clinerules/
├── README.md                 # 本文件
├── vue3-components.md       # Vue 3 组件规则
├── typescript-types.md      # TypeScript 类型规则
├── error-handling.md        # 错误处理规则
├── no-hardcoding.md         # 避免硬编码规则
├── dry-principle.md         # DRY 原则规则
└── project-structure.md     # 项目结构规则
```

## 规则列表

| 文件 | 核心内容 |
|------|---------|
| `vue3-components.md` | Vue 3 组件规范（Props、Emits、scoped、key） |
| `typescript-types.md` | TypeScript 类型规范（禁止 any、接口） |
| `error-handling.md` | 错误处理规范（try-catch、loading、message） |
| `no-hardcoding.md` | 避免硬编码（API、端点、消息） |
| `dry-principle.md` | DRY 原则（提取重复代码） |
| `project-structure.md` | 项目结构（目录规范） |

## 使用方式

### 1. 选择需要的规则

根据项目选择对应的规则文件：
- Vue 3 项目：使用 `vue3-components.md`
- TypeScript 项目：使用 `typescript-types.md`
- 所有项目：使用 `error-handling.md`、`no-hardcoding.md`、`dry-principle.md`

### 2. 整合到 Cline

可以将多个规则文件整合为一个完整的规则，或选择性使用。

### 3. 示例：整合规则

```markdown
# Cline Vue 项目规则

## 必须遵守

### 1. TypeScript
- 禁止 any
- 参数和返回值必须有类型

### 2. Vue 3 组件
- 使用 <script setup>
- Props 和 Emits 必须定义

### 3. 错误处理
- 异步必须有 try-catch
- 必须有用户可见的错误消息

### 4. 避免硬编码
- API 地址使用配置
- 端点使用常量

### 5. DRY 原则
- 相同逻辑出现 2 次必须提取
```

## 原则

1. **简洁** - 每个规则文件不超过 1 页
2. **解耦** - 每个文件专注一个方面
3. **实用** - 只写最重要的规则
4. **可执行** - 规则明确，是与否清晰

