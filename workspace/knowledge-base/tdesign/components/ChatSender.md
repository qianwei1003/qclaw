# ChatSender 对话输入组件

> 来源: https://tdesign.tencent.com/chat/components/chat-sender  
> 整理时间: 2026-03-21

---

## 简介

用于 AI 聊天的输入框，可以扩展模型、多模态等能力。

---

## 基础输入框

受控进行输入/发送等状态管理

```vue
<template>
  <t-chat-sender
    v-model="query"
    :stop-disabled="loading"
    :textarea-props="{
      placeholder: '请输入消息...',
    }"
    @send="inputEnter"
  >
    <template #suffix="{ renderPresets }">
      <!-- 在这里可以进行自由的组合使用，或者新增预设 -->
      <!-- 不需要附件操作的使用方式 -->
      <component :is="renderPresets([])" />
    </template>
  </t-chat-sender>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const query = ref('');
const loading = ref(false);

// 模拟消息发送
const inputEnter = function () {
  if (loading.value) {
    return;
  }
  if (!query.value) return;
  query.value = '';
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 5000);
};
</script>

<style>
.test {
  color: var(--td-brand-color);
}
</style>
```

---

## 附件输入

支持选择附件及展示附件列表，受控进行文件数据管理，示例中模拟了文件上传流程

```vue
<template>
  <t-chat-sender
    v-model="query"
    :stop-disabled="loading"
    :textarea-props="{
      placeholder: '请输入消息...',
    }"
    :attachments-props="{
      items: filesList,
      overflow: 'scrollX',
    }"
    @send="inputEnter"
    @file-select="handleUploadFile"
    @file-click="handleFileClick"
    @remove="handleRemoveFile"
  >
    <!-- 自定义操作区域的内容，默认支持图片上传、附件上传和发送按钮 -->
    <template #suffix="{ renderPresets }">
      <!-- 在这里可以进行自由的组合使用，或者新增预设 -->
      <!-- 不需要附件操作的使用方式 -->
      <!-- <component :is="renderPresets([])" /> -->
      <!-- 只需要附件上传的使用方式-->
      <!-- <component :is="renderPresets([{ name: 'uploadAttachment' }])" /> -->
      <!-- 只需要图片上传的使用方式-->
      <!-- <component :is="renderPresets([{ name: 'uploadImage' }])" /> -->
      <!-- 任意配置顺序-->
      <component :is="renderPresets([{ name: 'uploadImage' }, { name: 'uploadAttachment' }])" />
    </template>
  </t-chat-sender>
</template>

<script setup lang="ts">
import { TdAttachmentItem } from '@tdesign-vue-next/chat';
import { ref } from 'vue';

const query = ref('');
const loading = ref(false);

// 模拟消息发送
const inputEnter = function (inputValue: string) {
  if (loading.value) {
    return;
  }
  if (!inputValue) return;
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 5000);
};

const filesList = ref<TdAttachmentItem[]>([
  {
    key: '1',
    name: 'excel-file.xlsx',
    size: 111111,
  },
  {
    key: '2',
    name: 'word-file.docx',
    size: 222222,
  },
  {
    key: '3',
    name: 'image-file.png',
    size: 333333,
  },
  {
    key: '4',
    name: 'pdf-file.pdf',
    size: 444444,
  },
]);

const handleRemoveFile = (e: CustomEvent<TdAttachmentItem>) => {
  filesList.value = filesList.value.filter((item) => item.key !== e.detail.key);
};

const handleUploadFile = ({ files, name, e }) => {
  console.log('🚀 ~ handleUploadFile ~ eYLog :', e, files, name);
  // 添加新文件并模拟上传进度
  const newFile = {
    size: files[0].size,
    name: files[0].name,
    status: 'progress' as TdAttachmentItem['status'],
    description: '上传中',
  };
  filesList.value = [newFile, ...filesList.value];
  console.log('🚀 ~ handleUploadFile ~ filesListYLog :', filesList);
  setTimeout(() => {
    filesList.value = filesList.value.map((file) =>
      file.name === newFile.name
        ? {
            ...file,
            url: 'https://tdesign.gtimg.com/site/avatar.jpg',
            status: 'success',
            description: `${Math.floor(newFile.size / 1024)}KB`,
          }
        : file,
    );
  }, 1000);
};

const handleFileClick = (e: CustomEvent<TdAttachmentItem>) => {
  console.log('fileClick', e.detail);
};
</script>
```

