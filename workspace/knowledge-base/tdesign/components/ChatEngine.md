# ChatEngine 对话引擎

> 来源: https://tdesign.tencent.com/chat/components/chat-engine  
> 整理时间: 2026-03-21

---

## 简介

智能体对话底层逻辑引擎，提供灵活的 Hook API 用于深度定制。

ChatEngine 是一个底层对话引擎（Headless Core），提供灵活的 Hook API 用于深度定制。支持自定义 UI 结构、消息处理和 AG-UI 协议，适合构建复杂智能体应用，如工具调用、多步骤任务规划、状态流式传输等场景。

相比 Chatbot 组件提供了更高的灵活性，适合需要**深度定制 UI 结构和消息处理流程**的场景。Chatbot 组件本身也是基于 ChatEngine 构建的（ChatEngine + Preset UI）。

**阅读路径**：
1. **快速开始** - 了解 useChat Hook 的基本用法，组合组件构建对话界面的方法
2. **基础用法** - 掌握数据处理、消息管理、UI 定制、生命周期、自定义渲染等主要功能
3. **AG-UI 协议** - 学习 AG-UI 协议的使用和高级特性（工具调用、状态订阅等）

---

## 快速开始

使用 `useChat` Hook 创建对话引擎，组合 `ChatList`、`ChatMessage`、`ChatSender` 组件构建对话界面。

```vue
<template>
  <div style="margin-top: -18px; height: 408px; display: flex; flex-direction: column">
    <!-- 消息列表 -->
    <t-chat-list :clear-history="false" style="flex: 1">
      <t-chat-message
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :placement="message.role === 'user' ? 'right' : 'left'"
        :variant="message.role === 'user' ? 'base' : 'text'"
      />
    </t-chat-list>
    <!-- 输入框 -->
    <t-chat-sender
      v-model="inputValue"
      placeholder="请输入内容"
      :loading="status === 'pending' || status === 'streaming'"
      @send="handleSend"
      @stop="handleStop"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import {
  type SSEChunkData,
  type AIMessageContent,
  type ChatMessagesData,
  useChat,
} from '@tdesign-vue-next/chat';

/**
 * 快速开始示例
 *
 * 学习目标：
 * - 使用 useChat Hook 创建聊天引擎
 * - 组合 ChatList、ChatMessage、ChatSender 组件
 * - 理解 chatEngine、messages、status 的作用
 */

const inputValue = ref<string>('');

const defaultMessages: ChatMessagesData[] = [
  {
    id: 'demo-1',
    role: 'user',
    content: [{ type: 'text', data: '南极的自动提款机叫什么名字' }],
    datetime: '2024-01-01 10:00:00',
  },
  {
    id: 'demo-2',
    role: 'assistant',
    status: 'complete',
    datetime: '2024-01-01 10:00:05',
    content: [
      {
        type: 'markdown',
        data: `南极的自动提款机并没有一个特定的专属名称，但历史上确实有一台ATM机曾短暂存在于南极的麦克默多站（McMurdo Station）。`,
      },
    ],
  },
];

// 使用 useChat Hook 创建聊天引擎
const { chatEngine, messages, status } = useChat({
  defaultMessages,
  chatServiceConfig: {
    endpoint: 'https://your-api.com/sse',
    stream: true,
    onMessage: (chunk: SSEChunkData): AIMessageContent => {
      const { ...rest } = chunk.data;
      return {
        type: 'markdown',
        data: rest?.msg || '',
      };
    },
  },
});

// 发送消息
const handleSend = async (params: string) => {
  const { prompt } = { prompt: params };
  await chatEngine.value?.sendUserMessage({ prompt });
  inputValue.value = '';
};

// 停止生成
const handleStop = () => {
  chatEngine.value?.abortChat();
};
</script>
```

---

## 基础用法

### 初始化消息

使用 `defaultMessages` 设置静态初始化消息，或通过 `chatEngine.setMessages` 动态加载历史消息。

