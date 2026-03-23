# Cline 项目结构规范

## 📁 完整的项目结构

```
my-vue-project/
├── src/
│   ├── components/                    # 可复用组件
│   │   ├── common/                   # 通用组件
│   │   │   ├── Button.vue
│   │   │   ├── Input.vue
│   │   │   ├── Modal.vue
│   │   │   ├── Loading.vue
│   │   │   ├── Empty.vue
│   │   │   └── Error.vue
│   │   ├── business/                 # 业务组件
│   │   │   ├── UserCard.vue
│   │   │   ├── ProductList.vue
│   │   │   └── OrderForm.vue
│   │   └── layout/                   # 布局组件
│   │       ├── Header.vue
│   │       ├── Sidebar.vue
│   │       ├── Footer.vue
│   │       └── MainLayout.vue
│   │
│   ├── views/                        # 页面组件（路由对应）
│   │   ├── home/
│   │   │   ├── HomePage.vue
│   │   │   └── index.ts
│   │   ├── user/
│   │   │   ├── UserListPage.vue
│   │   │   ├── UserDetailPage.vue
│   │   │   └── index.ts
│   │   ├── product/
│   │   │   ├── ProductListPage.vue
│   │   │   ├── ProductDetailPage.vue
│   │   │   └── index.ts
│   │   └── 404.vue
│   │
│   ├── composables/                  # Vue 3 组合式函数
│   │   ├── useUserList.ts           # 用户列表逻辑
│   │   ├── useUserForm.ts           # 用户表单逻辑
│   │   ├── usePagination.ts         # 分页逻辑
│   │   ├── useAsync.ts              # 异步操作逻辑
│   │   └── index.ts                 # 导出所有 composables
│   │
│   ├── hooks/                        # 自定义 Hooks（Vue 2 用 mixins）
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   ├── useThrottle.ts
│   │   └── index.ts
│   │
│   ├── services/                     # 业务逻辑层
│   │   ├── api/                     # API 调用
│   │   │   ├── user.ts             # 用户相关 API
│   │   │   ├── product.ts          # 产品相关 API
│   │   │   ├── order.ts            # 订单相关 API
│   │   │   └── index.ts            # 导出所有 API
│   │   ├── auth/                   # 认证服务
│   │   │   ├── authService.ts
│   │   │   ├── tokenService.ts
│   │   │   └── index.ts
│   │   ├── storage/                # 存储服务
│   │   │   ├── localStorageService.ts
│   │   │   ├── sessionStorageService.ts
│   │   │   └── index.ts
│   │   ├── user/                   # 用户领域服务
│   │   │   ├── userService.ts
│   │   │   └── index.ts
│   │   └── index.ts                # 导出所有服务
│   │
│   ├── stores/                      # 状态管理（Pinia/Vuex）
│   │   ├── modules/
│   │   │   ├── user.ts             # 用户状态
│   │   │   ├── product.ts          # 产品状态
│   │   │   ├── order.ts            # 订单状态
│   │   │   └── app.ts              # 应用状态
│   │   ├── index.ts                # 创建 store
│   │   └── types.ts                # store 类型定义
│   │
│   ├── utils/                       # 工具函数
│   │   ├── validators/             # 验证函数
│   │   │   ├── email.ts
│   │   │   ├── phone.ts
│   │   │   ├── password.ts
│   │   │   └── index.ts
│   │   ├── formatters/             # 格式化函数
│   │   │   ├── date.ts
│   │   │   ├── currency.ts
│   │   │   ├── number.ts
│   │   │   └── index.ts
│   │   ├── helpers/                # 辅助函数
│   │   │   ├── array.ts
│   │   │   ├── object.ts
│   │   │   ├── string.ts
│   │   │   └── index.ts
│   │   ├── request.ts              # HTTP 请求工具
│   │   ├── logger.ts               # 日志工具
│   │   └── index.ts                # 导出所有工具
│   │
│   ├── constants/                   # 常量定义
│   │   ├── api.ts                  # API 相关常量
│   │   │   ├── API_BASE_URL
│   │   │   ├── API_TIMEOUT
│   │   │   └── API_ENDPOINTS
│   │   ├── enums.ts                # 枚举定义
│   │   │   ├── UserRole
│   │   │   ├── OrderStatus
│   │   │   └── ProductCategory
│   │   ├── messages.ts             # 消息常量
│   │   │   ├── SUCCESS_MESSAGES
│   │   │   ├── ERROR_MESSAGES
│   │   │   └── VALIDATION_MESSAGES
│   │   ├── user.ts                 # 用户相关常量
│   │   ├── product.ts              # 产品相关常量
│   │   ├── order.ts                # 订单相关常量
│   │   └── index.ts                # 导出所有常量
│   │
│   ├── types/                       # TypeScript 类型定义
│   │   ├── index.ts                # 导出所有类型
│   │   ├── api.ts                  # API 相关类型
│   │   │   ├── ApiResponse
│   │   │   ├── ApiError
│   │   │   └── PaginationParams
│   │   ├── models.ts               # 数据模型
│   │   │   ├── User
│   │   │   ├── Product
│   │   │   └── Order
│   │   ├── user.ts                 # 用户相关类型
│   │   ├── product.ts              # 产品相关类型
│   │   └── order.ts                # 订单相关类型
│   │
│   ├── styles/                      # 全局样式
│   │   ├── variables.css            # CSS 变量
│   │   │   ├── --primary-color
│   │   │   ├── --secondary-color
│   │   │   ├── --spacing-unit
│   │   │   └── --font-family
│   │   ├── reset.css                # 重置样式
│   │   ├── global.css               # 全局样式
│   │   ├── animations.css           # 动画
│   │   └── responsive.css           # 响应式
│   │
│   ├── config/                      # 配置文件
│   │   ├── api.ts                  # API 配置
│   │   │   ├── baseURL
│   │   │   ├── timeout
│   │   │   └── headers
│   │   ├── app.ts                  # 应用配置
│   │   │   ├── appName
│   │   │   ├── version
│   │   │   └── environment
│   │   ├── env.ts                  # 环境配置
│   │   │   ├── isDev
│   │   │   ├── isProd
│   │   │   └── apiUrl
│   │   └── index.ts                # 导出所有配置
│   │
│   ├── router/                      # 路由配置
│   │   ├── index.ts                # 路由实例
│   │   ├── routes.ts               # 路由定义
│   │   └── guards.ts               # 路由守卫
│   │
│   ├── plugins/                     # Vue 插件
│   │   ├── axios.ts                # Axios 插件
│   │   ├── i18n.ts                 # 国际化插件
│   │   └── index.ts                # 注册所有插件
│   │
│   ├── main.ts                      # 应用入口
│   └── App.vue                      # 根组件
│
├── tests/                           # 测试文件
│   ├── unit/                       # 单元测试
│   │   ├── utils/
│   │   ├── services/
│   │   └── composables/
│   ├── components/                 # 组件测试
│   ├── e2e/                        # 端到端测试
│   └── setup.ts                    # 测试配置
│
├── public/                          # 静态资源
│   ├── images/
│   ├── icons/
│   └── favicon.ico
│
├── .env                             # 环境变量（本地）
├── .env.development                 # 开发环境变量
├── .env.production                  # 生产环境变量
├── .env.example                     # 环境变量示例
├── .eslintrc.js                     # ESLint 配置
├── .prettierrc.js                   # Prettier 配置
├── tsconfig.json                    # TypeScript 配置
├── vite.config.ts                   # Vite 配置
├── vitest.config.ts                 # Vitest 配置
├── package.json                     # 项目依赖
├── README.md                        # 项目文档
└── .gitignore                       # Git 忽略文件
```

