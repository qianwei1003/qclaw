# 硬编码检查规范

## 📋 概述

本文档定义了如何识别和避免硬编码的规范，确保代码使用配置文件而不是固定值。

---

## 🎯 核心原则

### 1. 什么不能硬编码

| 类型 | 示例 | 正确做法 |
|------|------|---------|
| API 地址 | `http://localhost:8080/api` | 使用 `config/api.ts` |
| API 端点 | `/users`, `/products` | 使用常量 |
| 端口号 | `8080`, `3000` | 使用环境变量 |
| 超时时间 | `5000`, `10000` | 使用配置 |
| 分页大小 | `10`, `20` | 使用常量 |
| 错误消息 | `'获取失败'` | 使用常量 |
| 正则表达式 | `/^[a-z]+$/` | 使用常量 |
| 魔法数字 | `3600`, `86400` | 使用常量 |

### 2. 应该使用配置文件的地方

```typescript
// ✅ 好 - 使用配置文件
// src/config/api.ts
export const API_CONFIG = {
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
  endpoints: {
    users: '/users',
    products: '/products',
    orders: '/orders'
  }
}

// src/constants/api.ts
export const API_ENDPOINTS = {
  USERS: '/users',
  PRODUCTS: '/products',
  ORDERS: '/orders'
} as const

export const DEFAULT_PAGE_SIZE = 10
export const MAX_PAGE_SIZE = 100

// src/constants/messages.ts
export const ERROR_MESSAGES = {
  NETWORK_ERROR: '网络错误，请检查您的网络连接',
  SERVER_ERROR: '服务器错误，请稍后再试',
  NOT_FOUND: '请求的资源不存在',
  UNAUTHORIZED: '您没有权限访问此资源'
} as const

// 使用
import { API_CONFIG } from '@/config/api'
import { API_ENDPOINTS, DEFAULT_PAGE_SIZE } from '@/constants/api'
import { ERROR_MESSAGES } from '@/constants/messages'

// ❌ 不好 - 硬编码
const api = 'http://localhost:8080/api'
const pageSize = 10
const errorMessage = '获取失败'
```

---

## 🔍 硬编码识别清单

### 1. API 相关

```typescript
// ❌ 不好 - 硬编码 API 地址
const response = await fetch('http://localhost:8080/api/users')

// ✅ 好 - 使用配置
import { API_CONFIG } from '@/config/api'
const response = await fetch(`${API_CONFIG.baseURL}/users`)

// ❌ 不好 - 硬编码端点
const users = await api.get('/users')
const products = await api.get('/products')

// ✅ 好 - 使用常量
import { API_ENDPOINTS } from '@/constants/api'
const users = await api.get(API_ENDPOINTS.USERS)
const products = await api.get(API_ENDPOINTS.PRODUCTS)
```

### 2. 超时时间

```typescript
// ❌ 不好 - 硬编码超时
const response = await fetch(url, {
  method: 'POST',
  signal: setTimeout(5000)  // 5秒超时
})

// ✅ 好 - 使用配置
import { API_CONFIG } from '@/config/api'
const response = await fetch(url, {
  method: 'POST',
  signal: setTimeout(API_CONFIG.timeout)
})
```

### 3. 分页

```typescript
// ❌ 不好 - 硬编码分页大小
const pageSize = 20

// ✅ 好 - 使用常量
import { DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE } from '@/constants/api'
const pageSize = DEFAULT_PAGE_SIZE
```

### 4. 错误消息

```typescript
// ❌ 不好 - 硬编码错误消息
try {
  await api.get('/users')
} catch (error) {
  alert('获取用户失败')
}

// ✅ 好 - 使用常量
import { ERROR_MESSAGES } from '@/constants/messages'
try {
  await api.get('/users')
} catch (error) {
  alert(ERROR_MESSAGES.NETWORK_ERROR)
}
```

### 5. 正则表达式