```vue
<template>
  <div style="position: relative">
    <!-- 操作按钮 -->
    <div class="op-button-area">
      <t-radio-group v-model="historyMode" variant="default-filled" @change="handleModeChange">
        <t-radio-button value="default">设置初始化消息</t-radio-button>
        <t-radio-button value="history">加载历史消息</t-radio-button>
      </t-radio-group>
    </div>

    <!-- 聊天界面 -->
    <div style="margin-top: 38px; height: 352px; display: flex; flex-direction: column">
      <t-chat-list :clear-history="false">
        <t-chat-message
          v-for="message in messages"
          :key="message.id"
          :message="message"
          :placement="message.role === 'user' ? 'right' : 'left'"
          :variant="message.role === 'user' ? 'base' : 'text'"
          :handle-actions="{
            suggestion: ({ content }) => handleSuggestionClick(content.prompt),
          }"
        />
      </t-chat-list>
      <t-chat-sender
        v-model="inputValue"
        placeholder="请输入内容"
        :loading="status === 'pending' || status === 'streaming'"
        @send="handleSend"
        @stop="handleStop"
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
  useChat,
} from '@tdesign-vue-next/chat';

const inputValue = ref<string>('');
const historyMode = ref<string>('default');

// 初始化消息（含建议问题）
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
          { title: '请介绍一下 TDesign 设计体系', prompt: '请介绍一下 TDesign 设计体系' },
          { title: 'TDesign Vue 如何快速开始使用？', prompt: 'TDesign Vue 如何快速开始使用？' },
          { title: 'TDesign 提供了哪些常用组件？', prompt: 'TDesign 提供了哪些常用组件？' },
        ],
      },
    ],
  },
];

// 模拟历史消息
const historyMessages: ChatMessagesData[] = [
  {
    id: 'history-1',
    role: 'user',
    datetime: '2024-01-01 10:00:00',
    content: [{ type: 'text', data: 'TDesign 支持哪些框架？' }],
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

const { chatEngine, messages, status } = useChat({
  defaultMessages,
  chatServiceConfig: {
    endpoint: 'https://your-api.com/sse',
    stream: true,
    onMessage: (chunk: SSEChunkData): AIMessageContent => {
      const { ...rest } = chunk.data;
      return { type: 'markdown', data: rest?.msg || '' };
    },
  },
});

// 切换消息模式
const handleModeChange = (value: string) => {
  if (value === 'history') {
    chatEngine.value?.setMessages(historyMessages, 'replace');
  } else {
    chatEngine.value?.setMessages(defaultMessages, 'replace');
  }
};

// 发送消息
const handleSend = async (params: string) => {
  await chatEngine.value?.sendUserMessage({ prompt: params });
  inputValue.value = '';
};

// 点击建议问题
const handleSuggestionClick = (prompt: string) => {
  inputValue.value = prompt;
};

// 停止生成
const handleStop = () => {
  chatEngine.value?.abortChat();
};
</script>
```

---

### 数据处理

`chatServiceConfig` 是 ChatEngine 的核心配置，控制着与后端的通信和数据处理。

**自定义协议**：

```javascript
const chatServiceConfig = {
  endpoint: '/api/chat',
  stream: true,
  protocol: 'default',

  // 请求配置
  onRequest: (params) => ({
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer your-token',
    },
    body: JSON.stringify({ ...params, model: 'gpt-4' }),
  }),

  // 流式开始回调
  onStart: (chunk) => {
    console.log('开始接收流式数据:', chunk);
  },

  // 数据转换（核心）
  onMessage: (chunk) => {
    const { type, ...rest } = chunk.data;
    switch (type) {
      case 'text':
        return { type: 'markdown', data: rest?.msg || '', strategy: 'merge' };
      case 'think':
        return {
          type: 'thinking',
          data: { title: rest.title || '思考中', text: rest.content || '' },
          status: /完成/.test(rest?.title) ? 'complete' : 'streaming',
        };
      case 'search':
        return {
          type: 'search',
          data: { title: rest.title || '搜索结果', references: rest?.content || [] },
        };
      default:
        return null;
    }
  },

  // 完成回调
  onComplete: (isAborted, params) => {
    console.log('请求完成:', { isAborted, params });
  },

  // 中止回调
  onAbort: async () => {
    console.log('用户中止对话');
  },

  // 错误处理
  onError: (err) => {
    console.error('请求错误:', err);
  },
};
```

