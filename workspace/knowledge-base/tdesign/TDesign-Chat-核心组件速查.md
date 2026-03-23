# TDesign Chat 核心组件速查

> 整理时间: 2026-03-21  
> 版本: 0.5.1

---

## 1. Chatbot 智能对话 ⭐⭐⭐

**定位**: 高度封装的一体化组件，开箱即用

**适用场景**: 快速集成标准 AI 应用

**核心能力**:
- 完整的状态管理
- SSE 流式传输
- 消息渲染和交互逻辑
- 支持智能客服、问答系统、代码助手

**关键配置**:
```javascript
const chatServiceConfig = {
  endpoint: '/api/chat',
  stream: true,
  protocol: 'default', // 或 'agui'
  onMessage: (chunk) => ({ type: 'markdown', data: chunk.data.msg }),
};
```

**文档状态**: ✅ 已整理完整

---

## 2. ChatEngine 对话引擎 ⭐⭐⭐⭐⭐

**定位**: 底层 Headless Core，提供 Hook API

**适用场景**: 深度定制 UI 结构和消息处理流程

**核心能力**:
- `useChat` Hook
- 事件总线 (EventBus)
- AG-UI 协议完整支持
- 工具调用管理
- 状态流式传输

**基础用法**:
```javascript
const { chatEngine, messages, status } = useChat({
  chatServiceConfig: {
    endpoint: '/api/chat',
    protocol: 'agui',
    stream: true,
  },
});
```

**文档状态**: 📝 已获取主要内容，待整理

---

## 3. ChatSender 对话输入 ⭐⭐

**定位**: AI 聊天的输入框组件

**适用场景**: 需要自定义输入交互的场景

**核心能力**:
- 受控输入管理
- 附件上传/展示
- 多插槽自定义 (input-prefix, footer-prefix, suffix, inner-header)
- 模型切换、深度思考等扩展能力

**关键示例**:
```vue
<t-chat-sender
  v-model="inputValue"
  :attachments-props="{ items: filesList }"
  @send="handleSend"
  @file-select="handleUpload"
>
  <template #footer-prefix>
    <t-select v-model="model" :options="models" />
    <t-button>深度思考</t-button>
  </template>
</t-chat-sender>
```

**文档状态**: ✅ 已整理完整

---

## 4. ChatMessage 对话消息体 ⭐⭐⭐

**定位**: 单条消息的渲染组件

**适用场景**: 自定义消息展示效果

**核心能力**:
- 多种变体 (variant: base/text)
- 位置控制 (placement: left/right)
- 头像、昵称配置
- 内容类型支持 (text/markdown/thinking/search/suggestion/image)
- 操作按钮 (复制、点赞、点踩、重试)

**关键配置**:
```javascript
const messageProps = {
  variant: 'text',
  placement: 'left',
  avatar: 'https://example.com/avatar.jpg',
  name: 'AI助手',
  actions: ['copy', 'good', 'bad'],
  handleActions: {
    copy: () => MessagePlugin.success('已复制'),
  },
};
```

**文档状态**: ⏳ 待爬取

---

## 5. ChatList 对话列表 ⭐⭐

**定位**: 消息列表容器组件

**适用场景**: 管理消息列表的展示和滚动

**核心能力**:
- 消息列表渲染
- 自动滚动控制
- 清空历史记录
- 滚动到指定位置

**关键 API**:
```javascript
// 实例方法
listRef.value?.scrollToBottom();
listRef.value?.scrollTo({ top: 100 });
```

**文档状态**: ⏳ 待爬取

---

## 6. ChatContent 对话正文 ⭐⭐

**定位**: 消息内容的渲染组件

**适用场景**: 自定义特定类型内容的展示

**核心能力**:
- 文本渲染
- Markdown 渲染
- 思考过程 (Thinking)
- 搜索结果 (Search)
- 建议问题 (Suggestion)
- 图片/附件

**内容类型**:
```javascript
const content = [
  { type: 'thinking', data: { title: '思考中...', text: '...' } },
  { type: 'search', data: { title: '搜索结果', references: [] } },
  { type: 'markdown', data: '**粗体文本**' },
  { type: 'suggestion', data: [{ title: '问题1', prompt: '...' }] },
];
```

**文档状态**: ⏳ 待爬取

---

## 组件关系图

```
Chatbot (一体化)
    ├── ChatList (列表容器)
    │       └── ChatMessage (消息体)
    │               └── ChatContent (内容渲染)
    │                       ├── ChatMarkdown
    │                       ├── ChatThinking
    │                       └── ...
    ├── ChatSender (输入框)
    │       └── Attachments (附件)
    └── ChatActionbar (操作栏)

ChatEngine (底层引擎)
    ├── useChat (Hook)
    ├── useAgentToolcall (工具调用)
    ├── useAgentActivity (Activity)
    └── EventBus (事件总线)
```

---

## 选择建议

| 场景 | 推荐组件 | 理由 |
|------|----------|------|
| 快速上线 | Chatbot | 开箱即用，配置简单 |
| 深度定制 | ChatEngine + 原子组件 | 完全可控，灵活度高 |
| 自定义输入 | ChatSender | 丰富的插槽和配置 |
| 自定义消息 | ChatMessage + ChatContent | 精细控制展示效果 |
| 复杂 Agent | ChatEngine + AG-UI | 工具调用、状态管理 |

---

## 文档完成度

| 组件 | 状态 | 文件 |
|------|------|------|
| Chatbot | ✅ 完整 | components/Chatbot.md |
| ChatEngine | 📝 已获取 | 待整理 |
| ChatSender | ✅ 完整 | components/ChatSender.md |
| ChatMessage | ⏳ 待爬取 | - |
| ChatList | ⏳ 待爬取 | - |
| ChatContent | ⏳ 待爬取 | - |

---

## 下一步

需要我深入整理哪个组件？
- **ChatEngine** - 整理已获取的详细内容
- **ChatMessage/ChatList/ChatContent** - 爬取并整理
- **其他组件** - ChatActionbar、ChatMarkdown、ChatThinking 等
