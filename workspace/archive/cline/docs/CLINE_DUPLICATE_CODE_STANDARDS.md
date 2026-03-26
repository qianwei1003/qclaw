# 重复代码识别与提取规范

## 📋 概述

本文档定义了如何识别、检测和提取重复代码的规范，确保代码遵循 DRY（Don't Repeat Yourself）原则。

---

## 🎯 什么是重复代码

### 1. 完全相同的代码

```typescript
// 文件 A
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// 文件 B（完全相同）
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}
```

### 2. 几乎相同的代码（只有参数不同）

```typescript
// 类似的逻辑，只有值不同
const users = await api.get('/users', { page: 1, size: 10 })
const products = await api.get('/products', { page: 1, size: 10 })
const orders = await api.get('/orders', { page: 1, size: 10 })

// 类似的验证
if (!email) return '邮箱不能为空'
if (!phone) return '手机号不能为空'
if (!name) return '姓名不能为空'

// 类似的格式化
const userName = `${user.firstName} ${user.lastName}`
const productName = `${product.brand} ${product.model}`
const orderNo = `#${order.year}-${order.month}-${order.id}`
```

### 3. 相同的代码模式

```typescript
// 相同的 API 调用模式
const fetchUsers = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/users')
    users.value = response.data
  } catch (err) {
    error.value = err as Error
  } finally {
    loading.value = false
  }
}

const fetchProducts = async () => {
  loading.value = true
  error.value = null
  try {
    const response = await api.get('/products')
    products.value = response.data
  } catch (err) {
    error.value = err as Error
  } finally {
    loading.value = false
  }
}
```

---

## 🔍 重复代码识别模式

### 1. API 调用模式

```typescript
// ❌ 重复 - 相同的加载状态管理
const fetchData1 = async () => {
  loading1.value = true
  error1.value = null
  try {
    data1.value = await api.get('/endpoint1')
  } catch (err) {
    error1.value = err as Error
  } finally {
    loading1.value = false
  }
}

const fetchData2 = async () => {
  loading2.value = true
  error2.value = null
  try {
    data2.value = await api.get('/endpoint2')
  } catch (err) {
    error2.value = err as Error
  } finally {
    loading2.value = false
  }
}

