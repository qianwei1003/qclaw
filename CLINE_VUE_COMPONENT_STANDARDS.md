# Vue 2/3 组件设计规范

## 📋 概述

本文档定义了 Vue 2 和 Vue 3 组件的设计规范，确保生成的组件代码质量一致、可维护、可复用。

---

## 🎯 组件设计核心原则

### 1. 职责单一
- 一个组件只做一件事
- 组件应该可以独立使用
- 组件之间通过 Props 和 Events 通信

### 2. 接口清晰
- Props 必须有类型定义
- Props 必须有默认值（非 required 时）
- Props 必须有验证器（必要时）
- Events 必须有类型定义

### 3. 状态管理
- 使用 ref/reactive 管理响应式状态（Vue 3）
- 使用 data() 管理状态（Vue 2）
- 避免直接修改 Props

### 4. 可复用性
- 提取业务逻辑到 Composables/Mixins
- 提取通用逻辑到工具函数
- 组件应该可以参数化

---

## 📦 Vue 3 组件设计规范

### 1. 组件文件结构

```vue
<!-- 组件文件: src/components/business/UserCard.vue -->
<template>
  <!-- 模板内容 -->
</template>

<script setup lang="ts">
// 1. 类型导入
import type { User } from '@/types/user'

// 2. Props 定义
interface Props {
  user: User
  showAvatar?: boolean
  size?: 'small' | 'medium' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  showAvatar: true,
  size: 'medium'
})

// 3. Emits 定义
const emit = defineEmits<{
  click: [user: User]
  delete: [id: number]
  update: [user: User]
}>()

// 4. Composables 使用
const { isLoading, error, fetchUser } = useUser(props.user.id)

// 5. 计算属性
const avatarSize = computed(() => {
  const sizes = { small: 32, medium: 48, large: 64 }
  return sizes[props.size]
})

// 6. 方法
const handleClick = () => {
  emit('click', props.user)
}

const handleDelete = () => {
  emit('delete', props.user.id)
}

// 7. 生命周期
onMounted(() => {
  fetchUser()
})
</script>

<style scoped>
/* 样式内容 */
</style>

<!-- 8. 文档注释 -->
```

### 2. Props 设计规范

```typescript
// ✅ 好 - 完整的 Props 定义
interface Props {
  // 必填属性
  userId: number
  
  // 可选属性（带默认值）
  showActions?: boolean
  maxHeight?: string
  
  // 限制值域
  variant?: 'primary' | 'secondary' | 'danger'
  
  // 对象类型
  user?: User
  
  // 数组类型
  tags?: string[]
}

// 使用 withDefaults 设置默认值
withDefaults(defineProps<Props>(), {
  showActions: true,
  variant: 'primary',
  user: () => ({ id: 0, name: '' }),
  tags: () => []
})

// ❌ 不好 - 简单的 Props 定义
props: ['userId', 'user', 'showActions']
```

### 3. Emits 设计规范

```typescript
// ✅ 好 - 类型安全的 Emits
const emit = defineEmits<{
  // 事件名: [参数类型]
  select: [id: number]
  delete: [id: number]
  update: [user: User]
  change: [value: string, oldValue: string]
}>()

// 使用
emit('select', user.id)

// ❌ 不好 - 没有类型定义
this.$emit('select', user.id)  // 参数类型不确定
```

### 4. 组件命名规范

```typescript
// ✅ 好 - PascalCase 命名
export default {
  name: 'UserProfileCard',  // 组件名
}

// 使用
<UserProfileCard />

// ❌ 不好
export default {
  name: 'user-profile-card',  // 不符合规范
}
```

### 5. Props 验证

```typescript
// ✅ 好 - 完整的验证
props: {
  userId: {
    type: Number,
    required: true,
    validator: (value: number) => value > 0
  },
  user: {
    type: Object as PropType<User>,
    required: false,
    default: () => ({ id: 0, name: '' })
  },
  status: {
    type: String,
    required: false,
    default: 'active',
    validator: (value: string) => ['active', 'inactive', 'pending'].includes(value)
  }
}

// ❌ 不好 - 没有验证
props: {
  userId: Number,
  user: Object
}
```

---

## 📦 Vue 2 组件设计规范

### 1. 组件文件结构

```vue
<!-- 组件文件: src/components/business/UserCard.vue -->
<template>
  <!-- 模板内容 -->
</template>

<script>
import type { User } from '@/types/user'

export default {
  name: 'UserCard',
  
  // 1. Props 定义（带验证）
  props: {
    user: {
      type: Object as () => User,
      required: true
    },
    showAvatar: {
      type: Boolean,
      default: true
    },
    size: {
      type: String,
      default: 'medium',
      validator: (value) => ['small', 'medium', 'large'].includes(value)
    }
  },
  
  // 2. 数据
  data() {
    return {
      isLoading: false,
      error: null
    }
  },
  
  // 3. 计算属性
  computed: {
    avatarSize() {
      const sizes = { small: 32, medium: 48, large: 64 }
      return sizes[this.size]
    },
    
    fullName() {
      return `${this.user.firstName} ${this.user.lastName}`
    }
  },
  
  // 4. 方法
  methods: {
    handleClick() {
      this.$emit('click', this.user)
    },
    
    async handleDelete() {
      this.isLoading = true
      try {
        await this.$services.user.delete(this.user.id)
        this.$emit('delete', this.user.id)
      } catch (error) {
        this.error = error
      } finally {
        this.isLoading = false
      }
    }
  },
  
  // 5. 生命周期
  mounted() {
    this.fetchData()
  }
}
</script>

<style scoped>
/* 样式内容 */
</style>
```

