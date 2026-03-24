# 函数设计规范

## 📋 概述

本文档定义了函数的设计规范，确保生成的函数代码质量一致、可维护、可测试。

---

## 🎯 核心原则

### 1. 单一职责
- 一个函数只做一件事
- 函数应该可以独立测试
- 函数应该没有副作用（除非必要）

### 2. 命名清晰
- 函数名应该是动词或动词短语
- 函数名应该表达意图，不只是描述行为
- 避免模糊的命名

### 3. 参数合理
- 参数数量不超过 5 个
- 使用对象参数代替多个参数
- 参数必须有类型注解

### 4. 返回值明确
- 始终定义返回类型
- 返回值应该符合预期
- 错误情况要有明确的处理

---

## 📝 TypeScript 函数规范

### 1. 函数类型注解

```typescript
// ✅ 好 - 完整的类型注解
/**
 * 获取用户列表
 * @param pageNum - 页码
 * @param pageSize - 每页数量
 * @returns 用户列表
 */
function getUserList(
  pageNum: number,
  pageSize: number
): Promise<User[]> {
  return api.get('/users', { pageNum, pageSize })
}

// ✅ 好 - 使用箭头函数
const getUserList = (
  pageNum: number,
  pageSize: number
): Promise<User[]> => {
  return api.get('/users', { pageNum, pageSize })
}

// ❌ 不好 - 没有返回类型
function getUserList(pageNum, pageSize) {
  return api.get('/users', { pageNum, pageSize })
}

// ❌ 不好 - 使用 any
function getUserList(pageNum: any, pageSize: any): any {
  return api.get('/users', { pageNum, pageSize })
}
```

### 2. 参数类型注解

```typescript
// ✅ 好 - 所有参数都有类型
function createUser(
  name: string,
  email: string,
  age: number
): Promise<User> {
  return api.post('/users', { name, email, age })
}

// ✅ 好 - 使用对象参数
interface CreateUserParams {
  name: string
  email: string
  age: number
}

function createUser(params: CreateUserParams): Promise<User> {
  return api.post('/users', params)
}

// ❌ 不好 - 参数没有类型
function createUser(name, email, age) {
  return api.post('/users', { name, email, age })
}

// ❌ 不好 - 参数过多
function createUser(
  name: string,
  email: string,
  age: number,
  phone: string,
  address: string,
  city: string,
  country: string,
  zipCode: string
) {}

// 建议：使用对象参数
function createUser(params: {
  name: string
  email: string
  age: number
  phone?: string
  address?: Address
}) {}
```

### 3. 返回类型注解

```typescript
// ✅ 好 - 明确的返回类型
function getUserById(id: number): Promise<User | null> {
  return api.get(`/users/${id}`).catch(() => null)
}

function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
}

function formatUserName(user: User): string {
  return `${user.firstName} ${user.lastName}`
}

// ❌ 不好 - 没有返回类型
function getUserById(id) {
  return api.get(`/users/${id}`)
}
```

### 4. 异常处理

```typescript
// ✅ 好 - 完整的错误处理
/**
 * 获取用户
 * @param id - 用户 ID
 * @returns 用户信息
 * @throws {ApiError} 当用户不存在时
 */
async function getUserById(id: number): Promise<User> {
  try {
    const response = await api.get<User>(`/users/${id}`)
    return response.data
  } catch (error) {
    if (error instanceof ApiError && error.status === 404) {
      throw new Error(`用户 ${id} 不存在`)
    }
    throw error
  }
}

// ✅ 好 - 使用 Result 类型
type Result<T, E = Error> = 
  | { success: true; data: T }
  | { success: false; error: E }

function getUserById(id: number): Result<User> {
  try {
    const user = await api.get<User>(`/users/${id}`)
    return { success: true, data: user }
  } catch (error) {
    return { success: false, error: error as Error }
  }
}

// 使用
const result = getUserById(1)
if (result.success) {
  console.log(result.data)
} else {
  console.error(result.error)
}

// ❌ 不好 - 没有错误处理
async function getUserById(id: number): Promise<User> {
  const response = await api.get(`/users/${id}`)
  return response.data
}
```

---

## 📝 Vue 组件中的函数规范

### 1. 方法定义（Vue 3 Composition API）

```typescript
// ✅ 好 - 清晰的方法定义
const fetchUsers = async (
  pageNum: number = 1,
  pageSize: number = 10
): Promise<void> => {
  loading.value = true
  error.value = null
  
  try {
    const response = await userService.getUserList(pageNum, pageSize)
    users.value = response.data
    total.value = response.total
  } catch (err) {
    error.value = err as Error
    console.error('获取用户列表失败:', err)
  } finally {
    loading.value = false
  }
}

// ✅ 好 - 事件处理方法
const onSubmit = (formData: FormData): void => {
  if (!validateForm(formData)) {
    return
  }
  emit('submit', formData)
}

const onReset = (): void => {
  formData.value = initialFormData()
}

// ❌ 不好 - 没有类型注解
const fetchUsers = async () => {
  const response = await api.get('/users')
  users.value = response.data
}
```