**AG-UI 协议**（无需 onMessage）：

```javascript
const chatServiceConfig = {
  endpoint: '/api/agui/chat',
  protocol: 'agui',
  stream: true,
};
```

---

### 实例方法

通过 `chatEngine` 调用各种方法控制组件行为：

| 方法 | 说明 |
|------|------|
| `sendUserMessage({ prompt })` | 发送用户消息 |
| `sendAIMessage({ content, sendRequest })` | 发送 AI 消息 |
| `sendSystemMessage(text)` | 发送系统消息 |
| `setMessages(messages, mode)` | 批量设置消息（mode: replace/append） |
| `regenerateAIMessage()` | 重新生成最后一条 AI 消息 |
| `abortChat()` | 中止当前请求 |

```javascript
// 发送用户消息
chatEngine.value?.sendUserMessage({ prompt: '你好' });

// 发送 AI 消息（不触发请求）
chatEngine.value?.sendAIMessage({
  content: [{ type: 'text', data: '这是 AI 回答' }],
  sendRequest: false,
});

// 发送系统消息
chatEngine.value?.sendSystemMessage('这是一条系统通知');

// 批量设置消息
chatEngine.value?.setMessages(messages, 'replace');

// 清空消息
chatEngine.value?.setMessages([], 'replace');

// 重新生成
chatEngine.value?.regenerateAIMessage();

// 中止
chatEngine.value?.abortChat();
```

---

### 自定义渲染

使用**动态插槽机制**实现自定义渲染：

**步骤**：
1. 扩展类型：通过 TypeScript 声明自定义内容类型
2. 解析数据：在 `onMessage` 中返回自定义类型的数据结构
3. 监听变化：通过 `onMessageChange` 监听消息变化并同步到本地状态
4. 植入插槽：循环 `messages` 数组，使用 `slot = ${content.type}-${index}` 属性来渲染自定义组件

```vue
<t-chat-message
  v-for="message in messages"
  :key="message.id"
  :message="message"
  allow-content-segment-custom
>
  <!-- 自定义内容渲染 -->
  <template v-for="(item, index) in message.content" :key="index">
    <div v-if="item.type === 'imageview'" :slot="`${item.type}-${index}`">
      <!-- 自定义图片预览组件 -->
      <my-image-viewer :images="item.data" />
    </div>
  </template>

  <!-- 自定义操作栏 -->
  <template #actionbar>
    <t-chat-actionbar
      v-if="isAIMessage(message) && message.status === 'complete'"
      :action-bar="['copy', 'good', 'bad']"
      @actions="handleAction"
    />
    <t-chat-loading v-else animation="dot" />
  </template>
</t-chat-message>
```

---

## Headless 事件总线

ChatEngine 内置了事件总线（EventBus），支持在无 UI 场景下进行事件分发，适用于日志监控、跨组件通信、外部系统集成等场景。

```javascript
import ChatEngine, { ChatEngineEventType } from 'tdesign-web-components/lib/chat-engine';

// 创建引擎实例
const engine = new ChatEngine({
  debug: true,
  historySize: 50,
});

// 初始化配置
engine.init({
  endpoint: '/api/chat',
  stream: true,
  onMessage: (chunk) => ({ type: 'markdown', data: chunk.data?.msg || '' }),
});

// 订阅生命周期事件
engine.eventBus.on(ChatEngineEventType.ENGINE_INIT, (payload) => {
  console.log('引擎初始化', payload);
});

// 订阅消息事件
engine.eventBus.on(ChatEngineEventType.MESSAGE_CREATE, (payload) => {
  console.log('消息创建', payload.message.id, payload.message.role);
});

// 订阅请求事件
engine.eventBus.on(ChatEngineEventType.REQUEST_COMPLETE, (payload) => {
  console.log('请求完成', payload.messageId);
});

// 等待特定事件（Promise 方式）
const result = await engine.eventBus.waitFor(ChatEngineEventType.REQUEST_COMPLETE, 60000);

// 发布自定义事件
engine.eventBus.emitCustom('user:action', { action: 'button_click' });

// 获取事件历史
const history = engine.eventBus.getHistory();

// 销毁引擎
engine.destroy();
```