---

## 输入框自定义

可输入区域前置部分 `input-prefix`，输入框底部左侧区域 `footer-prefix`，输入框底部操作区域 `suffix`

```vue
<template>
  <t-chat-sender
    ref="chatSenderRef"
    v-model="inputValue"
    class="chat-sender"
    :textarea-props="{
      placeholder: options.filter((item) => item.value === scene)[0].placeholder,
    }"
    :loading="loading"
    @send="inputEnter"
  >
    <template #input-prefix>
      <t-dropdown
        :options="options"
        trigger="click"
        :style="{ padding: 0 }"
        @click="switchScene"
      >
        <t-tag
          shape="round"
          variant="light"
          color="var(--td-brand-color)"
          :style="{ marginRight: '4px', cursor: 'pointer' }"
        >
          {{ options.filter((item) => item.value === scene)[0].content }}
        </t-tag>
      </t-dropdown>
    </template>
    
    <template #footer-prefix>
      <div class="model-select">
        <t-tooltip v-model:visible="allowToolTip" content="切换模型" trigger="hover">
          <t-select
            v-model="selectValue"
            :options="selectOptions"
            value-type="object"
            @focus="allowToolTip = false"
          ></t-select>
        </t-tooltip>
        <t-button
          class="check-box"
          :class="{ 'is-active': isChecked }"
          variant="outline"
          @click="checkClick"
        >
          <SystemSumIcon />
          <span>深度思考</span>
        </t-button>
      </div>
    </template>
  </t-chat-sender>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { SystemSumIcon } from 'tdesign-icons-vue-next';

const loading = ref(false);
const allowToolTip = ref(false);
const chatSenderRef = ref(null);
const inputValue = ref('');

const options = [
  {
    content: '帮我写作',
    value: 1,
    placeholder: '输入你要撰写的主题',
  },
  {
    content: '图像生成',
    value: 2,
    placeholder: '说说你的创作灵感',
  },
  {
    content: '网页摘要',
    value: 3,
    placeholder: '输入你要解读的网页地址',
  },
];

const scene = ref(1);

const selectOptions = [
  {
    label: '默认模型',
    value: 'default',
  },
  {
    label: 'Deepseek',
    value: 'deepseek-r1',
  },
  {
    label: '混元',
    value: 'hunyuan',
  },
];

const selectValue = ref({
  label: '默认模型',
  value: 'default',
});

const isChecked = ref(false);

const checkClick = () => {
  isChecked.value = !isChecked.value;
};

// 模拟消息发送
const inputEnter = function () {
  if (loading.value) {
    return;
  }
  if (!inputValue.value) return;
  inputValue.value = '';
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 5000);
};

const switchScene = (data: any) => {
  scene.value = data.value;
};
</script>

<style lang="less">
.chat-sender {
  .btn {
    color: var(--td-text-color-disabled);
    border: none;
    &:hover {
      color: var(--td-brand-color-hover);
      border: none;
      background: none;
    }
  }
  .btn.t-button {
    height: var(--td-comp-size-m);
    padding: 0;
  }
  .model-select {
    display: flex;
    align-items: center;
    .t-select {
      width: 112px;
      height: var(--td-comp-size-m);
      margin-right: var(--td-comp-margin-s);
      .t-input {
        border-radius: 32px;
        padding: 0 15px;
      }
      .t-input.t-is-focused {
        box-shadow: none;
      }
    }
    .check-box {
      width: 112px;
      height: var(--td-comp-size-m);
      border-radius: 32px;
      box-sizing: border-box;
      flex: 0 0 auto;
      .t-button__text {
        display: flex;
        align-items: center;
        justify-content: center;
        span {
          margin-left: var(--td-comp-margin-s);
        }
      }
    }
    .check-box.is-active {
      border: 1px solid var(--td-brand-color-focus);
      background: var(--td-brand-color-light);
      color: var(--td-text-color-brand);
    }
  }
}
</style>
```

