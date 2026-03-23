# 可复用性检查规范

## 📋 概述

本文档定义了如何识别和提取可复用代码的规范，确保代码遵循 DRY（Don't Repeat Yourself）原则。

---

## 🎯 核心原则

### 1. 识别重复代码
- 相同的逻辑出现 2 次以上
- 相似的逻辑只有参数不同
- 可以参数化的代码

### 2. 提取可复用逻辑
- 提取为工具函数
- 提取为 Composables（Vue 3）
- 提取为 Mixins（Vue 2）
- 提取为基类组件

### 3. 参数化组件
- 通过 Props 参数化
- 通过 Slots 扩展
- 通过 Scoped CSS 定制

---

## 🔍 重复代码识别

### 1. 相同的逻辑重复

```typescript
// ❌ 不好 - 重复的逻辑
// 文件 1
function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// 文件 2
function validateEmailAddress(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// 文件 3
function checkEmailValid(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// ✅ 好 - 提取为工具函数
// src/utils/validators/email.ts
export function validateEmail(email: string): boolean {
  const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return regex.test(email)
}

// 使用
import { validateEmail } from '@/utils/validators/email'
```

### 2. 相似的逻辑（参数不同）

```typescript
// ❌ 不好 - 相似的逻辑，只有参数不同
function formatUserName(user: User): string {
  return `${user.firstName} ${user.lastName}`
}

function formatProductName(product: Product): string {
  return `${product.brand} ${product.model}`
}

function formatOrderNumber(order: Order): string {
  return `#${order.year}-${order.month}-${order.id}`
}

// ✅ 好 - 提取为通用函数
// src/utils/formatters/index.ts
type Formatter<T> = (item: T) => string

const formatUserName: Formatter<User> = (user) => 
  `${user.firstName} ${user.lastName}`

const formatProductName: Formatter<Product> = (product) => 
  `${product.brand} ${product.model}`

const formatOrderNumber: Formatter<Order> = (order) => 
  `#${order.year}-${order.month}-${order.id}`
```

### 3. 相似的组件

```typescript
// ❌ 不好 - 多个相似的组件
// PrimaryButton.vue
<template>
  <button class="btn btn-primary" @click="handleClick">
    <slot />
  </button>
</template>

// SecondaryButton.vue
<template>
  <button class="btn btn-secondary" @click="handleClick">
    <slot />
  </button>
</template>

// DangerButton.vue
<template>
  <button class="btn btn-danger" @click="handleClick">
    <slot />
  </button>
</template>

// ✅ 好 - 提取为一个参数化的组件
// Button.vue
<template>
  <button 
    class="btn" 
    :class="[`btn-${variant}`, { 'btn-disabled': disabled }]"
    :disabled="disabled"
    @click="handleClick"
  >
    <slot />
  </button>
</template>

<script setup lang="ts">
interface Props {
  variant?: 'primary' | 'secondary' | 'danger'
  disabled?: boolean
}

withDefaults(defineProps<Props>(), {
  variant: 'primary',
  disabled: false
})

const emit = defineEmits<{
  click: [event: MouseEvent]
}>()

const handleClick = (event: MouseEvent) => {
  emit('click', event)
}
</script>

// 使用
<Button variant="primary" @click="handleClick">提交</Button>
<Button variant="secondary" @click="handleCancel">取消</Button>
<Button variant="danger" :disabled="isLoading">删除</Button>
```

---

## 🛠️ 提取为工具函数

### 1. 提取条件判断

```typescript
// ❌ 不好 - 重复的条件判断
function isAdult(user: User): boolean {
  return user.age >= 18
}

function isAdmin(user: User): boolean {
  return user.age >= 18 && user.role === 'admin'
}

function isGuest(user: User): boolean {
  return user.age >= 18 && user.role === 'guest'
}

// ✅ 好 - 提取为通用函数
// src/utils/validators/user.ts
interface User {
  age: number
  role: string
}

function hasMinimumAge(user: User, minAge: number): boolean {
  return user.age >= minAge
}

function hasRole(user: User, role: string): boolean {
  return user.role === role
}

// 使用
const isAdult = (user: User) => hasMinimumAge(user, 18)
const isAdmin = (user: User) => hasRole(user, 'admin')
const isGuest = (user: User) => hasRole(user, 'guest')
```

### 2. 提取数据转换

```typescript
// ❌ 不好 - 重复的数据转换
function getUserOptions(users: User[]): SelectOption[] {
  return users.map(user => ({
    label: user.name,
    value: user.id
  }))
}

