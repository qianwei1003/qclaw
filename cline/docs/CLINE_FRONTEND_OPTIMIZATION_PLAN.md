# Cline 企业级前端配置方案

## 📋 需求分析

### 你的技术栈
- **主要领域**: 前端开发
- **语言**: JavaScript / TypeScript
- **框架**: Vue 2 / Vue 3
- **代码质量目标**: 企业级（不是 Demo 级）

### 主要问题
1. ❌ 项目结构不规范
2. ❌ 代码规范不一致
3. ❌ AI 生成代码质量参差不齐
4. ❌ 重复代码多
5. ❌ 硬编码问题
6. ❌ 注释规范不统一

### 解决方案
✅ 通过 MCP、Skills、Hooks、Rules、Workflows 增强 Cline 能力

---

## 🎯 优化方案（四个维度）

### 维度 1：系统提示词优化
**目标**: 让 Cline 理解企业级代码标准

#### 1.1 核心行为规范
```
- 生成企业级代码，不是 Demo 代码
- 优先考虑可维护性、可扩展性、可测试性
- 遵循 DRY（Don't Repeat Yourself）原则
- 避免硬编码，使用配置文件和常量
- 代码必须有清晰的注释和文档
```

#### 1.2 Vue 2/3 编码规范
```
- 组件命名: PascalCase
- 文件结构: 单文件组件 (.vue)
- Props 验证: 必须定义类型和默认值
- 方法命名: camelCase，动词开头
- 常量: UPPER_SNAKE_CASE
- 避免 v-if 嵌套过深
- 提取可复用逻辑到 Composables (Vue 3) 或 Mixins (Vue 2)
```

#### 1.3 TypeScript 规范
```
- 所有函数必须有类型注解
- 避免使用 any，用 unknown 或具体类型
- 接口优于类型别名（除非需要联合类型）
- 枚举用于固定值集合
```

### 维度 2：项目结构规范
**目标**: 建立统一的项目目录结构

#### 2.1 推荐的项目结构
```
src/
├── components/              # 可复用组件
│   ├── common/             # 通用组件
│   ├── business/           # 业务组件
│   └── layout/             # 布局组件
├── views/                  # 页面组件
├── composables/            # Vue 3 组合式函数 (或 mixins for Vue 2)
├── hooks/                  # 自定义 Hooks
├── services/               # API 服务层
│   ├── api/               # API 调用
│   ├── auth/              # 认证服务
│   └── storage/           # 存储服务
├── stores/                 # 状态管理 (Pinia/Vuex)
├── utils/                  # 工具函数
│   ├── validators/        # 验证函数
│   ├── formatters/        # 格式化函数
│   └── helpers/           # 辅助函数
├── constants/              # 常量定义
├── types/                  # TypeScript 类型定义
├── styles/                 # 全局样式
├── config/                 # 配置文件
└── main.ts                 # 入口文件
```

#### 2.2 命名规范
```
- 组件文件: PascalCase.vue (UserProfile.vue)
- 工具函数: camelCase.ts (formatDate.ts)
- 常量文件: UPPER_SNAKE_CASE.ts (API_ENDPOINTS.ts)
- 类型文件: types.ts 或 [name].types.ts
- 测试文件: [name].spec.ts 或 [name].test.ts
```

### 维度 3：代码质量规范
**目标**: 确保 AI 生成的代码质量

#### 3.1 代码审查清单
```
□ 是否有类型注解？
□ 是否避免了 any 类型？
□ 是否有错误处理？
□ 是否有加载/空状态处理？
□ 是否避免了硬编码？
□ 是否有适当的注释？
□ 是否遵循了命名规范？
□ 是否可以提取为可复用组件？
□ 是否有单元测试？
□ 是否考虑了性能？
□ 是否考虑了可访问性？
□ 是否有文档？
```

#### 3.2 常见问题检查
```
❌ 硬编码检查
- 不要写死 API 地址、端口、路径
- 使用 .env 或 config 文件

❌ 重复代码检查
- 相同逻辑是否可以提取为函数？
- 相同组件是否可以参数化？

❌ 注释规范
- 函数必须有 JSDoc 注释
- 复杂逻辑必须有行注释
- 避免过度注释

❌ 错误处理
- 所有 API 调用必须有 try-catch
- 必须有用户友好的错误提示
```

#### 3.3 性能规范
```
- 组件懒加载
- 图片优化（webp、压缩）
- 代码分割
- 避免内存泄漏
- 避免不必要的重新渲染
```

### 维度 4：MCP + Skills + Hooks 增强
**目标**: 通过插件系统增强 Cline 能力

#### 4.1 需要的 MCP Servers
```
1. ESLint MCP
   - 自动检查代码规范
   - 提供修复建议

2. TypeScript MCP
   - 类型检查
   - 类型推断

3. Vue Language Server MCP
   - Vue 组件分析
   - 模板检查

4. Git MCP
   - 查看代码历史
   - 检查代码变更

5. File System MCP
   - 项目结构分析
   - 文件操作
```

#### 4.2 需要的 Skills
```
1. vue-component-generator
   - 生成规范的 Vue 组件
   - 自动添加类型注解

2. typescript-enforcer
   - 强制 TypeScript 类型检查
   - 避免 any 类型

3. code-quality-checker
   - 检查代码质量
   - 提供改进建议

4. project-structure-validator
   - 验证项目结构
   - 建议重构

5. documentation-generator
   - 自动生成文档
   - 生成 JSDoc 注释
```

