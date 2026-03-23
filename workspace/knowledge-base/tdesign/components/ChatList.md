# ChatList 对话列表

> 来源: https://tdesign.tencent.com/chat/components/chat-list  
> 整理时间: 2026-03-21

---

## 简介

用于展示对话或者普通对话场景的组件。

**核心特性**：
- 支持新消息自动滚动到底部
- 自动检测用户滚动行为，当用户主动滚动时暂停自动滚动
- 支持具名插槽和默认插槽两种使用方式
- 支持可拖拽悬窗、抽屉等场景

---

## 基础问答

最简单的用法，通过 `data` 属性传入消息列表：

```vue
<template>
  <t-chat-list
    :data="[
      {
        avatar: 'https://tdesign.gtimg.com/site/avatar.jpg',
        role: 'user',
        content: [{ type: 'text', data: '南极的自动提款机叫什么名字？' }],
      },
      {
        avatar: 'https://tdesign.gtimg.com/site/chat-avatar.png',
        role: 'assistant',
        content: [{ type: 'text', data: '它叫 McMurdo Station ATM。' }],
      },
    ]"
  />
</template>
```

---

## 具名插槽

通过具名插槽自定义各个区域，每个插槽都提供 `{ item, index }` 参数：

```vue
<template>
  <t-chat-list
    :clear-history="false"
    :text-loading="loading"
    :data="chatList"
  >
    <!-- 自定义头像 -->
    <template #avatar="{ item, index }">
      <t-avatar size="large" shape="circle" :image="item.avatar" />
    </template>

    <!-- 自定义昵称 -->
    <template #name="{ item, index }">
      {{ item.name }}
    </template>

    <!-- 自定义时间 -->
    <template #datetime="{ item, index }">
      {{ item.datetime }}
    </template>

    <!-- 自定义内容（支持自定义组件如图表） -->
    <template #content="{ item, index }">
      <template v-for="(contentItem, contentIndex) in item.content" :key="contentIndex">
        <t-chat-content
          v-if="contentItem.type === 'text'"
          :content="contentItem.data"
          :role="item.role"
        />
        <!-- 自定义图表组件 -->
        <MyChartComponent
          v-else-if="contentItem.type === 'chart'"
          :chart-type="contentItem.data.chartType"
          :options="contentItem.data.options"
        />
      </template>
    </template>

    <!-- 自定义操作栏 -->
    <template #actionbar="{ item, index }">
      <t-chat-actionbar
        v-if="item.role === 'assistant'"
        :content="getActionContent(item.content)"
        :action-bar="['good', 'bad', 'replay', 'copy']"
        :comment="item.comment"
        @actions="(type) => handleOperation(type, { item, index })"
      />
    </template>

    <!-- 底部输入框 -->
    <template #footer>
      <t-chat-sender :loading="isStreamLoad" @send="inputEnter" @stop="handleStop">
        <template #suffix="{ renderPresets }">
          <component :is="renderPresets([])" />
        </template>
      </t-chat-sender>
    </template>
  </t-chat-list>
</template>
```

---

## 默认插槽（推荐）

使用 `t-chat-list` 嵌套 `t-chat-message` 遍历聊天列表，提供更灵活的消息渲染控制：

```vue
<template>
  <div class="chat-box">
    <t-chat-list
      ref="chatRef"
      :clear-history="chatList.length > 0 && !isStreamLoad"
      :text-loading="loading"
      style="height: 600px"
      animation="gradient"
      @scroll="handleChatScroll"
      @clear="clearConfirm"
    >
      <!-- 遍历消息列表 -->
      <template v-for="(item, index) in chatList" :key="index">
        <t-chat-message
          :avatar="item.avatar"
          :name="item.name"
          :role="item.role"
          :content="item.content"
          :datetime="item.datetime"
          :handle-actions="onActions"
          :chat-content-props="{
            thinking: { maxHeight: 100, collapsed: false },
            search: { expandable: true },
          }"
        >
          <!-- 自定义操作按钮插槽 -->
          <template #actionbar>
            <t-chat-actionbar
              v-if="item.role === 'assistant'"
              :content="getActionContent(item.content)"
              :comment="item.comment || ''"
              :action-bar="['good', 'bad', 'replay', 'copy']"
              @actions="(type) => handleOperation(type, { item, index })"
            />
          </template>
        </t-chat-message>
      </template>

      <!-- 底部输入框 -->
      <template #footer>
        <t-chat-sender v-model="query" :loading="isStreamLoad" @send="inputEnter" @stop="onStop" />
      </template>
    </t-chat-list>
  </div>
</template>

<script setup lang="jsx">
import { ref } from 'vue';

const loading = ref(false);
const isStreamLoad = ref(false);
const query = ref('');
const chatRef = ref(null);

const chatList = ref([
  {
    avatar: 'https://tdesign.gtimg.com/site/avatar.jpg',
    name: '自己',
    datetime: '今天16:38',
    id: '11111',
    role: 'user',
    status: 'complete',
    content: [
      { type: 'text', data: '分析以下内容，总结一篇广告策划方案' },
      {
        type: 'attachment',
        data: [
          { fileType: 'doc', name: 'demo.docx', url: 'https://example.com/demo.docx', size: 12312 },
        ],
      },
    ],
  },
  {
    avatar: 'https://tdesign.gtimg.com/site/chat-avatar.png',
    name: 'TDesignAI',
    datetime: '今天16:38',
    id: '33333',
    role: 'assistant',
    status: 'complete',
    content: [
      {
        type: 'thinking',
        status: 'complete',
        data: { title: '已完成思考（耗时3秒）', text: '...' },
      },
      {
        type: 'markdown',
        data: '**数据支撑：** 据《传媒内参2024报告》，2024年偶像爱情剧完播率`提升12%`。',
      },
      {
        type: 'suggestion',
        data: [
          { title: '近3年偶像爱情剧的市场反馈如何', prompt: '近3年偶像爱情剧的市场反馈如何' },
        ],
      },
    ],
  },
]);

const handleChatScroll = ({ e }) => {
  console.log('handleChatScroll', e);
};

const clearConfirm = () => {
  chatList.value = [];
};

const handleOperation = (type, { item, index }) => {
  if (type === 'good' || type === 'bad') {
    if (item) {
      item.comment = item.comment === type ? '' : type;
    }
  }
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

const getActionContent = (contentArray) => {
  const textContent = contentArray.find((item) => item.type === 'text' || item.type === 'markdown');
  return textContent ? textContent.data : '';
};

const onStop = () => {
  isStreamLoad.value = false;
  loading.value = false;
};

const inputEnter = (inputValue) => {
  if (isStreamLoad.value || !inputValue) return;

  // 添加用户消息
  chatList.value.push({
    avatar: 'https://tdesign.gtimg.com/site/avatar.jpg',
    name: '自己',
    datetime: new Date().toDateString(),
    role: 'user',
    content: [{ type: 'text', data: inputValue }],
  });

  // 添加 AI 消息占位
  chatList.value.push({
    avatar: 'https://tdesign.gtimg.com/site/chat-avatar.png',
    name: 'TDesignAI',
    datetime: new Date().toDateString(),
    role: 'assistant',
    content: [
      { type: 'thinking', status: 'pending', data: { title: '思考中...', text: '' } },
      { type: 'markdown', data: '' },
    ],
  });

  query.value = '';
  // 调用 SSE 接口...
};
</script>
```