---

## 📝 文件命名规范

### 组件文件

```
src/components/
├── common/
│   ├── Button.vue                  # ✅ PascalCase
│   ├── Input.vue
│   └── Modal.vue
├── business/
│   ├── UserCard.vue
│   ├── ProductList.vue
│   └── OrderForm.vue
└── layout/
    ├── Header.vue
    ├── Sidebar.vue
    └── MainLayout.vue
```

**规则**:
- 文件名: `PascalCase.vue`
- 组件名: `PascalCase`
- 导出: `export default { name: 'ComponentName' }`

### 工具函数文件

```
src/utils/
├── validators/
│   ├── email.ts                    # ✅ camelCase
│   ├── phone.ts
│   └── password.ts
├── formatters/
│   ├── date.ts
│   ├── currency.ts
│   └── number.ts
└── helpers/
    ├── array.ts
    ├── object.ts
    └── string.ts
```

**规则**:
- 文件名: `camelCase.ts`
- 函数名: `camelCase`
- 导出: `export function functionName() {}`

### 常量文件

```
src/constants/
├── api.ts                          # ✅ camelCase
├── enums.ts
├── messages.ts
├── user.ts
├── product.ts
└── order.ts
```

**规则**:
- 文件名: `camelCase.ts`
- 常量名: `UPPER_SNAKE_CASE`
- 导出: `export const API_BASE_URL = '...'`