---

## 综合示例

```vue
<template>
  <t-chat-sender
    ref="chatSenderRef"
    v-model="inputValue"
    class="chat-sender"
    :textarea-props="{
      placeholder: '请输入消息...',
    }"
    :attachments-props="{
      items: filesList,
      overflow: 'scrollX',
    }"
    :loading="loading"
    @send="inputEnter"
    @file-select="handleUploadFile"
    @file-click="handleFileClick"
    @remove="handleRemoveFile"
  >
    <template #suffix="{ renderPresets }">
      <component :is="renderPresets([{ name: 'uploadImage' }, { name: 'uploadAttachment' }])" />
    </template>
    
    <template #footer-prefix>
      <div class="model-select">
        <t-tooltip v-model:visible="allowToolTip" content="切换模型" trigger="hover">
          <t-select
            v-model="selectValue"
            :options="selectOptions"
            value-type="object"
            @focus="allowToolTip = false"
          ></t-select>
        </t-tooltip>
        <t-button
          class="check-box"
          :class="{ 'is-active': isChecked }"
          variant="outline"
          @click="checkClick"
        >
          <SystemSumIcon />
          <span>深度思考</span>
        </t-button>
      </div>
    </template>
    
    <template #inner-header>
      <div
        :style="{
          display: 'flex',
          width: '100%',
          marginBottom: '8px',
          paddingBottom: '8px',
          justifyContent: 'space-between',
          alignItem: 'center',
          borderBottom: '1px solid var(--td-component-stroke)',
        }"
      >
        <div :style="{ flex: 1, display: 'flex', alignItems: 'center' }">
          <EnterIcon
            :size="'20px'"
            :style="{
              color: 'var(--td-text-color-disabled)',
              transform: 'scaleX(-1)',
              padding: '6px',
            }"
          />
          <p
            :style="{
              fontSize: '14px',
              color: 'var(--td-text-color-placeholder)',
              marginLeft: '4px',
            }"
          >
            "牛顿第一定律（惯性定律）仅适用于惯性参考系，而不适用于非惯性参考系。"
          </p>
        </div>
        <CloseIcon
          :size="'20px'"
          :style="{ color: 'var(--td-text-color-disabled)', padding: '6px' }"
          @click="onRemoveRef"
        />
      </div>
    </template>
  </t-chat-sender>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { SystemSumIcon, EnterIcon, CloseIcon } from 'tdesign-icons-vue-next';
import { TdAttachmentItem } from '@tdesign-vue-next/chat';

const loading = ref(false);
const allowToolTip = ref(false);
const chatSenderRef = ref(null);
const inputValue = ref('');

const selectOptions = [
  {
    label: '默认模型',
    value: 'default',
  },
  {
    label: 'Deepseek',
    value: 'deepseek-r1',
  },
  {
    label: '混元',
    value: 'hunyuan',
  },
];

const selectValue = ref({
  label: '默认模型',
  value: 'default',
});

const isChecked = ref(false);

const filesList = ref<TdAttachmentItem[]>([
  {
    key: '1',
    name: 'excel-file.xlsx',
    size: 111111,
  },
  {
    key: '2',
    name: 'word-file.docx',
    size: 222222,
  },
  {
    key: '3',
    name: 'image-file.png',
    size: 333333,
  },
  {
    key: '4',
    name: 'pdf-file.pdf',
    size: 444444,
  },
]);

const checkClick = () => {
  isChecked.value = !isChecked.value;
};

// 模拟消息发送
const inputEnter = function () {
  if (loading.value) {
    return;
  }
  if (!inputValue.value) return;
  inputValue.value = '';
  loading.value = true;
  setTimeout(() => {
    loading.value = false;
  }, 5000);
};

const handleRemoveFile = (e: CustomEvent<TdAttachmentItem>) => {
  filesList.value = filesList.value.filter((item) => item.key !== e.detail.key);
};

const handleUploadFile = ({ files, name, e }) => {
  console.log('🚀 ~ handleUploadFile ~ eYLog :', e, files, name);
  // 添加新文件并模拟上传进度
  const newFile = {
    size: files[0].size,
    name: files[0].name,
    status: 'progress' as TdAttachmentItem['status'],
    description: '上传中',
  };
  filesList.value = [newFile, ...filesList.value];
  console.log('🚀 ~ handleUploadFile ~ filesListYLog :', filesList);
  setTimeout(() => {
    filesList.value = filesList.value.map((file) =>
      file.name === newFile.name
        ? {
            ...file,
            url: 'https://tdesign.gtimg.com/site/avatar.jpg',
            status: 'success',
            description: `${Math.floor(newFile.size / 1024)}KB`,
          }
        : file,
    );
  }, 1000);
};

const handleFileClick = (e: CustomEvent<TdAttachmentItem>) => {
  console.log('fileClick', e.detail);
};
</script>

<style lang="less">
.chat-sender {
  .btn {
    color: var(--td-text-color-disabled);
    border: none;
    &:hover {
      color: var(--td-brand-color-hover);
      border: none;
      background: none;
    }
  }
  .btn.t-button {
    height: var(--td-comp-size-m);
    padding: 0;
  }
  .model-select {
    display: flex;
    align-items: center;
    .t-select {
      width: 112px;
      height: var(--td-comp-size-m);
      margin-right: var(--td-comp-margin-s);
      .t-input {
        border-radius: 32px;
        padding: 0 15px;
      }
      .t-input.t-is-focused {
        box-shadow: none;
      }
    }
    .check-box {
      width: 112px;
      height: var(--td-comp-size-m);
      border-radius: 32px;
      box-sizing: border-box;
      flex: 0 0 auto;
      .t-button__text {
        display: flex;
        align-items: center;
        justify-content: center;
        span {
          margin-left: var(--td-comp-margin-s);
        }
      }
    }
    .check-box.is-active {
      border: 1px solid var(--td-brand-color-focus);
      background: var(--td-brand-color-light);
      color: var(--td-text-color-brand);
    }
  }
}
</style>
```