### 2. 方法定义（Vue 2 Options API）

```typescript
export default {
  methods: {
    // ✅ 好 - 完整的方法定义
    async fetchUsers(
      pageNum: number = 1,
      pageSize: number = 10
    ): Promise<void> {
      this.loading = true
      this.error = null
      
      try {
        const response = await this.$services.user.getList(pageNum, pageSize)
        this.users = response.data
        this.total = response.total
      } catch (error) {
        this.error = error
        this.$message.error('获取用户列表失败')
      } finally {
        this.loading = false
      }
    },
    
    // ✅ 好 - 事件处理方法
    onSearch(query: string): void {
      this.searchQuery = query
      this.fetchUsers(1)  // 重置到第一页
    },
    
    onPageChange(pageNum: number): void {
      this.fetchUsers(pageNum)
    },
    
    onSortChange(sortBy: string, order: 'asc' | 'desc'): void {
      this.sortBy = sortBy
      this.order = order
      this.fetchUsers()
    },
    
    // ❌ 不好 - 没有类型注解
    fetchUsers() {
      api.get('/users').then(res => {
        this.users = res.data
      })
    }
  }
}
```

---

## 📝 JSDoc 注释规范

### 1. 完整 JSDoc

```typescript
/**
 * 获取用户列表
 * 
 * @param pageNum - 页码，从 1 开始
 * @param pageSize - 每页数量，默认 10，最大 100
 * @param search - 搜索关键词（可选）
 * @param sortBy - 排序字段（可选）
 * @param order - 排序方式（可选）
 * @returns 包含用户列表和总数的响应对象
 * @throws {ApiError} 当 API 调用失败时抛出
 * @throws {ValidationError} 当参数验证失败时抛出
 * 
 * @example
 * // 获取第一页用户
 * const result = await getUserList(1, 10)
 * 
 * @example
 * // 搜索并排序
 * const result = await getUserList(1, 20, '张三', 'name', 'asc')
 */
function getUserList(
  pageNum: number,
  pageSize: number = 10,
  search?: string,
  sortBy?: string,
  order?: 'asc' | 'desc'
): Promise<UserListResponse> {
  // 实现
}
```

### 2. 简单 JSDoc

```typescript
/**
 * 格式化日期
 * @param date - 日期对象或日期字符串
 * @returns 格式化的日期字符串
 */
function formatDate(date: Date | string): string {
  const d = typeof date === 'string' ? new Date(date) : date
  return d.toLocaleDateString('zh-CN')
}
```

### 3. 什么时候需要 JSDoc

```typescript
// ✅ 需要 JSDoc - 导出的函数
export function getUserList(): Promise<User[]> {}
export function formatDate(date: Date): string {}

// ✅ 需要 JSDoc - 复杂函数
/**
 * 使用二分查找在有序数组中查找目标元素
 * @param arr - 有序数组
 * @param target - 目标值
 * @returns 目标值的索引，未找到返回 -1
 */
function binarySearch(arr: number[], target: number): number {}

// ❌ 不需要 JSDoc - 简单的内部函数
const handleClick = () => {
  emit('click')
}
```

---

## ✅ 函数检查清单

### 生成函数后，必须检查

- [ ] 函数有清晰的命名（动词或动词短语）
- [ ] 所有参数都有类型注解
- [ ] 有返回类型注解
- [ ] 没有使用 any 类型
- [ ] 参数数量不超过 5 个（使用对象参数）
- [ ] 复杂函数有 JSDoc 注释
- [ ] JSDoc 包含 @param 和 @returns
- [ ] 异步函数有 try-catch
- [ ] 有错误处理和错误提示
- [ ] 函数职责单一（不超过 50 行）
- [ ] 没有副作用（除非必要）
- [ ] 函数可以独立测试

---

## 📝 常见错误

### 1. 参数过多

```typescript
// ❌ 不好
function createUser(
  name: string,
  email: string,
  age: number,
  phone: string,
  address: string
) {}

// ✅ 好 - 使用对象参数
function createUser(params: {
  name: string
  email: string
  age: number
  phone?: string
  address?: string
}) {}
```

### 2. 返回类型不明确

```typescript
// ❌ 不好
function getUser(id) {
  return api.get('/users/' + id)
}

// ✅ 好
function getUser(id: number): Promise<User> {
  return api.get(`/users/${id}`)
}
```

### 3. 没有错误处理

```typescript
// ❌ 不好
async function deleteUser(id: number): Promise<void> {
  await api.delete(`/users/${id}`)
}

// ✅ 好
async function deleteUser(id: number): Promise<void> {
  try {
    await api.delete(`/users/${id}`)
  } catch (error) {
    console.error('删除用户失败:', error)
    throw error
  }
}
```

### 4. 命名不清晰

```typescript
// ❌ 不好
const doStuff = () => {}
const handle = () => {}
const process = () => {}

// ✅ 好
const fetchUserList = () => {}
const handleButtonClick = () => {}
const processUserData = () => {}
```

