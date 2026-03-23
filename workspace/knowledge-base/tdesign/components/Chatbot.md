# Chatbot 智能对话组件

> 来源: https://tdesign.tencent.com/chat/components/chatbot  
> 整理时间: 2026-03-21

---

## 简介

高度封装且功能完备的一体化智能对话组件，专为快速集成标准AI应用而设计。

---

## 阅读指引

Chatbot 作为高度封装且功能完备的一体化智能对话组件，专为快速集成标准 AI 应用而设计。组件内置了完整的状态管理、SSE 流式传输、消息渲染和交互逻辑，支持多种业务场景，包括智能客服、问答系统、代码助手、任务规划等。

本文档按照**从简单到复杂**的顺序组织，建议按以下路径循序渐进阅读：

1. **快速开始** - 5 分钟上手，了解最基本的配置
2. **基础用法** - 了解常用功能特性，结合各项示例掌握数据处理、消息配置、自定义渲染等主要功能
3. **场景示例** - 参考实战案例，快速应用到项目中

> 💡 **示例说明**：所有示例都基于 Mock SSE 服务，您可以打开浏览器开发者工具（F12），切换到 Network（网络）标签，查看接口的请求和响应数据，了解数据格式。

---

## 快速开始

最简单的 Chatbot 配置示例，只需配置 `endpoint` 和 `onMessage` 即可实现一个可用的对话界面。

```vue
<template>
  <div>
    <t-chatbot :chat-service-config="chatServiceConfig" />
  </div>
</template>

<script setup lang="ts">
import type { SSEChunkData, AIMessageContent, ChatServiceConfig } from '@tdesign-vue-next/chat';

/**
 * 快速开始示例
 * 
 * 学习目标：
 * - 了解 Chatbot 组件的最小配置
 * - 理解 endpoint 和 onMessage 的作用
 * - 实现一个基于SSE流式传输的最简可用的对话界面
 */

// 聊天服务配置
const chatServiceConfig: ChatServiceConfig = {
  // 对话服务地址
  endpoint: 'https://1257786608-9i9j1kpa67.ap-guangzhou.tencentscf.com/sse/normal',
  // 开启流式传输
  stream: true,
  // 解析后端返回的数据，转换为组件所需格式
  onMessage: (chunk: SSEChunkData): AIMessageContent => {
    const { ...rest } = chunk.data as any;
    return {
      type: 'markdown',
      data: rest?.msg || '',
    };
  },
};
</script>
```

---

## 基础用法

### 初始化消息

使用 `defaultMessages` 设置静态初始化消息，或通过 `setMessages` 实例方法动态加载历史消息。

