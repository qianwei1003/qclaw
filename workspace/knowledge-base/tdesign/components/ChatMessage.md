# ChatMessage 对话消息体

> 来源: https://tdesign.tencent.com/chat/components/chat-message  
> 整理时间: 2026-03-21

---

## 简介

用于在聊天对话中显示单个消息项。可以展示用户的头像、昵称、时间、聊天内容，支持多种消息状态和样式变体。

---

## 基础样式

### 气泡样式

对话消息气泡样式，分为基础（base）、线框（outline）、文字（text），默认为文字。

```vue
<template>
  <t-space direction="vertical" style="width: 100%">
    <!-- 默认文字样式 -->
    <t-chat-message :content="message.content" :role="message.role" />
    <!-- 基础气泡样式 -->
    <t-chat-message variant="base" :content="message.content" :role="message.role" />
    <!-- 线框气泡样式 -->
    <t-chat-message variant="outline" :content="message.content" :role="message.role" />
  </t-space>
</template>

<script setup>
const message = {
  role: 'user',
  content: [
    {
      type: 'text',
      data: '牛顿第一定律是否适用于所有参考系？',
    },
  ],
};
</script>
```

---

### 可配置角色、头像、昵称、位置

```vue
<template>
  <t-space direction="vertical" style="width: 100%">
    <!-- 用户消息（右侧） -->
    <t-chat-message
      avatar="https://tdesign.gtimg.com/site/avatar.jpg"
      datetime="今天16:38"
      name="张三"
      role="user"
      :content="messages.user.content"
    />
    <!-- AI 消息（左侧） -->
    <t-chat-message
      avatar="https://tdesign.gtimg.com/site/chat-avatar.png"
      datetime="今天16:43"
      name="TDesignAI"
      role="assistant"
      :content="messages.ai.content"
    />
    <!-- 自定义位置 -->
    <t-chat-message placement="right" variant="base" role="user" :content="messages.user.content" />
    <t-chat-message placement="left" role="assistant" :content="messages.ai.content" />
    <!-- 系统消息 -->
    <t-chat-message :content="messages.system.content" role="system" />
  </t-space>
</template>

<script setup>
const messages = {
  ai: {
    id: '11111',
    role: 'assistant',
    content: [
      {
        type: 'text',
        data: '牛顿第一定律并不适用于所有参考系，它只适用于惯性参考系。',
      },
    ],
  },
  user: {
    id: '22222',
    role: 'user',
    content: [
      {
        type: 'text',
        data: '牛顿第一定律是否适用于所有参考系？',
      },
    ],
  },
  system: {
    id: '33333',
    role: 'system',
    content: [
      {
        type: 'text',
        data: '模型由 hunyuan 变为 GPT4',
      },
    ],
  },
};
</script>
```

---

### 消息状态

```vue
<template>
  <t-space direction="vertical" style="width: 100%">
    <!-- 加载状态（4种动画） -->
    <t-chat-message
      v-for="opt in animationOptions"
      :key="opt.value"
      avatar="https://tdesign.gtimg.com/site/chat-avatar.png"
      datetime="今天16:38"
      :animation="opt.value"
      name="TDesignAI"
      role="assistant"
      :status="'pending'"
    />
    <!-- 出错状态 -->
    <t-chat-message
      avatar="https://tdesign.gtimg.com/site/chat-avatar.png"
      role="assistant"
      :content="[{ type: 'text', data: '出错了' }]"
      status="error"
    />
  </t-space>
</template>

<script setup>
const animationOptions = [
  { label: 'skeleton', value: 'skeleton' },
  { label: 'moving', value: 'moving' },
  { label: 'gradient', value: 'gradient' },
  { label: 'dot', value: 'dot' },
];
</script>
```

---

## 消息内容渲染

### 内置支持的消息内容类型

通过配置 `content` 数组中的 `type` 属性，可以渲染内置的几种消息内容：

| type | 说明 | 配置项 |
|------|------|--------|
| `text` | 纯文本 | - |
| `markdown` | Markdown 格式内容 | `markdownProps` |
| `thinking` | 思考过程 | `thinking.maxHeight`, `thinking.collapsed` |
| `search` | 搜索结果/资料来源 | `search.expandable` |
| `suggestion` | 建议问题 | - |
| `attachment` | 文件附件 | `attachments.onFileClick` |
| `image` / `imageview` | 图片 | - |

```vue
<template>
  <t-space direction="vertical" style="width: 100%">
    <!-- 文件附件 -->
    <t-chat-message
      variant="base"
      :content="userMessage1.content"
      :role="userMessage1.role"
      :chat-content-props="{
        attachments: {
          onFileClick: (e) => {
            console.log('自定义附件点击逻辑', e.detail);
          },
        },
      }"
    />

    <!-- 思考过程 + 搜索结果 + Markdown + 建议问题 -->
    <t-chat-message
      :content="aiMessages.content"
      :role="aiMessages.role"
      animation="gradient"
      :chat-content-props="{
        thinking: { maxHeight: 100, collapsed: true },
        search: { expandable: true },
      }"
      :handle-actions="onActions"
    />
  </t-space>
</template>

<script setup>
const userMessage1 = {
  role: 'user',
  status: 'complete',
  content: [
    { type: 'text', data: '分析以下内容，总结一篇广告策划方案' },
    {
      type: 'attachment',
      data: [
        { fileType: 'doc', name: 'demo.docx', url: 'https://example.com/demo.docx', size: 12312 },
        { fileType: 'pdf', name: 'demo2.pdf', url: 'https://example.com/demo.pdf', size: 34333 },
      ],
    },
  ],
};

const aiMessages = {
  role: 'assistant',
  status: 'complete',
  content: [
    // 思考过程
    {
      type: 'thinking',
      status: 'complete',
      data: {
        title: '已完成思考（耗时3秒）',
        text: '好的，我现在需要回答用户关于对比近3年当代偶像爱情剧并总结创作经验的问题...',
      },
    },
    // 搜索结果
    {
      type: 'search',
      data: {
        title: '搜索到2篇相关内容',
        references: [
          { title: '《传媒内参2024剧集市场分析报告》', url: '' },
          { title: '2024年国产剧市场分析', url: '' },
        ],
      },
    },
    // Markdown 内容
    {
      type: 'markdown',
      data: '**数据支撑：** 据《传媒内参2024报告》，2024年偶像爱情剧完播率`提升12%`。',
    },
    // 建议问题
    {
      type: 'suggestion',
      data: [
        { title: '近3年偶像爱情剧的市场反馈如何', prompt: '近3年偶像爱情剧的市场反馈如何' },
        { title: '偶像爱情剧的观众群体分析', prompt: '偶像爱情剧的观众群体分析' },
      ],
    },
  ],
};

const onActions = {
  suggestion: (content) => {
    console.log('suggestionItem', content);
  },
  searchItem: (content, event) => {
    event.preventDefault();
    event.stopPropagation();
    console.log('searchItem', content);
  },
};
</script>
```

