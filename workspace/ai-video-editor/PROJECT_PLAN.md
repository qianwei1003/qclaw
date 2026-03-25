# AI 视频剪辑器 - 开发计划

## 项目概述

**目标：** 通过 AI 自动化视频剪辑，让用户无需手动操作即可完成基础剪辑工作。

**核心理念：** 不是从零开发，而是组合现有的开源工具，用 AI 做决策，用脚本串联流程。

---

## 技术栈

| 工具 | 用途 | 特点 |
|------|------|------|
| FFmpeg | 视频处理基础工具 | 免费、功能强大 |
| auto-editor | 自动剪辑静音片段 | 免费、命令行、支持导出到 Premiere/DaVinci |
| PySceneDetect | 检测场景变化 | 免费、Python 库、自动分割视频 |
| MoviePy | Python 视频编辑库 | 免费、可编程 |
| Whisper (可选) | 语音识别生成字幕 | OpenAI 开源 |

---

## 开发阶段

### 第一阶段：基础自动剪辑

**目标：** 实现自动删除静音/静止片段

**功能：**
- 自动检测视频中的静音片段并删除
- 自动检测静止画面（屏幕不动）并删除
- 支持调整剪辑节奏（保留多少空白）

**验收标准：**
- [ ] 能够处理一个测试视频
- [ ] 输出删除静音后的视频
- [ ] 处理时间在可接受范围内

**具体任务：**
1. 安装 auto-editor 和 FFmpeg
2. 测试基础剪辑功能
3. 创建 Python 封装脚本
4. 添加参数配置（静音阈值、保留时长等）

### 第二阶段：场景分割

**目标：** 实现场景自动检测和分割

**功能：**
- 检测视频中的场景变化（切换镜头）
- 自动在场景变化处分割视频
- 生成每个场景的缩略图

**验收标准：**
- [ ] 能够检测场景变化
- [ ] 自动分割成多个片段
- [ ] 生成场景列表和时间码

**具体任务：**
1. 安装 PySceneDetect
2. 测试场景检测功能
3. 整合到主脚本中
4. 添加场景预览功能

### 第三阶段：自动字幕

**目标：** 实现语音识别自动生成字幕

**功能：**
- 自动识别视频中的语音
- 生成字幕文件（SRT 格式）
- 将字幕嵌入视频

**验收标准：**
- [ ] 能够识别中文语音
- [ ] 生成正确的字幕时间轴
- [ ] 字幕可导出或嵌入视频

**具体任务：**
1. 安装 Whisper 或其他语音识别工具
2. 测试语音识别准确率
3. 生成 SRT 字幕文件
4. 整合到视频输出流程

### 第四阶段：智能剪辑

**目标：** AI 识别精彩片段，自动生成短视频

**功能：**
- 识别视频中的精彩片段（高潮、转折等）
- 自动生成短视频版本（竖屏/横屏）
- 自动添加背景音乐

**验收标准：**
- [ ] 能够识别精彩片段
- [ ] 自动生成 60 秒短视频
- [ ] 视频节奏合理

**具体任务：**
1. 分析视频特征（音频能量、画面变化等）
2. 定义"精彩"的标准
3. 实现自动选段算法
4. 添加转场和音乐

---

## 完整流程设计

```
原始视频
    ↓
【第1步】AI 分析
    ├─ 分析音频 → 找出静音片段
    ├─ 分析画面 → 找出静止/黑屏片段
    └─ 分析场景 → 找出镜头切换点
    ↓
【第2步】AI 决策
    ├─ 哪些片段要删除？
    ├─ 哪些片段要保留？
    └─ 片段之间如何衔接？
    ↓
【第3步】自动剪辑
    ├─ 删除无效片段
    ├─ 按场景分割
    └─ 添加转场效果
    ↓
【第4步】可选增强
    ├─ 自动添加字幕（语音识别）
    ├─ 自动添加背景音乐
    └─ 自动生成短视频版本
    ↓
输出成品
```

---

## 文件结构

```
ai-video-editor/
├── PROJECT_PLAN.md          # 本文件
├── README.md                # 项目说明
├── ARCHITECTURE.md          # 技术架构文档（更新版）
├── config.yaml              # 配置文件
├── main.py                  # 主入口脚本
├── modules/
│   ├── __init__.py
│   ├── parser.py            # 需求解析模块
│   ├── executor.py          # 执行器模块
│   └── validator.py         # 验证器模块
├── tests/
│   ├── test_video.mp4       # 测试视频
│   ├── generate_test_video.py    # 测试视频生成脚本1
│   └── generate_test_video2.py   # 测试视频生成脚本2（真正的静音）
├── docs/
│   ├── ARCHITECTURE.md      # 技术架构文档
│   ├── API_DESIGN.md        # API 设计文档
│   ├── WORKFLOW.md          # 处理流程文档
│   ├── TEST_PLAN.md          # 测试方案文档
│   └── ERROR_HANDLING.md    # 错误处理规范
└── output/                  # 输出目录
```

---

## 文档索引

