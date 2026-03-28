# AI 视频剪辑器

通过 AI 自动化视频剪辑，无需手动操作即可完成基础剪辑工作。

---

## 项目目标

一个 AI 驱动的视频剪辑工具，用户通过自然语言描述剪辑需求，AI 理解意图并调用结构化工具执行，无需手动操作。

---

## 功能特点

| 阶段 | 功能 | 状态 |
|------|------|------|
| **V1** | 基础自动剪辑 | ✅ 完成 |
| | - 删除静音段 | ✅ |
| | - 删除静止帧段 | ✅ |
| | - 裁剪、合并、转换 | ✅ |
| **V2** | 场景分割 | ✅ 完成 |
| | - 场景检测 | ✅ |
| | - AI 辅助场景选择 | ✅ |
| | - 内容密度分析 | ✅ |
| **V3** | 自动字幕 | ✅ 完成 |
| | - Whisper 语音识别 | ✅ |
| | - SRT 生成 | ✅ |
| | - 字幕烧录 | ✅ |
| **V4** | 智能剪辑 | ⏳ 待开发 |
| | - AI 决策层 | ⏳ 待开发 |
| | - Pipeline 执行引擎 | ⏳ 待开发 |

---

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 基础用法

```bash
# 自动删除静音
python edit_video.py --operation remove_silence --input video.mp4 --output output.mp4

# 场景检测
python edit_video.py --operation detect_scenes --input video.mp4

# 生成字幕
python edit_video.py --operation auto_subtitle --input video.mp4 --output output.mp4
```

---

## 项目结构

```
ai-video-editor/
├── edit_video.py          # AI 调用入口（结构化 CLI）
├── main.py                # VideoEditor 主类
├── config.yaml            # 配置文件
├── modules/               # 核心模块
│   ├── analyzer.py        # 视频分析入口
│   ├── audio.py           # 音频处理
│   ├── scene.py           # 场景检测
│   ├── content.py         # 内容分析
│   ├── subtitle.py        # 字幕生成
│   ├── executor.py        # 执行引擎
│   └── validator.py       # 输出验证
├── tests/                 # 测试文件
└── docs/                  # 设计文档
```

---

## 架构概览

```
用户 / AI
    ↓
edit_video.py              # 结构化 CLI 入口
    ↓
Executor                   # 执行引擎
    ↓
Analyzer                   # 分析层（共用）
    ├── audio.py           # 音频分析
    ├── scene.py           # 场景检测
    ├── content.py         # 内容分析
    └── subtitle.py        # 字幕生成
    ↓
FFmpeg                    # 实际视频处理
```

---

## 下一步：V4 智能剪辑

V4 需要新增：
1. **决策层（Planner）** - 从分析结果生成剪辑决策
2. **Pipeline 执行引擎** - 链式执行、回滚、Dry-run

详见 [ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

_Last updated: 2026-03-28_