---

## AI 助手可拖拽

搭配 `Dialog` 非模态对话框组件，实现可拖拽的 AI 助手：

```vue
<template>
  <t-button theme="primary" @click="visibleModelessDrag = true">AI助手可拖拽</t-button>

  <t-dialog
    v-model:visible="visibleModelessDrag"
    :footer="false"
    header="AI助手"
    mode="modeless"
    draggable
  >
    <template #body>
      <t-chat-list
        layout="single"
        style="height: 600px"
        :data="chatList"
        :clear-history="chatList.length > 0 && !isStreamLoad"
        :text-loading="loading"
        :reverse="true"
        @clear="clearConfirm"
      >
        <template #content="{ item }">
          <template v-for="(content, contentIndex) in item.content" :key="contentIndex">
            <t-chat-content :content="content.data" :role="item.role" />
          </template>
        </template>
        <template #footer>
          <t-chat-input :stop-disabled="isStreamLoad" @send="inputEnter" @stop="onStop" />
        </template>
      </t-chat-list>
    </template>
  </t-dialog>
</template>
```

---

## AI 助手悬窗

搭配 `Drawer` 抽屉组件：

```vue
<template>
  <t-button theme="primary" @click="visible = true">AI助手悬窗展示</t-button>

  <t-drawer v-model:visible="visible" :footer="false" size="480px" :close-btn="true">
    <template #header>
      <t-avatar size="32px" shape="circle" image="https://tdesign.gtimg.com/site/chat-avatar.png" />
      <span class="title">Hi, 我是AI</span>
    </template>

    <t-chat-list
      layout="both"
      :clear-history="chatList.length > 0 && !isStreamLoad"
      :text-loading="loading"
      @clear="clearConfirm"
    >
      <template v-for="(item, index) in chatList" :key="index">
        <t-chat-message
          :avatar="item.avatar"
          :name="item.name"
          :role="item.role"
          :content="item.content"
          :datetime="item.datetime"
          :variant="getStyle(item.role)"
          :placement="item.role === 'user' ? 'right' : 'left'"
        >
          <template #actionbar>
            <t-chat-actionbar
              v-if="item.role === 'assistant'"
              :content="getActionContent(item.content)"
              :comment="item.comment || ''"
              :action-bar="['good', 'bad', 'replay', 'copy']"
              @actions="(type) => handleOperation(type, { item, index })"
            />
          </template>
        </t-chat-message>
      </template>
      <template #footer>
        <t-chat-input :stop-disabled="isStreamLoad" @send="inputEnter" @stop="onStop" />
      </template>
    </t-chat-list>
  </t-drawer>
</template>
```

---

## API

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| data | `Array` | - | 消息数据列表（使用具名插槽时传入） |
| clear-history | boolean | false | 是否显示清空历史记录按钮 |
| text-loading | boolean | false | 是否显示文字加载状态 |
| animation | `'skeleton' \| 'moving' \| 'gradient' \| 'dot'` | `'skeleton'` | 加载动画类型 |
| layout | `'both' \| 'single'` | `'both'` | 布局方式 |
| reverse | boolean | false | 是否倒序渲染（用于可拖拽场景） |

### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| scroll | `{ e }` | 滚动时触发 |
| clear | - | 点击清空历史记录时触发 |

### Slots

| 插槽 | 参数 | 说明 |
|------|------|------|
| default | - | 默认插槽，用于嵌套 `t-chat-message` |
| avatar | `{ item, index }` | 自定义头像 |
| name | `{ item, index }` | 自定义昵称 |
| datetime | `{ item, index }` | 自定义时间 |
| content | `{ item, index }` | 自定义内容 |
| actionbar | `{ item, index }` | 自定义操作栏 |
| footer | - | 底部区域（通常放输入框） |

### 实例方法

```javascript
// 滚动到底部
chatRef.value?.scrollToBottom();

// 滚动到指定位置
chatRef.value?.scrollTo({ top: 100 });
```

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chat-list