### 2. Props 设计规范（Vue 2）

```javascript
// ✅ 好 - 完整的 Props 定义
props: {
  // 基础类型
  userId: {
    type: Number,
    required: true,
    validator: (value) => value > 0
  },
  
  // 对象类型
  user: {
    type: Object,
    required: false,
    default: () => ({ id: 0, name: '' })
  },
  
  // 数组类型
  tags: {
    type: Array,
    default: () => []
  },
  
  // 字符串
  variant: {
    type: String,
    default: 'primary',
    validator: (value) => ['primary', 'secondary', 'danger'].includes(value)
  }
}

// ❌ 不好 - 没有验证
props: ['userId', 'user', 'tags']
```

### 3. Emits 设计规范（Vue 2）

```javascript
// ✅ 好 - 在组件中明确发射的事件
export default {
  name: 'UserCard',
  
  methods: {
    handleSelect() {
      // 发射带参数的事件
      this.$emit('select', {
        id: this.user.id,
        name: this.user.name
      })
    },
    
    handleDelete() {
      // 确认后再发射
      if (confirm('确定要删除吗？')) {
        this.$emit('delete', this.user.id)
      }
    }
  }
}

// 使用
// <UserCard @select="handleSelect" @delete="handleDelete" />

// ❌ 不好 - 没有文档的事件
this.$emit('select', data)
```

### 4. Mixins 使用规范（Vue 2）

```javascript
// ✅ 好 - 提取到独立的 mixin 文件
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
      } finally {
        this.loading = false
      }
    }
  }
}

// 组件中使用
import userMixin from '@/mixins/userMixin'

export default {
  name: 'UserDetail',
  mixins: [userMixin],
  
  mounted() {
    this.fetchUser()
  }
}

// ❌ 不好 - 在组件中直接定义所有逻辑
export default {
  data() {
    return {
      user: null,
      loading: false,
      error: null
    }
  },
  // ... 100 行重复的逻辑
}
```

---

## 🎨 Vue 2/3 通用规范

### 1. 模板规范

```vue
<!-- ✅ 好 - 简洁的模板 -->
<template>
  <div class="user-card">
    <!-- 使用 v-if 处理条件 -->
    <div v-if="loading" class="loading">加载中...</div>
    
    <!-- 使用 v-else-if 处理错误 -->
    <div v-else-if="error" class="error">
      {{ error.message }}
    </div>
    
    <!-- 使用 v-else 显示内容 -->
    <div v-else class="content">
      <img 
        v-if="showAvatar" 
        :src="user.avatar" 
        :alt="user.name"
        class="avatar"
      />
      <div class="info">
        <h3>{{ user.name }}</h3>
        <p>{{ user.email }}</p>
      </div>
    </div>
    
    <!-- 使用 v-for 时必须有 key -->
    <div 
      v-for="item in items" 
      :key="item.id"
      class="item"
    >
      {{ item.name }}
    </div>
  </div>
</template>

<!-- ❌ 不好 - 嵌套过深 -->
<template>
  <div>
    <div v-if="show">
      <div v-for="item in items">
        <div v-if="item.active">
          <div v-if="item.role === 'admin'">
            <!-- 嵌套太深 -->
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
```

### 2. 样式规范

```vue
<style scoped>
/* ✅ 好 - 使用 BEM 命名 */
.user-card {
  &__avatar {
    width: 48px;
    height: 48px;
  }
  
  &__info {
    padding: 8px;
  }
  
  &--active {
    border-color: green;
  }
}

/* ✅ 好 - 使用 CSS 变量 */
.button {
  background-color: var(--primary-color);
  color: var(--text-color);
}

/* ✅ 好 - 响应式设计 */
.container {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
  
  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

/* ❌ 不好 - 全局样式污染 */
<style>
/* 没有 scoped */
.class {
  color: red;
}
</style>
```

### 3. 事件处理规范

```vue
<script setup lang="ts">
// ✅ 好 - 事件处理函数命名规范
const onButtonClick = () => {
  emit('click')
}

const onInputChange = (event: Event) => {
  const value = (event.target as HTMLInputElement).value
  emit('update:value', value)
}

const onFormSubmit = () => {
  if (validateForm()) {
    emit('submit', formData)
  }
}

// ❌ 不好 - 命名不规范
const handleClick = () => {}      // 不知道处理什么事件
const click = () => {}           // 没有前缀
const doStuff = () => {}        // 不清晰的命名
</script>

<template>
  <!-- ✅ 好 - 使用规范的事件名 -->
  <button @click="onButtonClick">点击</button>
  <input @input="onInputChange" />
  <form @submit.prevent="onFormSubmit" />
  
  <!-- ❌ 不好 -->
  <button @click="handleClick">点击</button>
</template>
```

---

## ✅ 组件检查清单

### 生成组件后，必须检查

- [ ] 组件有 `name` 属性（使用 PascalCase）
- [ ] Props 有完整的类型定义
- [ ] Props 有默认值（非 required 时）
- [ ] Props 有验证器（必要时）
- [ ] Emits 有定义
- [ ] 没有直接修改 Props
- [ ] 使用 v-if 时有 v-else 或 v-show 处理其他状态
- [ ] 使用 v-for 时有 :key
- [ ] 模板没有嵌套过深（> 3 层）
- [ ] 使用 scoped 样式
- [ ] 样式使用 BEM 或 CSS 变量
- [ ] 事件处理函数命名清晰（on + 动作）
- [ ] 复杂逻辑提取到 Composables/Mixins
- [ ] 组件可以独立使用
- [ ] 组件有适当的注释