| 文档 | 说明 |
|------|------|
| [README.md](../README.md) | 项目说明 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 技术架构文档 |
| [API_DESIGN.md](docs/API_DESIGN.md) | API 设计文档 |
| [WORKFLOW.md](docs/WORKFLOW.md) | 处理流程文档 |
| [TEST_PLAN.md](docs/TEST_PLAN.md) | 测试方案文档 |
| [ERROR_HANDLING.md](docs/ERROR_HANDLING.md) | 错误处理规范 |

---

## 当前进度

- [x] 项目创建
- [x] 开发计划文档
- [x] 技术架构文档（2026-03-24 更新）
- [x] API 设计文档
- [x] 处理流程文档
- [x] 测试方案文档
- [x] 错误处理规范
- [x] **第三阶段：原型实现（已完成）**
  - [x] Step 1: 实现 Parser 模块（需求解析）
  - [x] Step 2: 实现 Executor 模块（执行）
  - [x] Step 3: 实现 Validator 模块（验证）
  - [x] Step 4: 实现主接口（VideoEditor 类 + CLI）
  - [x] Step 5: 测试视频生成脚本
  - [x] Step 6: 准备测试环境 + 演示完整工作流
  - [x] Step 7: 修复 remove_silence（FFmpeg 7.x 兼容）
  - [x] Step 8: 实现 remove_static（OpenCV 帧分析）

---

## 使用方式

```bash
# 基础用法：自动删除静音
python main.py "删除前 10 秒" input.mp4 output.mp4

# 高级用法：指定参数
python main.py "删除静音段" input.mp4 output.mp4

# 完整功能
python main.py "删除静音段" input.mp4 output.mp4 --detect-scenes --generate-subtitles
```

---

## 架构分层

详见 [ARCHITECTURE.md](ARCHITECTURE.md)

| 层级 | 说明 |
|------|------|
| 通用基础设施 | Parser / Executor / Validator / 视频下载 |
| 工具层 | FFmpeg / auto-editor / PySceneDetect / Whisper |
| 业务阶段 | V1: 基础剪辑 / V2: 场景分割 / V3: 字幕 / V4: 智能剪辑 |

---

## 通用基础设施

| 功能 | 状态 | 说明 |
|------|------|------|
| Parser（需求解析） | ✅ 已完成 | 自然语言 → 结构化指令，支持多段截取 |
| Executor（执行器） | ✅ 已完成 | FFmpeg 封装，含多段截取合并 |
| Validator（验证器） | ✅ 已完成 | 输出验证，元数据提取 |
| Analyzer（视频分析） | ✅ 已完成 | extract_audio / detect_scenes / extract_thumbnail / analyze_audio_energy / detect_static_segments |
| 视频下载 | ✅ 已完成 | yt-dlp |

---

## V1: 基础自动剪辑

**目标：** 自动删除静音/静止片段

### 已完成的模块

| 小功能 | 工具 | 状态 |
|--------|------|------|
| 单段截取（从头/从尾/范围） | FFmpeg | ✅ 已完成 |
| 多段截取合并 | FFmpeg | ✅ 已完成 |
| 视频合并 | FFmpeg | ✅ 已完成 |
| 格式转换/分辨率改变 | FFmpeg | ✅ 已完成 |
| 删除静音段 | FFmpeg silenceremove | ✅ 已完成（FFmpeg 7.x 兼容版） |
| 删除静止段 | OpenCV 帧分析 | ✅ 已完成（Analyzer.detect_static_segments） |

### Parser 支持的操作类型

| 操作 | 指令示例 | 状态 |
|------|---------|------|
| trim_start | "删除前 10 秒" | ✅ |
| trim_end | "删除最后 5 秒" | ✅ |
| trim_range | "只保留 1:00 到 3:00" | ✅ |
| trim_range（多段） | "只保留 0到10和30到50" | ✅ |
| concat | "合并 video1.mp4 和 video2.mp4" | ✅ |
| convert | "转换为 1080p" | ✅ |
| remove_silence | "删除静音段" | ✅ |
| remove_static | "删除静止段" | ⚠️ Parser 完成，Executor 待实现 |

### Executor 核心能力

- ✅ 多段截取（`_trim_segments`）：自动分段 → 临时文件 → FFmpeg concat → 合并输出
- ✅ FFmpeg 路径自动检测（Windows 兼容）
- ✅ 自动回退（`-c copy` 失败时重新编码）
- ✅ 临时文件自动清理
- ✅ 获取视频时长（Duration 解析）

---

## 更新记录

| 日期 | 版本 | 更新内容 |
|------|------|---------|
| 2026-03-23 | 1.0 | 项目创建，完成基础文档 |
| 2026-03-24 v1.1 | 1.1 | 完成通用基础设施（Parser/Executor/Validator） |
| 2026-03-24 v1.2 | 1.2 | 完成多段截取合并功能 |
| 2026-03-24 v1.3 | 1.3 | 完成 VideoEditor 主类 + CLI，完整工作流串联 |
| 2026-03-24 v1.4 | 1.4 | 完成全部 6 个文档（架构/流程/测试/API/错误处理） |
| 2026-03-24 v1.5 | 1.5 | 完成测试视频生成脚本（含真正静音段测试视频） |

| 2026-03-25 v1.6 | 1.6 | 新增 Analyzer 模块（extract_audio/detect_scenes/extract_thumbnail/analyze_audio_energy/detect_static_segments），实现 remove_static，建立 V2/V3/V4 共用分析层 |