#### 4.3 需要的 Hooks
```
1. pre-code-generation
   - 检查需求是否清晰
   - 验证项目结构

2. post-code-generation
   - 自动运行 ESLint
   - 检查类型错误
   - 验证代码质量

3. pre-commit
   - 检查代码规范
   - 运行测试

4. documentation-hook
   - 自动生成注释
   - 更新文档
```

#### 4.4 需要的 Rules
```
1. 企业级代码规则
   - 禁止硬编码
   - 禁止 any 类型
   - 禁止过深嵌套
   - 禁止重复代码

2. 命名规范规则
   - 组件必须 PascalCase
   - 函数必须 camelCase
   - 常量必须 UPPER_SNAKE_CASE

3. 注释规范规则
   - 函数必须有 JSDoc
   - 复杂逻辑必须有注释
   - 避免过度注释

4. 项目结构规则
   - 组件必须在 components/ 目录
   - 工具函数必须在 utils/ 目录
   - 类型定义必须在 types/ 目录
```

#### 4.5 需要的 Workflows
```
1. 新组件生成工作流
   输入: 组件需求
   → 验证需求
   → 生成组件框架
   → 添加类型注解
   → 生成文档
   → 运行 ESLint
   输出: 规范的组件

2. 代码审查工作流
   输入: 代码片段
   → 检查类型
   → 检查规范
   → 检查重复
   → 检查硬编码
   → 提供改进建议
   输出: 审查报告

3. 项目重构工作流
   输入: 项目路径
   → 分析项目结构
   → 识别问题
   → 生成重构计划
   → 执行重构
   输出: 重构后的项目

4. 文档生成工作流
   输入: 代码文件
   → 提取函数签名
   → 生成 JSDoc
   → 生成 README
   输出: 完整文档
```

---

## 📁 配置文件清单

需要创建的文件：

```
C:\Users\admin\.qclaw\
├── cline-system-prompt.md              # ⭐ 系统提示词
├── cline-coding-standards.md           # ⭐ 编码规范详细版
├── cline-project-structure.md          # ⭐ 项目结构规范
├── cline-code-quality-checklist.md     # ⭐ 代码质量检查清单
├── cline-mcp-config.json               # ⭐ MCP 配置
├── cline-skills-config.json            # ⭐ Skills 配置
├── cline-hooks-config.json             # ⭐ Hooks 配置
├── cline-rules-config.json             # ⭐ Rules 配置
├── cline-workflows-config.json         # ⭐ Workflows 配置
├── cline-vue-best-practices.md         # Vue 最佳实践
├── cline-typescript-best-practices.md  # TypeScript 最佳实践
└── cline-common-mistakes.md            # 常见错误和解决方案
```

---

## 🚀 执行步骤

### 第一步：创建系统提示词（今天）
我会编写一个详细的系统提示词，包含：
- 企业级代码标准
- Vue 2/3 规范
- TypeScript 规范
- 项目结构要求
- 代码质量要求

### 第二步：配置 MCP Servers（明天）
- 列出需要的 MCP Servers
- 编写安装和配置指南
- 测试 MCP 功能

### 第三步：创建 Skills（后天）
- 设计 Vue 组件生成 Skill
- 设计代码质量检查 Skill
- 设计项目结构验证 Skill

### 第四步：配置 Hooks 和 Rules（第四天）
- 配置代码生成后的自动检查
- 配置命名规范检查
- 配置硬编码检查

### 第五步：设计 Workflows（第五天）
- 设计新组件生成工作流
- 设计代码审查工作流
- 设计项目重构工作流

### 第六步：测试和优化（第六天）
- 测试所有配置
- 收集反馈
- 持续改进

---

## 📊 预期效果

### 使用前 ❌
```
Cline 生成的代码：
- 没有类型注解
- 硬编码 API 地址
- 没有错误处理
- 没有注释
- 项目结构混乱
- 重复代码多
```

### 使用后 ✅
```
Cline 生成的代码：
- 完整的类型注解
- 使用配置文件
- 完善的错误处理
- 清晰的 JSDoc 注释
- 规范的项目结构
- 可复用的组件和函数
- 通过 ESLint 检查
- 符合企业级标准
```

---

## ⏰ 时间表

| 步骤 | 任务 | 预计时间 | 状态 |
|------|------|---------|------|
| 1 | 创建系统提示词 | 2-3 小时 | ⏳ 待开始 |
| 2 | 配置 MCP Servers | 2-3 小时 | ⏳ 待开始 |
| 3 | 创建 Skills | 3-4 小时 | ⏳ 待开始 |
| 4 | 配置 Hooks 和 Rules | 2-3 小时 | ⏳ 待开始 |
| 5 | 设计 Workflows | 3-4 小时 | ⏳ 待开始 |
| 6 | 测试和优化 | 2-3 小时 | ⏳ 待开始 |

**总计**: 14-20 小时（分散在 5-6 天）

---

## 🎯 下一步

我现在开始创建详细的配置文件。首先从**系统提示词**开始，这是最核心的部分。

你需要确认：
1. ✅ 这个方案是否符合你的需求？
2. ✅ 有没有需要调整的地方？
3. ✅ 是否有其他特殊要求？

确认后，我会立即开始创建配置文件。

