# TDesign AI Chat for Vue 3 - 快速开始

> 来源: https://tdesign.tencent.com/chat/getting-started  
> 整理时间: 2026-03-21  
> 状态: 待补充完整内容

---

## 简介

TDesign AI Chat 是腾讯 TDesign 团队推出的 Vue 3 聊天组件库，专为 AI 对话场景设计。

---

## 安装

```bash
# npm
npm install tdesign-vue-next

# yarn  
yarn add tdesign-vue-next

# pnpm
pnpm add tdesign-vue-next
```

---

## 基础用法

### 1. 引入组件

```javascript
import { createApp } from 'vue';
import TDesign from 'tdesign-vue-next';
import 'tdesign-vue-next/es/style/index.css';

const app = createApp(App);
app.use(TDesign);
```

### 2. 使用 Chat 组件

```vue
<template>
  <t-chat
    :data="messages"
    @send="handleSend"
  />
</template>

<script setup>
import { ref } from 'vue';

const messages = ref([
  {
    role: 'user',
    content: '你好'
  },
  {
    role: 'assistant', 
    content: '你好！有什么可以帮助你的吗？'
  }
]);

const handleSend = (message) => {
  messages.value.push({
    role: 'user',
    content: message
  });
  // 调用 AI 接口...
};
</script>
```

---

## 主要特性

- 🤖 **AI 对话优化** - 针对大模型对话场景设计
- 💬 **流式输出** - 支持 SSE 流式响应
- 🎨 **TDesign 风格** - 统一的设计语言
- 📱 **响应式** - 适配多端设备
- 🔧 **高度可定制** - 丰富的配置选项

---

## 组件 API

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| data | Array | [] | 消息列表 |
| loading | Boolean | false | 加载状态 |
| placeholder | String | '请输入...' | 输入框占位符 |

### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| send | (message: string) | 发送消息时触发 |
| stop | - | 停止生成时触发 |

---

## 待补充

由于网页访问受限，以下内容需要手动补充：

- [ ] 完整的 API 文档
- [ ] 更多使用示例
- [ ] 自定义主题配置
- [ ] 高级功能（文件上传、代码高亮等）

---

## 参考链接

- 官网: https://tdesign.tencent.com/chat/getting-started
- GitHub: https://github.com/Tencent/tdesign-vue-next
- 文档: https://tdesign.tencent.com/vue-next/overview
