# TDesign Chat 组件文档索引

> 来源: https://tdesign.tencent.com/chat  
> 整理时间: 2026-03-21  
> 版本: 0.5.1

---

## 📚 文档结构

```
tdesign/
├── TDesign-Chat-快速开始.md          ← 已整理 ✅
├── TDesign-Chat-组件文档索引.md      ← 本文档
├── components/
│   ├── Chatbot.md                    ← 已整理 ✅
│   ├── ChatEngine.md                 ← 待整理
│   ├── ChatSender.md                 ← 待整理
│   ├── ChatMessage.md                ← 待整理
│   ├── ChatActionbar.md              ← 待整理
│   ├── ChatMarkdown.md               ← 待整理
│   ├── ChatThinking.md               ← 待整理
│   ├── ChatLoading.md                ← 待整理
│   ├── Attachments.md                ← 待整理
│   ├── ChatList.md                   ← 待整理
│   └── ChatContent.md                ← 待整理
├── guide/
│   ├── 概述.md                       ← 待整理
│   ├── 更新日志.md                   ← 待整理
│   ├── 流式输出(SSE).md              ← 待整理
│   └── AG-UI协议集成.md              ← 待整理
└── theme/
    ├── 自定义主题.md                 ← 待整理
    ├── 深色模式.md                   ← 待整理
    └── 自定义样式.md                 ← 待整理
```

---

## 🧩 组件清单

### 核心组件

| 组件 | 说明 | 复杂度 | 状态 |
|------|------|--------|------|
| **Chatbot** | 高度封装的一体化智能对话组件 | ⭐⭐⭐ | ✅ 已整理 |
| **ChatEngine** | 底层对话引擎，提供 Hook API | ⭐⭐⭐⭐⭐ | 📝 已获取 |
| **ChatSender** | 对话输入组件 | ⭐⭐ | ⏳ 待爬取 |
| **ChatMessage** | 对话消息体组件 | ⭐⭐⭐ | ⏳ 待爬取 |
| **ChatActionbar** | 对话操作栏 | ⭐⭐ | ⏳ 待爬取 |

### 内容组件

| 组件 | 说明 | 复杂度 | 状态 |
|------|------|--------|------|
| **ChatMarkdown** | Markdown 内容渲染 | ⭐⭐ | ⏳ 待爬取 |
| **ChatThinking** | 思考过程展示 | ⭐⭐ | ⏳ 待爬取 |
| **ChatLoading** | 对话加载状态 | ⭐ | ⏳ 待爬取 |
| **Attachments** | 文件附件 | ⭐⭐ | ⏳ 待爬取 |

### 布局组件

| 组件 | 说明 | 复杂度 | 状态 |
|------|------|--------|------|
| **ChatList** | 对话列表容器 | ⭐⭐ | ⏳ 待爬取 |
| **ChatContent** | 对话正文 | ⭐⭐ | ⏳ 待爬取 |

### 废弃组件

| 组件 | 说明 | 替代方案 |
|------|------|----------|
| ChatItem | 对话单元 | ChatMessage |
| ChatInput | 对话输入 | ChatSender |
| ChatReasoning | 思考过程 | ChatThinking |

---

## 📖 指南文档

| 文档 | 说明 | 状态 |
|------|------|------|
| 概述 | TDesign Chat 整体介绍 | ⏳ 待爬取 |
| 快速开始 | 5分钟上手教程 | ✅ 已整理 |
| 更新日志 | 版本更新记录 | ⏳ 待爬取 |
| 流式输出(SSE) | SSE 技术详解 | ⏳ 待爬取 |
| AG-UI协议集成 | AG-UI 标准协议 | 📝 已获取部分内容 |

---

## 🎨 主题配置

| 文档 | 说明 | 状态 |
|------|------|------|
| 自定义主题 | 主题定制指南 | ⏳ 待爬取 |
| 深色模式 | Dark Mode 配置 | ⏳ 待爬取 |
| 自定义样式 | 样式覆盖方法 | ⏳ 待爬取 |

---

## 🎯 已获取的关键信息

### Chatbot 组件
- ✅ 快速开始示例
- ✅ 初始化消息配置
- ✅ 角色消息配置
- ✅ 输入配置
- ✅ 数据处理（自定义协议 + AG-UI 协议）
- ✅ 实例方法
- ✅ 自定义渲染

### ChatEngine 组件
- ✅ 简介：底层对话引擎，提供 Hook API
- ✅ 快速开始：useChat Hook 基础用法
- ✅ 基础用法：初始化消息、数据处理、实例方法、自定义渲染
- ✅ Headless 事件总线
- ✅ AG-UI 协议支持

---

## 📥 批量爬取脚本

如果你想一次性爬取所有组件，可以使用以下脚本：

```bash
# 创建 URL 列表
cat > tdesign_urls.txt << 'EOF'
https://tdesign.tencent.com/chat/overview
https://tdesign.tencent.com/chat/getting-started
https://tdesign.tencent.com/chat/changelog
https://tdesign.tencent.com/chat/sse
https://tdesign.tencent.com/chat/agui
https://tdesign.tencent.com/chat/custom-theme
https://tdesign.tencent.com/chat/dark-mode
https://tdesign.tencent.com/chat/custom-style
https://tdesign.tencent.com/chat/components/chatbot
https://tdesign.tencent.com/chat/components/chat-engine
https://tdesign.tencent.com/chat/components/chat-sender
https://tdesign.tencent.com/chat/components/chat-message
https://tdesign.tencent.com/chat/components/chat-actionbar
https://tdesign.tencent.com/chat/components/chat-markdown
https://tdesign.tencent.com/chat/components/chat-thinking
https://tdesign.tencent.com/chat/components/chat-loading
https://tdesign.tencent.com/chat/components/attachments
https://tdesign.tencent.com/chat/components/chat-list
https://tdesign.tencent.com/chat/components/chat-content
EOF

# 批量爬取
python skills/web-crawler-doc/scripts/batch_crawl.py \
  --urls-file tdesign_urls.txt \
  --output-dir ./knowledge-base/tdesign/ \
  --workers 1 \
  --delay 3
```

---

## ❓ 接下来做什么？

请告诉我你想优先获取哪些文档：

**选项 1：按优先级**
- 高优先级组件（ChatSender、ChatMessage）
- 中优先级组件（ChatActionbar、ChatMarkdown）
- 低优先级组件（其他）

**选项 2：按场景**
- 快速开发场景（Chatbot + ChatSender）
- 深度定制场景（ChatEngine + 各原子组件）
- 主题定制（自定义主题 + 深色模式）

**选项 3：全部获取**
- 我帮你批量爬取所有剩余文档

**选项 4：指定组件**
- 你指定具体要哪个组件的文档

---

## 🔗 相关链接

- 官网: https://tdesign.tencent.com/chat
- GitHub: https://github.com/Tencent/tdesign-vue-next
- 设计资源: https://tdesign.tencent.com/source
