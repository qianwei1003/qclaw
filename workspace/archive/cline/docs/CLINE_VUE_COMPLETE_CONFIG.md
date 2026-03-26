# Vue 2/3 Cline 配置 - 完整文件清单

## 📁 已创建的文件

所有文件保存在：`C:\Users\admin\.qclaw\`

| 文件名 | 内容 | 优先级 |
|--------|------|--------|
| `CLINE_VUE_COMPONENT_STANDARDS.md` | Vue 2/3 组件设计规范 | 🔴 必须 |
| `CLINE_FUNCTION_DESIGN_STANDARDS.md` | 函数设计规范 | 🔴 必须 |
| `CLINE_REUSABILITY_STANDARDS.md` | 可复用性检查规范 | 🔴 必须 |
| `CLINE_HARDCODING_STANDARDS.md` | 硬编码检查规范 | 🔴 必须 |
| `CLINE_DUPLICATE_CODE_STANDARDS.md` | 重复代码识别规范 | 🔴 必须 |

---

## 📋 每个文件的内容

### 1️⃣ CLINE_VUE_COMPONENT_STANDARDS.md

**核心内容**：
- Vue 3 组件设计（Composition API）
- Vue 2 组件设计（Options API）
- Props 设计与验证
- Emits 定义
- 模板规范
- 样式规范
- 事件处理规范
- 组件检查清单

**关键点**：
- Props 必须有类型、默认值、验证器
- Emits 必须有类型定义
- 使用 scoped 样式
- v-for 必须有 :key
- 模板嵌套不超过 3 层

---

### 2️⃣ CLINE_FUNCTION_DESIGN_STANDARDS.md

**核心内容**：
- TypeScript 函数类型注解
- 参数设计原则（不超过 5 个）
- 返回类型注解
- 错误处理规范
- JSDoc 注释规范
- Vue 组件中的方法定义

**关键点**：
- 所有参数必须有类型注解
- 必须有返回类型注解
- 不能使用 any
- 异步函数必须有 try-catch
- 复杂函数必须有 JSDoc

---

### 3️⃣ CLINE_REUSABILITY_STANDARDS.md

**核心内容**：
- 重复代码识别（3 种类型）
- 提取为工具函数
- 提取为 Composables（Vue 3）
- 提取为 Mixins（Vue 2）
- 参数化组件设计
- 可复用性检查清单

**关键点**：
- 相同逻辑出现 2 次以上就要提取
- API 调用模式 → Composable
- 验证规则 → 工具函数
- 相似的组件 → 参数化

---

### 4️⃣ CLINE_HARDCODING_STANDARDS.md

**核心内容**：
- 不能硬编码的内容清单
- 配置文件结构
- 常量定义规范
- 环境变量使用
- 魔法数字处理
- 硬编码检查清单

**关键点**：
- API 地址 → config/api.ts
- API 端点 → constants/api.ts
- 错误消息 → constants/messages.ts
- 正则表达式 → constants/patterns.ts
- 魔法数字 → constants/time.ts

---

### 5️⃣ CLINE_DUPLICATE_CODE_STANDARDS.md

**核心内容**：
- 重复代码的 3 种类型
- 常见重复模式识别
- API 调用模式提取
- 表单验证模式提取
- 列表操作模式提取
- 条件渲染模式提取

**关键点**：
- 相同逻辑 → 工具函数
- 响应式状态 → Composable
- 验证规则 → 验证函数
- 相似 UI → 组件

---

## 🎯 使用方式

### 方式 1：作为 Cline 的系统提示词

将这些规范整合到 Cline 的系统提示词中，让 Cline 生成代码时自动遵循这些规范。

### 方式 2：作为代码审查清单

生成代码后，对照这些规范检查代码质量。

### 方式 3：作为生成模板

在让 Cline 生成代码时，明确告诉它需要遵循这些规范。

---

## 📝 检查清单汇总

### 生成组件后检查

- [ ] 组件有 name 属性
- [ ] Props 有类型、默认值、验证器
- [ ] Emits 有定义
- [ ] 使用 scoped 样式
- [ ] v-for 有 :key
- [ ] 模板嵌套不过深

### 生成函数后检查

- [ ] 参数有类型注解
- [ ] 有返回类型注解
- [ ] 没有 any
- [ ] 有错误处理
- [ ] 有 JSDoc 注释

### 生成代码后检查

- [ ] 没有硬编码值
- [ ] 没有重复代码
- [ ] 可复用逻辑已提取
- [ ] 遵循项目结构规范

---

## 🔧 下一步

1. **将这些规范整合到 Cline 的系统提示词中**
2. **用新项目测试效果**
3. **根据实际使用反馈调整**

---

## 📚 相关文件

之前创建的配置文件：

- `CLINE_CONFIG.md` - 配置管理主文档
- `CLINE_CONFIG_LOG.md` - 配置记录表
- `CLINE_OPTIMIZATION_PLAN.md` - 优化计划
- `CLINE_REFINED_PLAN.md` - 调整后的计划