**支持的事件类型**：

| 事件 | 说明 |
|------|------|
| `ENGINE_INIT` | 引擎初始化 |
| `ENGINE_DESTROY` | 引擎销毁 |
| `MESSAGE_CREATE` | 消息创建 |
| `MESSAGE_UPDATE` | 消息更新 |
| `MESSAGE_STATUS_CHANGE` | 消息状态变化 |
| `MESSAGE_CLEAR` | 消息清空 |
| `REQUEST_START` | 请求开始 |
| `REQUEST_STREAM` | 流式数据 |
| `REQUEST_COMPLETE` | 请求完成 |
| `REQUEST_ERROR` | 请求错误 |
| `REQUEST_ABORT` | 请求中止 |

---

## AG-UI 协议

### 基础用法

开启 AG-UI 协议支持（`protocol: 'agui'`），组件会自动解析标准事件类型。

```vue
<template>
  <div style="height: 500px; display: flex; flex-direction: column">
    <t-chat-list ref="listRef" :clear-history="false">
      <t-chat-message
        v-for="message in messages"
        :key="message.id"
        :message="message"
        :placement="message.role === 'user' ? 'right' : 'left'"
        :variant="message.role === 'user' ? 'base' : 'text'"
      />
    </t-chat-list>
    <t-chat-sender
      v-model="inputValue"
      placeholder="请输入内容，体验 AG-UI 协议"
      :loading="status === 'pending' || status === 'streaming'"
      @send="handleSend"
      @stop="handleStop"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { type ChatRequestParams, type TdChatListApi, AGUIAdapter, useChat } from '@tdesign-vue-next/chat';

const inputValue = ref<string>('');
const listRef = ref<TdChatListApi | null>(null);

const { chatEngine, messages, status } = useChat({
  defaultMessages: [],
  chatServiceConfig: {
    endpoint: '/api/agui/chat',
    protocol: 'agui', // 开启 AG-UI 协议
    stream: true,
    onRequest: (params: ChatRequestParams) => ({
      body: JSON.stringify({ uid: 'agui-demo', prompt: params.prompt }),
    }),
    onStart: (chunk) => {
      console.log('AG-UI 流式传输开始:', chunk);
    },
    onComplete: (aborted, params, event) => {
      console.log('AG-UI 流式传输完成:', { aborted, event });
    },
    onError: (err) => {
      console.error('AG-UI 错误:', err);
    },
  },
});

// 初始化加载历史消息
onMounted(async () => {
  try {
    const response = await fetch('/api/conversation/history');
    const result = await response.json();
    if (result.success && result.data) {
      // 使用 AGUIAdapter 转换历史消息格式
      const convertedMessages = AGUIAdapter.convertHistoryMessages(result.data);
      chatEngine.value?.setMessages(convertedMessages);
      listRef.value?.scrollToBottom();
    }
  } catch (error) {
    console.error('加载历史消息出错:', error);
  }
});

const handleSend = async (params: string) => {
  await chatEngine.value?.sendUserMessage({ prompt: params });
  inputValue.value = '';
};

const handleStop = () => {
  chatEngine.value?.abortChat();
};
</script>
```

---

### 工具调用

AG-UI 协议支持通过 `TOOL_CALL_*` 事件让 AI Agent 调用前端工具组件，实现人机协作。

**核心 Hook 与组件**：

| 名称 | 类型 | 说明 |
|------|------|------|
| `useAgentToolcall` | Hook | 注册工具配置（元数据、参数、UI 组件） |
| `ToolCallRenderer` | 组件 | 工具调用的统一渲染器，自动匹配并渲染注册的 UI 组件 |

