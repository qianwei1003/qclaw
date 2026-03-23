# ChatContent 对话正文

> 来源: https://tdesign.tencent.com/chat/components/chat-content  
> 整理时间: 2026-03-21

---

## 简介

支持 Markdown 格式的渲染。对大模型返回的 Markdown 数据自动渲染，也支持纯文本展示。

---

## 默认聊天格式（Markdown 渲染）

对大模型返回的 Markdown 数据自动渲染，支持标题、列表、代码块、引用、链接等所有标准 Markdown 语法。

```vue
<template>
  <t-chat-content :content="content" :markdown-props="markdownProps" />
</template>

<script setup lang="ts">
const markdownProps = {
  options: {
    themeSettings: {
      // 代码块主题设置，默认是 'light' | 'dark'
      codeBlockTheme: 'dark',
    },
  },
};

const doc = `
# This is TDesign

## This is TDesign

### This is TDesign

#### This is TDesign

The point of reference-style links is not that they're easier to write.

> This is a blockquote with two paragraphs. Lorem ipsum dolor sit amet.

an example | *an example* | **an example**

1. Bird
1. McHale
1. Parish

- Red
- Green
- Blue

This is [an example](http://example.com/ "Title") inline link.

<http://example.com/>

\`\`\`bash
$ npm i tdesign-vue-next
\`\`\`

---

\`\`\`javascript
import { createApp } from 'vue';
import App from './app.vue';
const app = createApp(App);
app.use(TDesignChat);
\`\`\`
`;

const content = {
  type: 'markdown',
  data: doc,
};
</script>
```

---

## 纯文本聊天

用户发送的消息保持默认格式显示，没有高亮效果：

```vue
<template>
  <t-chat-content :content="content" />
</template>

<script setup lang="ts">
const ask = `import TDesign from 'tdesign-vue-next';
// 引入tdesign组件库
app.use(TDesign).use(router).mount('#app');`;

const content = {
  type: 'text',
  data: ask,
};
</script>
```

---

## API

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| content | `ContentItem` | - | 内容对象，包含 `type` 和 `data` |
| role | `'user' \| 'assistant'` | - | 消息角色，影响渲染样式 |
| markdown-props | object | - | Markdown 渲染配置 |

### content 对象结构

```typescript
// 文本类型
interface TextContent {
  type: 'text';
  data: string;
}

// Markdown 类型
interface MarkdownContent {
  type: 'markdown';
  data: string;
}

// 联合类型
type ContentItem = TextContent | MarkdownContent;
```

### markdownProps 配置

```javascript
const markdownProps = {
  options: {
    themeSettings: {
      codeBlockTheme: 'light', // 代码块主题：'light' | 'dark'
    },
    // 其他 CherryMarkdown 配置
  },
};
```

---

## 与 ChatMessage 的关系

`ChatContent` 是 `ChatMessage` 内部使用的内容渲染组件。

| 使用方式 | 说明 |
|---------|------|
| 直接使用 `ChatMessage` | 通过 `content` 数组传入，自动处理多种类型（thinking、search、suggestion 等） |
| 直接使用 `ChatContent` | 只处理 `text` 和 `markdown` 两种基础类型，适合在自定义插槽中使用 |

```vue
<!-- 在 ChatList 的 content 插槽中使用 -->
<template #content="{ item, index }">
  <template v-for="(contentItem, contentIndex) in item.content" :key="contentIndex">
    <!-- 思考过程单独处理 -->
    <t-chat-thinking
      v-if="contentItem.type === 'thinking'"
      :status="contentItem.status"
      :content="contentItem.data"
    />
    <!-- 其他内容用 ChatContent 渲染 -->
    <t-chat-content
      v-else
      :content="contentItem.data"
      :role="item.role"
    />
  </template>
</template>
```

---

## 支持的内容类型

| 类型 | 说明 | 组件 |
|------|------|------|
| `text` | 纯文本 | ChatContent |
| `markdown` | Markdown 格式 | ChatContent → ChatMarkdown |
| `thinking` | 思考过程 | ChatThinking |
| `search` | 搜索结果 | 内置渲染 |
| `suggestion` | 建议问题 | 内置渲染 |
| `attachment` | 文件附件 | Attachments |
| `image` / `imageview` | 图片 | 内置渲染 |

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chat-content
- ChatMessage: https://tdesign.tencent.com/chat/components/chat-message
- ChatMarkdown: https://tdesign.tencent.com/chat/components/chat-markdown
- CherryMarkdown: https://github.com/Tencent/CherryMarkdown