```typescript
// ❌ 不好 - 硬编码正则
const isValidEmail = (email: string) => 
  /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

const isValidPhone = (phone: string) => 
  /^1\d{10}$/.test(phone)

// ✅ 好 - 使用常量
// src/constants/patterns.ts
export const REGEX_PATTERNS = {
  EMAIL: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
  PHONE: /^1\d{10}$/,
  URL: /^https?:\/\/.+/,
  ID_CARD: /^\d{17}[\dXx]$/
} as const

// 使用
import { REGEX_PATTERNS } from '@/constants/patterns'
const isValidEmail = (email: string) => REGEX_PATTERNS.EMAIL.test(email)
const isValidPhone = (phone: string) => REGEX_PATTERNS.PHONE.test(phone)
```

### 6. 魔法数字

```typescript
// ❌ 不好 - 魔法数字
const secondsInDay = 86400
const maxRetries = 3
const cacheExpiry = 3600

// ✅ 好 - 使用常量
// src/constants/time.ts
export const TIME = {
  SECONDS_IN_MINUTE: 60,
  SECONDS_IN_HOUR: 3600,
  SECONDS_IN_DAY: 86400,
  MS_IN_SECOND: 1000
} as const

// src/constants/config.ts
export const CONFIG = {
  MAX_RETRIES: 3,
  CACHE_EXPIRY: 3600
} as const

// 使用
const secondsInDay = TIME.SECONDS_IN_DAY
const maxRetries = CONFIG.MAX_RETRIES
const cacheExpiry = CONFIG.CACHE_EXPIRY
```

### 7. 状态值

```typescript
// ❌ 不好 - 硬编码状态值
const status = 1  // 1 = pending, 2 = active, 3 = completed

// ✅ 好 - 使用枚举
// src/constants/enums.ts
export enum OrderStatus {
  PENDING = 1,
  ACTIVE = 2,
  COMPLETED = 3,
  CANCELLED = 4
}

export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest'
}

// 使用
const status = OrderStatus.PENDING
const role = UserRole.ADMIN

// 在比较时
if (status === OrderStatus.PENDING) {
  // 处理待处理状态
}
```

### 8. 路由路径

```typescript
// ❌ 不好 - 硬编码路由
router.push('/users')
router.push('/products/123')
router.push('/orders/edit/456')

// ✅ 好 - 使用常量
// src/constants/routes.ts
export const ROUTES = {
  HOME: '/',
  USERS: '/users',
  USER_DETAIL: (id: number) => `/users/${id}`,
  PRODUCTS: '/products',
  PRODUCT_DETAIL: (id: number) => `/products/${id}`,
  ORDERS: '/orders',
  ORDER_EDIT: (id: number) => `/orders/edit/${id}`
} as const

// 使用
router.push(ROUTES.USERS)
router.push(ROUTES.USER_DETAIL(123))
router.push(ROUTES.ORDER_EDIT(456))
```

---

## 📁 配置文件结构

### 1. 配置文件示例

```
src/
├── config/
│   ├── api.ts          # API 配置
│   ├── app.ts          # 应用配置
│   ├── storage.ts      # 存储配置
│   └── env.ts          # 环境配置
│
├── constants/
│   ├── api.ts          # API 常量
│   ├── enums.ts        # 枚举定义
│   ├── messages.ts     # 消息常量
│   ├── patterns.ts     # 正则表达式
│   ├── routes.ts       # 路由常量
│   ├── time.ts         # 时间常量
│   └── status.ts       # 状态常量
│
└── types/
    └── config.ts       # 配置类型定义
```

### 2. 配置类型定义

```typescript
// src/types/config.ts

// API 配置
export interface ApiConfig {
  baseURL: string
  timeout: number
  endpoints: {
    users: string
    products: string
    orders: string
  }
}

// 分页参数
export interface PaginationParams {
  pageNum: number
  pageSize: number
}

// 响应类型
export interface ApiResponse<T> {
  data: T
  total: number
  pageNum: number
  pageSize: number
}
```

### 3. 环境变量