```vue
<template>
  <div>
    <!-- 操作按钮 -->
    <div class="quick-actions">
      <div class="actions-title">快捷指令：</div>
      <div class="actions-buttons">
        <t-button variant="outline" size="small" :disabled="hasHistory" @click="loadHistory">
          加载历史消息
        </t-button>
        <t-button variant="outline" size="small" :disabled="!hasHistory" @click="clearMessages">
          清空历史消息
        </t-button>
      </div>
    </div>
    
    <!-- 聊天组件 -->
    <div style="height: 500px">
      <t-chatbot
        ref="chatRef"
        :default-messages="defaultMessages"
        :message-props="messageProps"
        :chat-service-config="chatServiceConfig"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { 
  type SSEChunkData, 
  type AIMessageContent, 
  type ChatMessagesData, 
  type ChatServiceConfig, 
  type TdChatbotApi, 
  type SuggestionItem,
} from '@tdesign-vue-next/chat';

/**
 * 初始化消息示例
 * 
 * 学习目标：
 * - 使用 defaultMessages 设置欢迎语和建议问题
 * - 通过 setMessages 动态加载历史消息
 * - 实现点击建议问题填充输入框
 */

const chatRef = ref<TdChatbotApi | null>(null);
const hasHistory = ref(false);

// 初始化消息
const defaultMessages: ChatMessagesData[] = [
  {
    id: 'welcome',
    role: 'assistant',
    content: [
      {
        type: 'text',
        status: 'complete',
        data: '你好！我是 TDesign 智能助手，有什么可以帮助你的吗？',
      },
      {
        type: 'suggestion',
        status: 'complete',
        data: [
          {
            title: 'TDesign 是什么？',
            prompt: '请介绍一下 TDesign 设计体系',
          },
          {
            title: '如何快速上手？',
            prompt: 'TDesign React 如何快速开始使用？',
          },
          {
            title: '有哪些组件？',
            prompt: 'TDesign 提供了哪些常用组件？',
          },
        ],
      },
    ],
  },
];

// 模拟历史消息数据（通常从后端接口获取）
const historyMessages: ChatMessagesData[] = [
  {
    id: 'history-1',
    role: 'user',
    datetime: '2024-01-01 10:00:00',
    content: [
      { type: 'text', data: 'TDesign 支持哪些框架？' },
    ],
  },
  {
    id: 'history-2',
    role: 'assistant',
    datetime: '2024-01-01 10:00:05',
    status: 'complete',
    content: [
      {
        type: 'markdown',
        data: 'TDesign 目前支持以下框架：\n\n- **React**\n- **Vue 2/3**\n- **Flutter**\n- **小程序**',
      },
    ],
  },
];

// 加载历史消息
const loadHistory = () => {
  chatRef.value?.setMessages(historyMessages, 'replace');
  hasHistory.value = true;
};

// 清空消息
const clearMessages = () => {
  chatRef.value?.clearMessages();
  hasHistory.value = false;
};

// 聊天服务配置
const chatServiceConfig: ChatServiceConfig = {
  endpoint: 'https://1257786608-9i9j1kpa67.ap-guangzhou.tencentscf.com/sse/normal',
  stream: true,
  onMessage: (chunk: SSEChunkData): AIMessageContent => {
    const { ...rest } = chunk.data as any;
    return {
      type: 'markdown',
      data: rest?.msg || '',
    };
  },
};

// 消息配置：处理建议问题点击
const messageProps = {
  assistant: {
    handleActions: {
      // 点击建议问题时，填充到输入框
      suggestion: ({ content }: { content: SuggestionItem }) => {
        chatRef.value?.addPrompt(content.prompt);
      },
    },
  },
};
</script>

<style scoped lang="less">
.quick-actions {
  margin-bottom: 16px;
  padding: 12px;
  background: var(--td-bg-color-secondarycontainer);
  border-radius: 4px;
  
  .actions-title {
    margin-bottom: 8px;
    font-size: 14px;
    font-weight: 500;
  }
  
  .actions-buttons {
    display: flex;
    gap: 8px;
  }
}
</style>
```

---

### 角色消息配置

使用 `messageProps` 配置不同角色的消息展示效果，这些配置会透传给内部的 [ChatMessage] 组件。包括**消息样式**（气泡样式、位置、头像、昵称）、**操作回调**（复制、点赞、点踩、重试）、**内容展示**行为（思考过程、搜索结果、Markdown 等）。支持静态配置对象和动态配置函数两种方式。

```vue
<template>
  <div style="margin-top: -18px; height: 408px">
    <t-chatbot
      ref="chatRef"
      :default-messages="defaultMessages"
      :message-props="messageProps"
      :chat-service-config="chatServiceConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { 
  type SSEChunkData, 
  type AIMessageContent, 
  type TdChatMessageConfigItem, 
  type ChatMessagesData, 
  type ChatServiceConfig, 
  type TdChatbotApi,
} from '@tdesign-vue-next/chat';
import { MessagePlugin } from 'tdesign-vue-next';
import { ref } from 'vue';

/**
 * 角色消息配置示例
 * 
 * 本示例展示如何通过 messageProps 配置不同角色的消息展示效果。
 * messageProps 会透传给内部的 ChatMessage 组件，用于控制消息的渲染和交互。
 * 
 * 配置内容包括：
 * - 消息样式配置（气泡样式、位置、头像、昵称等）
 * - 消息操作按钮配置（复制、点赞、点踩、重试）
 * - 内容类型展示配置（思考过程、搜索结果、Markdown 等）
 * - 静态配置 vs 动态配置的使用场景
 * 
 * 学习目标：
 * - 掌握 messageProps 动态配置函数的使用方式
 * - 了解如何根据消息内容、状态动态调整配置
 * - 学会配置消息操作按钮及其回调
 * - 学会使用 chatContentProps 控制内容展示行为
 */

const chatRef = ref<TdChatbotApi | null>(null);

// 初始化消息：展示各种内置支持的渲染类型
const defaultMessages: ChatMessagesData[] = [
  {
    id: 'demo-1',
    role: 'user',
    content: [
      { type: 'text', data: '请展示一下 TDesign Chatbot 内置支持的各种内容类型' },
    ],
    datetime: '2024-01-01 10:00:00',
  },
  {
    id: 'demo-2',
    role: 'assistant',
    status: 'complete',
    datetime: '2024-01-01 10:00:05',
    content: [
      // 1. 思考过程
      {
        type: 'thinking',
        data: {
          title: '分析问题',
          text: '正在分析用户问题的核心需求，准备展示各种内容类型...',
        },
        status: 'complete',
      },
      // 2. 搜索结果
      {
        type: 'search',
        data: {
          title: '找到 3 条相关内容',
          references: [
            {
              title: 'TDesign 官网',
              url: 'https://tdesign.tencent.com',
              content: 'TDesign 是腾讯开源的企业级设计体系',
            },
          ],
        },
      },
      // 3. Markdown 内容
      {
        type: 'markdown',
        data: `好的！以下是 TDesign Chatbot 支持的各种内容类型：