### 类型文件

```
src/types/
├── index.ts                        # ✅ 导出所有类型
├── api.ts
├── models.ts
├── user.ts
├── product.ts
└── order.ts
```

**规则**:
- 文件名: `camelCase.ts` 或 `[name].types.ts`
- 类型名: `PascalCase`
- 导出: `export interface TypeName {}`

### 服务文件

```
src/services/
├── api/
│   ├── user.ts                    # ✅ camelCase
│   ├── product.ts
│   └── order.ts
├── auth/
│   ├── authService.ts
│   └── tokenService.ts
└── storage/
    ├── localStorageService.ts
    └── sessionStorageService.ts
```

**规则**:
- 文件名: `camelCase.ts` 或 `[name]Service.ts`
- 类名: `PascalCase`
- 导出: `export class ServiceName {}`

### 测试文件

```
src/
├── utils/
│   ├── formatters/
│   │   ├── date.ts
│   │   └── date.spec.ts           # ✅ [name].spec.ts
│   └── validators/
│       ├── email.ts
│       └── email.test.ts          # ✅ [name].test.ts
```

**规则**:
- 文件名: `[name].spec.ts` 或 `[name].test.ts`
- 测试用例: `describe()` 和 `it()`

---

## 🎯 导入导出规范

### 相对路径导入

```typescript
// ✅ 好 - 使用相对路径
import { Button } from '../common/Button.vue'
import { formatDate } from '../../utils/formatters/date'
import type { User } from '../../types/user'

// ❌ 不好 - 路径过长
import { Button } from '../../../components/common/Button.vue'
```

### 路径别名导入

```typescript
// ✅ 好 - 使用路径别名
import { Button } from '@/components/common/Button.vue'
import { formatDate } from '@/utils/formatters/date'
import type { User } from '@/types/user'
import { API_BASE_URL } from '@/constants/api'

// ❌ 不好 - 混合使用
import { Button } from '@/components/common/Button.vue'
import { formatDate } from '../utils/formatters/date'
```

### 命名导出 vs 默认导出

```typescript
// ✅ 好 - 使用命名导出
export function formatDate(date: Date): string {}
export interface User {}
export const API_BASE_URL = '...'

// 导入
import { formatDate, User, API_BASE_URL } from '@/utils'

// ❌ 不好 - 使用默认导出
export default function formatDate(date: Date): string {}

// 导入
import formatDate from '@/utils/formatDate'
```

### 导出索引文件

```typescript
// src/utils/index.ts
export * from './formatters/date'
export * from './formatters/currency'
export * from './validators/email'
export * from './validators/phone'
export * from './helpers/array'

// 使用
import { formatDate, formatCurrency, validateEmail } from '@/utils'
```

---

## 📂 目录组织原则

### 1. 按功能组织

```
src/
├── user/                           # 用户功能模块
│   ├── components/
│   ├── services/
│   ├── types/
│   ├── constants/
│   └── utils/
├── product/                        # 产品功能模块
│   ├── components/
│   ├── services/
│   ├── types/
│   ├── constants/
│   └── utils/
└── order/                          # 订单功能模块
    ├── components/
    ├── services/
    ├── types/
    ├── constants/
    └── utils/
```

### 2. 按类型组织（推荐）

```
src/
├── components/                     # 所有组件
├── services/                       # 所有服务
├── types/                          # 所有类型
├── constants/                      # 所有常量
└── utils/                          # 所有工具
```

---

## ✅ 检查清单

- [ ] 所有组件文件都在 `components/` 目录
- [ ] 所有页面都在 `views/` 目录
- [ ] 所有工具函数都在 `utils/` 目录
- [ ] 所有服务都在 `services/` 目录
- [ ] 所有常量都在 `constants/` 目录
- [ ] 所有类型都在 `types/` 目录
- [ ] 所有样式都在 `styles/` 目录
- [ ] 文件命名遵循规范
- [ ] 导入使用路径别名
- [ ] 没有循环导入
- [ ] 没有过深的目录嵌套
- [ ] 相关文件放在一起