```typescript
// .env 文件
VITE_API_BASE_URL=http://localhost:8080
VITE_API_TIMEOUT=10000

// src/config/env.ts
export const ENV = {
  isDev: import.meta.env.DEV,
  isProd: import.meta.env.PROD,
  apiBaseURL: import.meta.env.VITE_API_BASE_URL,
  apiTimeout: Number(import.meta.env.VITE_API_TIMEOUT) || 10000
}
```

---

## ✅ 硬编码检查清单

### 生成代码后，必须检查

#### API 相关
- [ ] 是否有硬编码的 API 地址？
- [ ] 是否有硬编码的 API 端点？
- [ ] 是否有硬编码的端口号？

#### 配置相关
- [ ] 是否有硬编码的超时时间？
- [ ] 是否有硬编码的分页大小？
- [ ] 是否有硬编码的重试次数？

#### 消息相关
- [ ] 是否有硬编码的错误消息？
- [ ] 是否有硬编码的提示消息？
- [ ] 是否有硬编码的验证消息？

#### 模式相关
- [ ] 是否有硬编码的正则表达式？
- [ ] 是否有硬编码的格式模板？

#### 数值相关
- [ ] 是否有魔法数字？
- [ ] 是否有硬编码的状态值？
- [ ] 是否有硬编码的路由路径？

#### 业务相关
- [ ] 是否有硬编码的业务规则？
- [ ] 是否有硬编码的限制值？
- [ ] 是否有硬编码的默认值？

---

## 🚫 常见错误

### 1. 在组件中硬编码

```vue
<!-- ❌ 不好 -->
<script>
export default {
  data() {
    return {
      pageSize: 20  // 硬编码
    }
  },
  methods: {
    async fetchUsers() {
      const res = await fetch('http://localhost:8080/api/users')  // 硬编码
      // ...
    }
  }
}
</script>

<!-- ✅ 好 -->
<script>
// constants/api.ts
// export const DEFAULT_PAGE_SIZE = 20
import { DEFAULT_PAGE_SIZE } from '@/constants/api'

export default {
  data() {
    return {
      pageSize: DEFAULT_PAGE_SIZE
    }
  }
}
</script>
```

### 2. 在工具函数中硬编码

```typescript
// ❌ 不好
function delay(ms: number) {
  return new Promise(resolve => setTimeout(resolve, 5000))  // 硬编码
}

// ✅ 好
// constants/time.ts
// export const DEFAULT_DELAY = 5000
import { DEFAULT_DELAY } from '@/constants/time'

function delay(ms: number = DEFAULT_DELAY) {
  return new Promise(resolve => setTimeout(resolve, ms))
}
```

### 3. 在类型定义中硬编码

```typescript
// ❌ 不好
interface User {
  status: 1 | 2 | 3  // 硬编码状态值
}

// ✅ 好
// constants/enums.ts
// export enum UserStatus { ACTIVE = 1, INACTIVE = 2, PENDING = 3 }
import { UserStatus } from '@/constants/enums'

interface User {
  status: UserStatus
}
```

---

## 📝 最佳实践

### 1. 创建常量文件

```typescript
// src/constants/index.ts
export * from './api'
export * from './enums'
export * from './messages'
export * from './patterns'
export * from './routes'
export * from './time'
```

### 2. 使用路径别名

```typescript
// ❌ 不好 - 相对路径
import { API_CONFIG } from '../../config/api'

// ✅ 好 - 路径别名
import { API_CONFIG } from '@/config/api'
```

### 3. 统一导出

```typescript
// ❌ 不好 - 混合导入
import { API_CONFIG } from '@/config/api'
import { ERROR_MESSAGES } from '@/constants/messages'

// ✅ 好 - 统一从 index 导入
import { API_CONFIG } from '@/constants'
import { ERROR_MESSAGES } from '@/constants'
```

### 4. 类型安全

```typescript
// ✅ 好 - 使用 as const 确保类型安全
export const API_ENDPOINTS = {
  USERS: '/users',
  PRODUCTS: '/products'
} as const

// 类型: Readonly<{ USERS: '/users', PRODUCTS: '/products' }>
```