function getProductOptions(products: Product[]): SelectOption[] {
  return products.map(product => ({
    label: product.title,
    value: product.id
  }))
}

// ✅ 好 - 提取为通用函数
// src/utils/mappers/select.ts
interface SelectOption {
  label: string
  value: number | string
}

interface HasId {
  id: number | string
}

interface HasName {
  name: string
}

function toSelectOptions<T extends HasId & HasName>(
  items: T[]
): SelectOption[] {
  return items.map(item => ({
    label: item.name,
    value: item.id
  }))
}

// 使用
const userOptions = toSelectOptions(users)
const productOptions = toSelectOptions(products)
```

### 3. 提取 API 调用模式

```typescript
// ❌ 不好 - 重复的 API 调用模式
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

// ✅ 好 - 提取为 Composable
// src/composables/useFetch.ts
import { ref, type Ref } from 'vue'

interface FetchState<T> {
  data: Ref<T | null>
  loading: Ref<boolean>
  error: Ref<Error | null>
}

function useFetch<T>(url: string): FetchState<T> & { 
  fetch: () => Promise<void> 
} {
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
const { data: users, loading, error, fetch } = useFetch<User[]>('/users')
await fetch()

const { data: products, loading, error, fetch: fetchProducts } = useFetch<Product[]>('/products')
await fetchProducts()
```

---

## 🧩 提取为 Composables（Vue 3）

### 1. 提取业务逻辑

```typescript
// ❌ 不好 - 组件中包含业务逻辑
// UserList.vue
<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { User } from '@/types/user'

const users = ref<User[]>([])
const loading = ref(false)
const error = ref<Error | null>(null)
const searchQuery = ref('')
const currentPage = ref(1)
const pageSize = ref(10)
const total = ref(0)

const fetchUsers = async () => {
  loading.value = true
  try {
    const response = await api.get('/users', {
      params: {
        page: currentPage.value,
        size: pageSize.value,
        search: searchQuery.value
      }
    })
    users.value = response.data
    total.value = response.total
  } catch (err) {
    error.value = err as Error
  } finally {
    loading.value = false
  }
}

const onSearch = (query: string) => {
  searchQuery.value = query
  currentPage.value = 1
  fetchUsers()
}

const onPageChange = (page: number) => {
  currentPage.value = page
  fetchUsers()
}

onMounted(() => {
  fetchUsers()
})
</script>

// ✅ 好 - 提取为 Composable
// src/composables/useUserList.ts
import { ref, onMounted } from 'vue'
import type { User } from '@/types/user'

export function useUserList() {
  const users = ref<User[]>([])
  const loading = ref(false)
  const error = ref<Error | null>(null)
  const searchQuery = ref('')
  const currentPage = ref(1)
  const pageSize = ref(10)
  const total = ref(0)

  const fetchUsers = async () => {
    loading.value = true
    try {
      const response = await api.get('/users', {
        params: {
          page: currentPage.value,
          size: pageSize.value,
          search: searchQuery.value
        }
      })
      users.value = response.data
      total.value = response.total
    } catch (err) {
      error.value = err as Error
    } finally {
      loading.value = false
    }
  }

  const onSearch = (query: string) => {
    searchQuery.value = query
    currentPage.value = 1
    fetchUsers()
  }

  const onPageChange = (page: number) => {
    currentPage.value = page
    fetchUsers()
  }

  onMounted(() => {
    fetchUsers()
  })

  return {
    users,
    loading,
    error,
    searchQuery,
    currentPage,
    pageSize,
    total,
    fetchUsers,
    onSearch,
    onPageChange
  }
}

// 使用
// UserList.vue
<script setup lang="ts">
import { useUserList } from '@/composables/useUserList'

const {
  users,
  loading,
  error,
  searchQuery,
  currentPage,
  pageSize,
  total,
  onSearch,
  onPageChange
} = useUserList()
</script>
```

### 2. 提取通用逻辑

```typescript
// ✅ 好 - 提取分页逻辑
// src/composables/usePagination.ts
import { ref, computed } from 'vue'

export function usePagination<T>(initialPageSize = 10) {
  const currentPage = ref(1)
  const pageSize = ref(initialPageSize)
  const total = ref(0)

  const totalPages = computed(() => 
    Math.ceil(total.value / pageSize.value)
  )

  const isFirstPage = computed(() => 
    currentPage.value === 1
  )

  const isLastPage = computed(() => 
    currentPage.value >= totalPages.value
  )

  const setPage = (page: number) => {
    currentPage.value = page
  }

  const setPageSize = (size: number) => {
    pageSize.value = size
    currentPage.value = 1
  }

  const setTotal = (count: number) => {
    total.value = count
  }

  const nextPage = () => {
    if (!isLastPage.value) {
      currentPage.value++
    }
  }

  const prevPage = () => {
    if (!isFirstPage.value) {
      currentPage.value--
    }
  }

  return {
    currentPage,
    pageSize,
    total,
    totalPages,
    isFirstPage,
    isLastPage,
    setPage,
    setPageSize,
    setTotal,
    nextPage,
    prevPage
  }
}

// 使用
const {
  currentPage,
  pageSize,
  total,
  totalPages,
  onPageChange
} = usePagination(20)
```

---

## 🧩 提取为 Mixins（Vue 2）

### 1. 提取业务逻辑

```javascript
// ✅ 好 - 提取为独立的 Mixin
// src/mixins/userMixin.js
export default {
  props: {
    userId: {
      type: Number,
      required: true
    }
  },
  
  data() {
    return {
      user: null,
      loading: false,
      error: null
    }
  },
  
  computed: {
    hasUser() {
      return this.user !== null
    },
    
    userName() {
      return this.user ? `${this.user.firstName} ${this.user.lastName}` : ''
    }
  },
  
  methods: {
    async fetchUser() {
      this.loading = true
      this.error = null
      
      try {
        this.user = await this.$services.user.get(this.userId)
      } catch (error) {
        this.error = error
        this.$message.error('获取用户信息失败')
      } finally {
        this.loading = false
      }
    },
    
    async updateUser(userData) {
      this.loading = true
      try {
        this.user = await this.$services.user.update(this.userId, userData)
        this.$message.success('更新成功')
      } catch (error) {
        this.error = error
        this.$message.error('更新失败')
      } finally {
        this.loading = false
      }
    }
  },
  
  mounted() {
    this.fetchUser()
  }
}

// 使用
// UserProfile.vue
import userMixin from '@/mixins/userMixin'

export default {
  name: 'UserProfile',
  mixins: [userMixin],
  
  // 可以在组件中覆盖或扩展
}
```

---

## ✅ 可复用性检查清单

### 代码生成后，必须检查

- [ ] 是否有重复的逻辑（出现 2 次以上）？
- [ ] 是否有相似的代码只有参数不同？
- [ ] 是否可以提取为工具函数？
- [ ] 是否可以提取为 Composable（Vue 3）？
- [ ] 是否可以提取为 Mixin（Vue 2）？
- [ ] 是否有相似的组件可以参数化？
- [ ] 组件中的业务逻辑是否已提取？
- [ ] API 调用模式是否重复？
- [ ] 数据转换逻辑是否重复？
- [ ] 条件判断逻辑是否重复？

### 提取原则

- [ ] 函数职责单一（不超过 30 行）
- [ ] 函数可以独立测试
- [ ] Composable 专注于一个功能
- [ ] Mixin 专注于相关功能
- [ ] 组件通过 Props 参数化

---

## 🚫 不要重复

### ❌ 复制粘贴代码
```typescript
// 错误：复制粘贴
function validatePhone(phone: string): boolean {
  return /^1\d{10}$/.test(phone)
}

function validateMobile(mobile: string): boolean {
  return /^1\d{10}$/.test(mobile)
}

// 正确：提取为通用函数
function validatePhone(phone: string): boolean {
  return /^1\d{10}$/.test(phone)
}

// 或者直接使用同一个函数
const validateMobile = validatePhone
```

### ❌ 创建多个相似组件
```vue
<!-- 错误：多个相似的组件 -->
<PrimaryButton />
<SecondaryButton />
<DangerButton />

<!-- 正确：一个参数化的组件 -->
<Button variant="primary" />
<Button variant="secondary" />
<Button variant="danger" />
```

### ❌ 在每个组件中重复逻辑
```typescript
// 错误：在每个组件中重复
export default {
  methods: {
    async fetchData() {
      this.loading = true
      try {
        this.data = await api.get('/data')
      } finally {
        this.loading = false
      }
    }
  }
}

// 正确：提取为 Composable
// src/composables/useFetch.ts
export function useFetch<T>(url: string) {
  // ... 提取的逻辑
}
```