**1. 文本和 Markdown**
- 纯文本内容
- **粗体**、*斜体*、\`代码\`
- [链接](https://tdesign.tencent.com)

**2. 代码块**
\`\`\`javascript
const greeting = 'Hello TDesign!';
console.log(greeting);
\`\`\`

**3. 列表**
- 思考过程（Thinking）
- 搜索结果（Search）
- 建议问题（Suggestion）`,
      },
      // 4. 建议问题
      {
        type: 'suggestion',
        data: [
          { title: '继续了解 TDesign', prompt: '告诉我更多关于 TDesign 的信息' },
          { title: '查看组件列表', prompt: 'TDesign 有哪些组件？' },
        ],
      },
    ],
  },
];

// 聊天服务配置
const chatServiceConfig: ChatServiceConfig = {
  endpoint: 'https://1257786608-9i9j1kpa67.ap-guangzhou.tencentscf.com/sse/normal',
  stream: true,
  onMessage: (chunk: SSEChunkData): AIMessageContent => {
    const { ...rest } = chunk.data as any;
    return {
      type: 'markdown',
      data: rest?.msg || '',
    };
  },
};

// 动态配置消息展示函数：根据消息内容、状态等动态调整配置
const messageProps = (msg: ChatMessagesData): TdChatMessageConfigItem => {
  const { role } = msg;
  
  // 用户消息配置
  if (role === 'user') {
    return {
      variant: 'base',
      placement: 'right',
      avatar: 'https://tdesign.gtimg.com/site/avatar.jpg',
      name: '用户',
    };
  }
  
  // AI 消息配置
  if (role === 'assistant') {
    return {
      variant: 'text',
      placement: 'left',
      avatar: 'https://tdesign.gtimg.com/site/avatar-boy.jpg',
      name: 'TDesign 助手',
      // 消息操作按钮
      actions: ['copy', 'replay', 'good', 'bad'],
      // 消息操作回调
      handleActions: {
        copy: () => {
          MessagePlugin.success('已复制到剪贴板');
        },
        good: ({ message, active }) => {
          console.log('点赞', message, active);
          MessagePlugin.success(active ? '已点赞' : '取消点赞');
        },
        bad: ({ message, active }) => {
          console.log('点踩', message, active);
          MessagePlugin.success(active ? '已点踩' : '取消点踩');
        },
      },
      // 根据消息状态和内容动态配置
      chatContentProps: {
        // 思考过程
        thinking: {
          collapsed: false,
          layout: 'block',
          maxHeight: 200,
        },
        // 搜索结果
        search: {
          useCollapse: true,
          collapsed: false,
        },
        // markdown文本
        markdown: {
          options: {
            themeSettings: {
              codeBlockTheme: 'light',
            },
          },
        },
      },
    };
  }
  
  return {};
};
</script>
```

---

### 输入配置

使用 `senderProps` 配置输入框的各种行为，这些配置会透传给内部的 [ChatSender] 组件。包括基础配置（占位符、自动高度）、附件上传配置（文件类型、附件展示）、输入事件回调等。

```vue
<template>
  <div style="position: relative">
    <!-- 快捷指令区域 -->
    <div class="quick-prompts">
      <div class="prompts-title">快捷指令：</div>
      <div class="prompts-buttons">
        <t-button 
          v-for="(prompt, index) in quickPrompts" 
          :key="index"
          size="small" 
          variant="outline"
          @click="handleQuickPrompt(prompt)"
        >
          {{ prompt }}
        </t-button>
      </div>
    </div>
    
    <!-- 聊天组件 -->
    <div style="margin-top: 38px; height: 352px">
      <t-chatbot
        ref="chatRef"
        :sender-props="senderProps"
        :chat-service-config="chatServiceConfig"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { 
  type SSEChunkData, 
  type AIMessageContent, 
  type ChatServiceConfig, 
  type TdChatbotApi, 
  type TdAttachmentItem, 
  type TdChatSenderActionName,
} from '@tdesign-vue-next/chat';
import { MessagePlugin } from 'tdesign-vue-next';