---

### 消息内容自定义

通过 `#content` 插槽实现自定义渲染（如图表组件）：

```vue
<template>
  <t-chat-message
    variant="text"
    avatar="https://tdesign.gtimg.com/site/chat-avatar.png"
    name="TDesignAI"
    role="assistant"
  >
    <template #content>
      <template v-for="(contentItem, contentIndex) in message.content" :key="contentIndex">
        <!-- 文本内容 -->
        <t-chat-content v-if="contentItem.type === 'text'" :content="contentItem.data" />
        <!-- 自定义图表组件 -->
        <MyChartComponent
          v-else-if="contentItem.type === 'chart'"
          :chart-type="contentItem.data.chartType"
          :options="contentItem.data.options"
        />
      </template>
    </template>
  </t-chat-message>
</template>
```

---

### 消息操作栏

通过 `#actionbar` 插槽植入操作栏：

```vue
<template>
  <t-chat-message
    variant="text"
    avatar="https://tdesign.gtimg.com/site/chat-avatar.png"
    name="TDesignAI"
    :role="message.role"
    :content="message.content"
  >
    <!-- 植入操作栏插槽 -->
    <template #actionbar>
      <t-chat-actionbar
        :comment="comment"
        :content="message.content[0].data"
        :action-bar="['good', 'bad', 'replay', 'copy']"
        @actions="handleActions"
      />
    </template>
  </t-chat-message>
</template>
```

---

## API

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| role | `'user' \| 'assistant' \| 'system'` | - | 消息角色 |
| content | `Array<ContentItem>` | - | 消息内容数组 |
| variant | `'text' \| 'base' \| 'outline'` | `'text'` | 气泡样式 |
| placement | `'left' \| 'right'` | - | 消息位置 |
| avatar | string | - | 头像 URL |
| name | string | - | 昵称 |
| datetime | string | - | 时间 |
| status | `'pending' \| 'complete' \| 'error' \| 'stop'` | - | 消息状态 |
| animation | `'skeleton' \| 'moving' \| 'gradient' \| 'dot'` | `'skeleton'` | 加载动画类型 |
| chat-content-props | object | - | 内容类型的配置项 |
| handle-actions | object | - | 操作回调（suggestion、searchItem 等） |
| allow-content-segment-custom | boolean | false | 是否允许内容分段自定义插槽 |

### Slots

| 插槽 | 参数 | 说明 |
|------|------|------|
| `#content` | - | 自定义消息内容 |
| `#actionbar` | - | 自定义操作栏 |
| `#avatar` | - | 自定义头像 |

### chatContentProps 配置

```javascript
chatContentProps = {
  thinking: {
    maxHeight: 200,    // 思考过程最大高度
    collapsed: false,  // 是否折叠
    layout: 'block',   // 展示样式：border | block
  },
  search: {
    expandable: true,  // 是否可展开
    useCollapse: true, // 是否使用折叠
    collapsed: false,  // 是否折叠
  },
  markdown: {
    options: {
      themeSettings: {
        codeBlockTheme: 'light', // 代码块主题
      },
    },
  },
  attachments: {
    onFileClick: (e) => {},  // 附件点击回调
  },
}
```

---

### ContentItem 类型定义

```typescript
// 文本内容
interface TextContent {
  type: 'text';
  data: string;
  status?: 'pending' | 'streaming' | 'complete';
}

// Markdown 内容
interface MarkdownContent {
  type: 'markdown';
  data: string;
  status?: 'pending' | 'streaming' | 'complete';
}

// 思考过程
interface ThinkingContent {
  type: 'thinking';
  data: { title: string; text: string };
  status?: 'pending' | 'streaming' | 'complete';
}

// 搜索结果
interface SearchContent {
  type: 'search';
  data: {
    title: string;
    references: Array<{ title: string; url: string; content?: string }>;
  };
}

// 建议问题
interface SuggestionContent {
  type: 'suggestion';
  data: Array<{ title: string; prompt: string }>;
}

// 附件
interface AttachmentContent {
  type: 'attachment';
  data: Array<{ name: string; url: string; size: number; fileType: string }>;
}

// 联合类型
type ContentItem = TextContent | MarkdownContent | ThinkingContent | SearchContent | SuggestionContent | AttachmentContent;
```

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chat-message
- ChatActionbar: https://tdesign.tencent.com/chat/components/chat-actionbar
- ChatThinking: https://tdesign.tencent.com/chat/components/chat-thinking