// ✅ 提取为 Composable
// src/composables/useFetch.ts
export function useFetch<T>(url: string) {
  const data = ref<T | null>(null)
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetch = async () => {
    loading.value = true
    error.value = null
    try {
      const response = await api.get<T>(url)
      data.value = response.data
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  return { data, loading, error, fetch }
}

// 使用
const { data: users, loading: usersLoading, error: usersError, fetch: fetchUsers } = useFetch<User[]>('/users')
const { data: products, loading: productsLoading, error: productsError, fetch: fetchProducts } = useFetch<Product[]>('/products')
```

### 2. 表单验证模式

```typescript
// ❌ 重复 - 类似的验证逻辑
const validateUser = (data: UserFormData): string[] => {
  const errors: string[] = []
  if (!data.name) errors.push('姓名不能为空')
  if (!data.email) errors.push('邮箱不能为空')
  if (data.email && !isValidEmail(data.email)) errors.push('邮箱格式不正确')
  if (!data.phone) errors.push('手机号不能为空')
  if (data.phone && !isValidPhone(data.phone)) errors.push('手机号格式不正确')
  return errors
}

const validateProduct = (data: ProductFormData): string[] => {
  const errors: string[] = []
  if (!data.name) errors.push('名称不能为空')
  if (!data.price) errors.push('价格不能为空')
  if (data.price && data.price < 0) errors.push('价格不能为负数')
  return errors
}

// ✅ 提取为验证函数
// src/utils/validators/index.ts

// 基础验证
export function isRequired(value: any, fieldName: string): string | null {
  return value ? null : `${fieldName}不能为空`
}

export function isEmail(value: string, fieldName: string): string | null {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(value) ? null : `${fieldName}格式不正确`
}

export function isPositiveNumber(value: number, fieldName: string): string | null {
  return value >= 0 ? null : `${fieldName}不能为负数`
}

// 组合验证
export function validateField(
  value: any,
  rules: Array<(value: any) => string | null>
): string | null {
  for (const rule of rules) {
    const error = rule(value)
    if (error) return error
  }
  return null
}

// 使用
const validateUser = (data: UserFormData): string[] => {
  const errors: string[] = []
  
  errors.push(validateField(data.name, [v => isRequired(v, '姓名')]))
  errors.push(validateField(data.email, [v => isRequired(v, '邮箱'), v => isEmail(v, '邮箱')]))
  errors.push(validateField(data.phone, [v => isRequired(v, '手机号'), v => isPhone(v, '手机号')]))
  
  return errors.filter(Boolean)
}
```

### 3. 列表操作模式

```typescript
// ❌ 重复 - 类似的列表操作
const addUser = (user: User) => {
  users.value = [...users.value, user]
}

const addProduct = (product: Product) => {
  products.value = [...products.value, product]
}

const updateUser = (user: User) => {
  users.value = users.value.map(u => u.id === user.id ? user : u)
}

const updateProduct = (product: Product) => {
  products.value = products.value.map(p => p.id === product.id ? product : p)
}

const deleteUser = (id: number) => {
  users.value = users.value.filter(u => u.id !== id)
}

const deleteProduct = (id: number) => {
  products.value = products.value.filter(p => p.id !== id)
}

// ✅ 提取为通用函数
// src/utils/helpers/array.ts

export function addItem<T extends { id: number | string }>(
  list: Ref<T[]>,
  item: T
) {
  list.value = [...list.value, item]
}

export function updateItem<T extends { id: number | string }>(
  list: Ref<T[]>,
  item: T
) {
  list.value = list.value.map(i => i.id === item.id ? item : i)
}

export function deleteItem<T extends { id: number | string }>(
  list: Ref<T[]>,
  id: number | string
) {
  list.value = list.value.filter(i => i.id !== id)
}

export function findItem<T extends { id: number | string }>(
  list: T[],
  id: number | string
): T | undefined {
  return list.find(i => i.id === id)
}

// 使用
import { addItem, updateItem, deleteItem } from '@/utils/helpers/array'

const addUser = (user: User) => addItem(users, user)
const updateUser = (user: User) => updateItem(users, user)
const deleteUser = (id: number) => deleteItem(users, id)
```

### 4. 条件渲染模式

```typescript
// ❌ 重复 - 类似的条件渲染
<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="error">{{ error.message }}</div>
  <div v-else-if="!users.length">暂无数据</div>
  <div v-else>
    <!-- 用户列表 -->
  </div>
</template>

<!-- 另一个组件 -->
<template>
  <div v-if="loading">加载中...</div>
  <div v-else-if="error">{{ error.message }}</div>
  <div v-else-if="!products.length">暂无数据</div>
  <div v-else>
    <!-- 产品列表 -->
  </div>
</template>

// ✅ 提取为组件
// src/components/common/StateDisplay.vue
<template>
  <div v-if="loading" class="state-display state-display--loading">
    <slot name="loading">加载中...</slot>
  </div>
  <div v-else-if="error" class="state-display state-display--error">
    <slot name="error">{{ error }}</slot>
  </div>
  <div v-else-if="isEmpty" class="state-display state-display--empty">
    <slot name="empty">暂无数据</slot>
  </div>
  <div v-else class="state-display state-display--content">
    <slot />
  </div>
</template>

<script setup lang="ts">
interface Props {
  loading?: boolean
  error?: Error | null
  isEmpty?: boolean
}

defineProps<Props>()
</script>

// 使用
<StateDisplay :loading="loading" :error="error" :isEmpty="!users.length">
  <UserList :users="users" />
  
  <template #loading>
    <LoadingSpinner />
  </template>
  
  <template #error>
    <ErrorMessage :message="error.message" />
  </template>
  
  <template #empty>
    <EmptyState message="暂无用户" />
  </template>
</StateDisplay>
```

---

## 🛠️ 提取策略

### 1. 工具函数

**适用场景**: 纯函数，无副作用，相同的逻辑

```typescript
// 提取条件
- 相同的计算逻辑
- 相同的数据转换
- 相同的验证规则
- 相同的格式化

// 提取位置
// src/utils/[category]/[function].ts
```

### 2. Composables（Vue 3）

**适用场景**: 响应式状态 + 业务逻辑

```typescript
// 提取条件
- 相同的状态管理
- 相同的 API 调用模式
- 相同的生命周期逻辑
- 相同的用户交互处理

// 提取位置
// src/composables/use[Feature].ts
```

### 3. Mixins（Vue 2）

**适用场景**: 组件间的共享逻辑

```typescript
// 提取条件
- 相同的组件选项
- 相同的方法
- 相同的计算属性

// 提取位置
// src/mixins/[feature].js
```

### 4. 组件

**适用场景**: 相同的 UI 结构和行为

```typescript
// 提取条件
- 相同的模板结构
- 相同的样式
- 相同的行为

// 提取位置
// src/components/common/[ComponentName].vue
```

---

## ✅ 重复代码检查清单

### 生成代码后，必须检查

#### 相同逻辑
- [ ] 是否有完全相同的函数？
- [ ] 是否有几乎相同的函数？
- [ ] 是否可以提取为工具函数？

#### API 调用
- [ ] 是否有重复的 API 调用模式？
- [ ] 是否有重复的状态管理逻辑？
- [ ] 是否可以提取为 Composable/Mixin？

#### 验证逻辑
- [ ] 是否有重复的验证规则？
- [ ] 是否有重复的错误处理？
- [ ] 是否可以提取为验证函数？

#### 数据处理
- [ ] 是否有重复的数据转换？
- [ ] 是否有重复的列表操作？
- [ ] 是否可以提取为数据处理函数？

#### UI 组件
- [ ] 是否有相似的组件？
- [ ] 是否有重复的模板结构？
- [ ] 是否可以参数化为一个组件？

---

## 📝 提取示例

### 示例 1：从重复到工具函数

```typescript
// ❌ 之前 - 重复的格式化逻辑
function formatUserName(user: User): string {
  return `${user.firstName} ${user.lastName}`
}

function formatProductName(product: Product): string {
  return `${product.brand} ${product.model}`
}

// ✅ 之后 - 提取为通用函数
// src/utils/formatters/string.ts
type HasName = { firstName?: string; lastName?: string }
type HasBrand = { brand: string; model: string }

function formatName<T extends HasName>(item: T): string {
  return `${item.firstName} ${item.lastName}`
}

function formatProductName<T extends HasBrand>(item: T): string {
  return `${item.brand} ${item.model}`
}
```

### 示例 2：从重复到 Composable

```typescript
// ❌ 之前 - 重复的状态管理
// UserList.vue
const users = ref<User[]>([])
const loading = ref(false)
const error = ref<Error | null>(null)

const fetchUsers = async () => {
  loading.value = true
  // ...
}

// ProductList.vue
const products = ref<Product[]>([])
const loading = ref(false)
const error = ref<Error | null>(null)

const fetchProducts = async () => {
  loading.value = true
  // ...
}

// ✅ 之后 - 提取为 Composable
// src/composables/useFetchList.ts
export function useFetchList<T>(url: string) {
  const items = ref<T[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)

  const fetch = async () => {
    loading.value = true
    try {
      const response = await api.get<T[]>(url)
      items.value = response.data
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  return { items, loading, error, fetch }
}
```

### 示例 3：从重复到组件

```typescript
// ❌ 之前 - 重复的加载状态组件
// Loading1.vue
<template>
  <div class="loading">
    <span>加载中...</span>
  </div>
</template>

// Loading2.vue
<template>
  <div class="loading">
    <span>加载中...</span>
  </div>
</template>

// ✅ 之后 - 提取为一个通用组件
// src/components/common/Loading.vue
<template>
  <div class="loading">
    <slot>{{ message }}</slot>
  </div>
</template>

<script setup lang="ts">
withDefaults(defineProps<{
  message?: string
}>(), {
  message: '加载中...'
})
</script>
```

---

## 🔧 工具辅助

### ESLint 规则

```json
{
  "rules": {
    "no-duplicate-case": "error",
    "no-dupe-else-if": "error",
    "no-duplicate-imports": "error",
    "no-irregular-whitespace": "error"
  }
}
```

### TypeScript 配置

```json
{
  "compilerOptions": {
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