const chatRef = ref<TdChatbotApi | null>(null);
const files = ref<TdAttachmentItem[]>([]);

// 聊天服务配置
const chatServiceConfig: ChatServiceConfig = {
  endpoint: 'https://1257786608-9i9j1kpa67.ap-guangzhou.tencentscf.com/sse/normal',
  stream: true,
  onMessage: (chunk: SSEChunkData): AIMessageContent => {
    const { ...rest } = chunk.data as any;
    return {
      type: 'markdown',
      data: rest?.msg || '',
    };
  },
};

// 输入框配置
const senderProps = {
  // 基础配置
  placeholder: '请输入您的问题...（支持 Shift+Enter 换行）',
  // 输入框配置，透传Textarea组件的属性
  textareaProps: {
    maxlength: 10,
  },
  // 操作按钮
  actions: ['attachment', 'send'] as TdChatSenderActionName[],
  // 附件配置
  attachmentsProps: {
    items: files.value,
    overflow: 'scrollX',
  },
  // 上传配置
  uploadProps: {
    accept: '.pdf,.docx,.txt,.md',
  },
  // 事件回调
  onChange: (e: CustomEvent<string>) => {
    console.log('输入内容:', e.detail);
  },
  onFocus: () => {
    console.log('输入框获得焦点');
  },
  onBlur: () => {
    console.log('输入框失去焦点');
  },
  onFileSelect: (e: CustomEvent<File[]>) => {
    console.log('选择文件:', e.detail);
    // 添加新文件并模拟上传进度
    const newFile: TdAttachmentItem = {
      name: e.detail[0].name,
      size: e.detail[0].size,
      status: 'progress',
      description: '上传中',
    };
    files.value.unshift(newFile);
    
    // 模拟上传完成
    setTimeout(() => {
      const index = files.value.findIndex((file) => file.name === newFile.name);
      if (index !== -1) {
        files.value[index] = {
          ...files.value[index],
          url: 'https://tdesign.gtimg.com/site/avatar.jpg',
          status: 'success',
          description: `${Math.floor((newFile?.size || 0) / 1024)}KB`,
        };
      }
      MessagePlugin.success(`文件${newFile.name}上传成功`);
    }, 1000);
  },
  onFileRemove: (e: CustomEvent<TdAttachmentItem[]>) => {
    console.log('移除文件后的列表:', e.detail);
    files.value = e.detail;
    MessagePlugin.info('文件已移除');
  },
};

// 快捷指令列表
const quickPrompts = [
  '介绍一下 TDesign', 
  '如何使用 Chatbot 组件？', 
  '有哪些内容类型？', 
  '如何自定义样式？'
];

// 处理快捷指令点击
const handleQuickPrompt = (prompt: string) => {
  chatRef.value?.addPrompt(prompt);
};
</script>