---

## API

### Props

| 属性 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| v-model | string | - | 输入框内容 |
| loading | boolean | false | 加载状态 |
| stop-disabled | boolean | false | 停止按钮是否禁用 |
| textarea-props | TextareaProps | - | 透传给 Textarea 组件的属性 |
| attachments-props | AttachmentsProps | - | 附件配置，包含 `items`、`overflow` 等 |
| upload-props | UploadProps | - | 上传配置，包含 `accept` 等 |
| actions | TdChatSenderActionName[] | - | 操作按钮配置 |
| placeholder | string | '请输入...' | 输入框占位符 |

### Events

| 事件 | 参数 | 说明 |
|------|------|------|
| send | (value: string) | 发送消息时触发 |
| stop | - | 停止生成时触发 |
| change | (e: CustomEvent<string>) | 输入内容变化时触发 |
| focus | - | 输入框获得焦点时触发 |
| blur | - | 输入框失去焦点时触发 |
| file-select | ({ files, name, e }) | 选择文件时触发 |
| file-click | (e: CustomEvent<TdAttachmentItem>) | 点击文件时触发 |
| remove | (e: CustomEvent<TdAttachmentItem>) | 移除文件时触发 |

### Slots

| 插槽 | 参数 | 说明 |
|------|------|------|
| input-prefix | - | 输入框前置内容 |
| footer-prefix | - | 输入框底部左侧区域 |
| suffix | `{ renderPresets }` | 输入框底部操作区域，`renderPresets` 用于渲染预设按钮 |
| inner-header | - | 输入框内部顶部区域（用于引用消息等） |

### TdChatSenderActionName 类型

```typescript
type TdChatSenderActionName = 'uploadImage' | 'uploadAttachment' | 'send' | 'stop';
```

### renderPresets 用法

```vue
<template #suffix="{ renderPresets }">
  <!-- 不需要任何按钮 -->
  <component :is="renderPresets([])" />
  
  <!-- 只需要发送按钮 -->
  <component :is="renderPresets([{ name: 'send' }])" />
  
  <!-- 图片上传 + 附件上传 -->
  <component :is="renderPresets([{ name: 'uploadImage' }, { name: 'uploadAttachment' }])" />
</template>
```

---

## 相关链接

- 组件文档: https://tdesign.tencent.com/chat/components/chat-sender