**使用流程**：
1. 使用 `useAgentToolcall` 注册工具配置
2. 在消息渲染时使用 `ToolCallRenderer` 组件渲染工具调用
3. `ToolCallRenderer` 自动查找配置、解析参数、管理状态、渲染 UI

```javascript
import { useAgentToolcall, ToolCallRenderer, isToolCallContent } from '@tdesign-vue-next/chat';
import MyToolComponent from './MyToolComponent.vue';

// 注册工具
const toolcallActions = [
  {
    name: 'generate_image',
    description: '生成图片',
    parameters: [
      { name: 'taskId', type: 'string', required: true },
      { name: 'prompt', type: 'string', required: true },
    ],
    subscribeKey: (props) => props.args?.taskId, // 订阅状态的 key
    component: MyToolComponent,
  },
];

useAgentToolcall(toolcallActions);
```

```vue
<!-- 在消息渲染中使用 ToolCallRenderer -->
<t-chat-message
  v-for="message in messages"
  :key="message.id"
  :message="message"
  allow-content-segment-custom
>
  <template v-for="(item, index) in message.content" :key="`content-${index}`">
    <div v-if="isToolCallContent(item)" :slot="`${item.type}-${index}`">
      <tool-call-renderer
        :tool-call="item.data"
        @respond="handleToolCallRespond"
      />
    </div>
  </template>
</t-chat-message>
```

```javascript
// 处理工具调用响应
const handleToolCallRespond = async (toolcall, response) => {
  await chatEngine.value?.sendAIMessage({
    params: {
      toolCallMessage: {
        toolCallId: toolcall.toolCallId,
        toolCallName: toolcall.toolCallName,
        result: JSON.stringify(response),
      },
    },
    sendRequest: true,
  });
};
```

---

### 工具状态订阅

使用 `useAgentState` 在对话组件外部订阅工具执行状态：

```javascript
import { useAgentState } from '@tdesign-vue-next/chat';

// 外部进度面板组件
const { stateMap, currentStateKey } = useAgentState();

// 获取当前任务状态
const currentState = currentStateKey ? stateMap[currentStateKey] : null;
const items = currentState?.items || [];
const completedCount = items.filter((item) => item.status === 'completed').length;
```

后端通过 `STATE_SNAPSHOT` 和 `STATE_DELTA` 事件推送状态数据：

```
// STATE_SNAPSHOT（初始快照）
data: {"type":"STATE_SNAPSHOT","snapshot":{"task_xxx":{"progress":0,"message":"准备开始...","items":[]}}}

// STATE_DELTA（增量更新，使用 JSON Patch 格式）
data: {"type":"STATE_DELTA","delta":[
  {"op":"replace","path":"/task_xxx/progress","value":20},
  {"op":"replace","path":"/task_xxx/message","value":"分析目的地信息"},
  {"op":"replace","path":"/task_xxx/items","value":[{"label":"分析目的地信息","status":"running"}]}
]}
```

---

### Activity 事件

AG-UI 协议支持通过 `ACTIVITY_*` 事件展示动态内容组件（如实时图表、进度条等）。

```javascript
import { useAgentActivity, isActivityContent, ActivityRenderer } from '@tdesign-vue-next/chat';

// 注册 Activity 组件
useAgentActivity([
  {
    activityType: 'plan-todo',
    component: PlanTodoActivity,
    description: '规划步骤展示',
  },
  {
    activityType: 'travel-progress',
    component: TravelProgressActivity,
    description: '行程规划进度',
  },
]);
```

```vue
<!-- 在消息渲染中使用 ActivityRenderer -->
<t-chat-message v-for="message in messages" :key="message.id" :message="message">
  <template v-if="Array.isArray(message.content)">
    <template v-for="(item, index) in message.content" :key="`content-${index}`">
      <ActivityRenderer v-if="isActivityContent(item)" :activity="item.data" />
    </template>
  </template>
</t-chat-message>
```

---