<style scoped lang="less">
.quick-prompts {
  position: absolute;
  top: -40px;
  left: -40px;
  width: calc(100% + 80px);
  padding: 12px 0 12px 16px;
  background: var(--td-bg-color-secondarycontainer);
  box-sizing: border-box;
  display: flex;
  align-items: center;
  
  .prompts-title {
    font-size: 14px;
    font-weight: 500;
  }
  
  .prompts-buttons {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
```

---

### 数据处理

`chatServiceConfig` 是 Chatbot 的核心配置，控制着与后端的通信和数据处理，是连接前端组件和后端服务的桥梁。

#### 自定义协议配置

```vue
<template>
  <div style="margin-top: -18px; height: 408px">
    <t-chatbot :chat-service-config="chatServiceConfig" />
  </div>
</template>

<script setup lang="ts">
import { 
  type SSEChunkData, 
  type AIMessageContent, 
  type ChatServiceConfig, 
  type ChatRequestParams,
} from '@tdesign-vue-next/chat';
import { MessagePlugin } from 'tdesign-vue-next';

// 聊天服务配置（自定义协议）
const chatServiceConfig: ChatServiceConfig = {
  // 1. 基础配置
  endpoint: 'https://1257786608-9i9j1kpa67.ap-guangzhou.tencentscf.com/sse/normal',
  stream: true,
  protocol: 'default',
  
  // 2. 请求发送前的配置
  onRequest: (params: ChatRequestParams) => {
    console.log('发送请求前:', params);
    return {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': 'Bearer your-token',
      },
      body: JSON.stringify({
        ...params,
        model: 'gpt-4',
        temperature: 0.7,
      }),
    };
  },
  
  // 3. 流式传输开始时的回调
  onStart: (chunk: string) => {
    console.log('开始接收流式数据:', chunk);
    MessagePlugin.info('AI 开始回复...');
  },
  
  // 4. 数据转换
  onMessage: (chunk: SSEChunkData): AIMessageContent | null => {
    console.log('收到数据块:', chunk);
    const { type, ...rest } = chunk.data as any;
    
    switch (type) {
      case 'text':
        return {
          type: 'markdown',
          data: rest?.msg || '',
          strategy: 'merge',
        };
      case 'think':
        return {
          type: 'thinking',
          data: {
            title: rest.title || '思考中',
            text: rest.content || '',
          },
          status: /完成/.test(rest?.title) ? 'complete' : 'streaming',
        };
      case 'search':
        return {
          type: 'search',
          data: {
            title: rest.title || '搜索结果',
            references: rest?.content || [],
          },
        };
      default:
        console.log('忽略事件类型:', type);
        return null;
    }
  },
  
  // 5. 请求完成时的回调
  onComplete: (isAborted: boolean, params?: ChatRequestParams) => {
    console.log('请求完成:', { isAborted, params });
    if (isAborted) {
      MessagePlugin.warning('已停止生成');
    } else {
      MessagePlugin.success('回复完成');
    }
  },
  
  // 6. 用户主动中止时的回调
  onAbort: async () => {
    console.log('用户中止对话');
  },
  
  // 7. 错误处理
  onError: (err: Error | Response) => {
    console.error('请求错误:', err);
    if (err instanceof Response) {
      MessagePlugin.error(`请求失败: ${err.status} ${err.statusText}`);
    } else {
      MessagePlugin.error(`发生错误: ${err.message}`);
    }
  },
};
</script>
```

#### AG-UI 协议配置

当后端服务符合 AG-UI 协议时，只需设置 `protocol: 'agui'`，无需编写 `onMessage` 进行数据转换：

```javascript
const chatServiceConfig: ChatServiceConfig = {
  endpoint: '/api/agui/chat',
  protocol: 'agui', // 启用AG-UI协议
  stream: true,
};
```

---

### 实例方法

通过 ref 获取组件实例，调用各种方法控制组件行为：

| 方法 | 说明 |
|------|------|
| `sendUserMessage` | 发送用户消息 |
| `sendAIMessage` | 发送AI消息 |
| `sendSystemMessage` | 发送系统消息 |
| `setMessages` | 批量设置消息 |
| `clearMessages` | 清空消息 |
| `regenerate` | 重新生成最后一条消息 |
| `abortChat` | 中止当前请求 |
| `scrollList` | 滚动列表 |
| `addPrompt` | 填充提示语到输入框 |
| `selectFile` | 触发文件选择 |
| `isChatEngineReady` | 获取 ChatEngine 就绪状态 |
| `chatStatus` | 获取当前对话状态 |
| `senderLoading` | 获取发送器加载状态 |

---

### 自定义渲染

使用**动态插槽机制**实现自定义渲染，包括自定义内容渲染、自定义操作栏、自定义输入区域。

---

## 场景示例

- 基础问答
- 代码助手
- 图像生成
- 任务规划

---

## API

### Chatbot Props

| 属性 | 类型 | 默认值 | 说明 | 必传 |
|------|------|--------|------|------|
| defaultMessages | `ChatMessagesData[]` | - | 初始消息数据列表 | N |
| messageProps | `Object \| Function` | - | 消息项配置，透传给内部 ChatMessage 组件。可以是静态配置对象或动态配置函数。TS 类型：`TdChatMessageConfig \| ((msg: ChatMessagesData) => TdChatMessageConfigItem)` | N |
| listProps | `TdChatListProps` | - | 消息列表配置 | N |
| senderProps | `TdChatSenderProps` | - | 发送框配置，透传给内部 ChatSender 组件 | N |
| chatServiceConfig | `ChatServiceConfig` | - | 对话服务配置，包含网络请求和回调配置 | N |
| onMessageChange | `Function` | - | 消息列表数据变化回调。TS 类型：`(e: CustomEvent<ChatMessagesData[]>) => void` | N |
| onChatReady | `Function` | - | 内部对话引擎初始化完成回调。TS 类型：`(e: CustomEvent) => void` | N |
| onChatAfterSend | `Function` | - | 发送消息后的回调。TS 类型：`(e: CustomEvent<ChatRequestParams>) => void` | N |

---

### TdChatListProps 消息列表配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| autoScroll | Boolean | `true` | 高度变化时列表是否自动滚动到底部 |
| onScroll | Function | - | 滚动事件回调 |

---

### ChatServiceConfig 对话服务配置

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| endpoint | String | - | 对话服务请求地址 url |
| protocol | String | `'default'` | 对话服务协议，支持 `'default'` 和 `'agui'` |
| stream | Boolean | `true` | 是否使用流式传输 |
| onStart | Function | - | 流式传输接收到第一个数据块时的回调。TS 类型：`(chunk: string) => void` |
| onRequest | Function | - | 请求发送前的配置回调，可修改请求参数、添加 headers 等。TS 类型：`(params: ChatRequestParams) => RequestInit` |
| onMessage | Function | - | 处理流式消息的回调，用于解析后端数据并映射为组件所需格式。TS 类型：`(chunk: SSEChunkData) => AIMessageContent \| AIMessageContent[] \| null` |
| onComplete | Function | - | 请求结束时的回调。TS 类型：`(isAborted: boolean, params?: ChatRequestParams) => AIMessageContent \| AIMessageContent[] \| null` |
| onAbort | Function | - | 中止请求时的回调。TS 类型：`() => Promise<void>` |
| onError | Function | - | 错误处理回调。TS 类型：`(err: Error \| Response) => void` |

---

### Chatbot 实例方法和属性

通过 ref 获取组件实例，调用以下方法：

| 方法/属性 | 类型 | 描述 |
|-----------|------|------|
| setMessages | `(messages: ChatMessagesData[], mode?: 'replace' \| 'prepend' \| 'append') => void` | 批量设置消息 |
| sendUserMessage | `(params: ChatRequestParams) => Promise<void>` | 发送用户消息，处理请求参数并触发消息流 |
| sendAIMessage | `{ params?: ChatRequestParams; content?: AIMessageContent[]; sendRequest?: boolean }` | 发送 AI 消息，处理请求参数并触发消息流 |
| sendSystemMessage | `(msg: string) => void` | 发送系统级通知消息，用于展示系统提示/警告 |
| abortChat | `() => Promise<void>` | 中止当前进行中的对话请求，清理网络连接 |
| addPrompt | `(prompt: string) => void` | 将预设提示语添加到输入框，辅助用户快速输入 |
| selectFile | `() => void` | 触发文件选择对话框，用于附件上传功能 |
| regenerate | `(keepVersion?: boolean) => Promise<void>` | 重新生成最后一条消息，可选保留历史版本 |
| registerMergeStrategy | `(type: T['type'], handler: (chunk: T, existing?: T) => T) => void` | 注册自定义消息合并策略，用于处理流式数据更新 |
| scrollList | `({ to: 'bottom' \| 'top', behavior: 'auto' \| 'smooth' }) => void` | 受控滚动到指定位置 |
| clearMessages | `() => void` | 清空消息列表 |
| isChatEngineReady | `boolean` | ChatEngine 是否就绪 |
| chatMessageValue | `ChatMessagesData[]` | 获取当前消息列表的只读副本 |
| chatStatus | `ChatStatus` | 获取当前对话状态（空闲/进行中/错误等） |
| senderLoading | `boolean` | 当前输入框按钮是否在'输出中' |

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chatbot
- ChatMessage 文档: https://tdesign.tencent.com/react-chat/components/chat-message
- ChatSender 文档: https://tdesign.tencent.com/react-chat/components/chat-sender
- ChatEngine 集成: https://tdesign.tencent.com/chat/components/chat-engine
- AG-UI 协议: https://tdesign.tencent.com/chat/agui