## AG-UI 事件类型

| 事件类型 | 说明 |
|----------|------|
| `RUN_STARTED` / `RUN_FINISHED` | 对话生命周期 |
| `TEXT_MESSAGE_START` / `TEXT_MESSAGE_CONTENT` / `TEXT_MESSAGE_END` | 文本消息 |
| `TEXT_MESSAGE_CHUNK` | 简化模式文本块 |
| `THINKING_START` / `THINKING_CONTENT` / `THINKING_END` | 思考过程 |
| `TOOL_CALL_START` / `TOOL_CALL_ARGS` / `TOOL_CALL_END` / `TOOL_CALL_RESULT` | 工具调用 |
| `TOOL_CALL_CHUNK` | 简化模式工具调用块 |
| `STATE_SNAPSHOT` | 状态快照 |
| `STATE_DELTA` | 状态增量更新（JSON Patch） |
| `ACTIVITY_SNAPSHOT` | Activity 初始化数据 |
| `ACTIVITY_DELTA` | Activity 增量更新 |

---

## API

### useChat Hook

```typescript
const { chatEngine, messages, status } = useChat(options);
```

#### 参数

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| defaultMessages | `ChatMessagesData[]` | `[]` | 初始消息列表 |
| chatServiceConfig | `ChatServiceConfig` | - | 对话服务配置 |

#### 返回值

| 属性 | 类型 | 说明 |
|------|------|------|
| chatEngine | `Ref<TdChatEngineApi \| null>` | ChatEngine 实例 |
| messages | `Ref<ChatMessagesData[]>` | 消息列表（响应式） |
| status | `Ref<ChatStatus>` | 当前状态：`'idle' \| 'pending' \| 'streaming' \| 'error'` |

---

### TdChatEngineApi 实例方法

| 方法 | 类型 | 说明 |
|------|------|------|
| sendUserMessage | `(params: ChatRequestParams) => Promise<void>` | 发送用户消息 |
| sendAIMessage | `(options: { params?; content?; sendRequest? }) => Promise<void>` | 发送 AI 消息 |
| sendSystemMessage | `(msg: string) => void` | 发送系统消息 |
| setMessages | `(messages: ChatMessagesData[], mode?: 'replace' \| 'prepend' \| 'append') => void` | 批量设置消息 |
| regenerateAIMessage | `() => Promise<void>` | 重新生成最后一条 AI 消息 |
| abortChat | `() => Promise<void>` | 中止当前请求 |
| clearMessages | `() => void` | 清空消息 |

---

### ChatMessagesData 类型

```typescript
interface ChatMessagesData {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: AIMessageContent[];
  datetime?: string;
  status?: 'pending' | 'streaming' | 'complete' | 'error' | 'stop';
  comment?: 'good' | 'bad' | '';
}

interface AIMessageContent {
  type: 'text' | 'markdown' | 'thinking' | 'search' | 'suggestion' | 'attachment' | 'image';
  data: any;
  status?: 'pending' | 'streaming' | 'complete' | 'error';
  strategy?: 'merge' | 'replace'; // 流式数据合并策略
}
```

---

### ChatServiceConfig 类型

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| endpoint | string | - | 对话服务请求地址 |
| protocol | `'default' \| 'agui'` | `'default'` | 协议类型 |
| stream | boolean | `true` | 是否流式传输 |
| onRequest | `(params) => RequestInit` | - | 请求前回调 |
| onStart | `(chunk) => void` | - | 流式开始回调 |
| onMessage | `(chunk) => AIMessageContent \| null` | - | 数据转换回调（自定义协议必需） |
| onComplete | `(isAborted, params) => void` | - | 请求完成回调 |
| onAbort | `() => Promise<void>` | - | 中止回调 |
| onError | `(err) => void` | - | 错误回调 |

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chat-engine
- AG-UI 协议: https://docs.ag-ui.com/introduction
- AGUIHistoryMessage 类型: https://github.com/TDesignOteam/tdesign-web-components/blob/develop/src/chat-engine/adapters/agui/types.ts
