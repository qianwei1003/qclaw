# AI 视频剪辑器

通过 AI 自动化视频剪辑，无需手动操作即可完成基础剪辑工作。

## 功能特点

- 🎬 **自动删除静音片段** - 自动检测并删除视频中的静音部分
- 🎥 **场景自动分割** - 检测镜头切换，自动分割场景
- 📝 **自动生成字幕** - 语音识别自动生成字幕
- ✨ **智能精彩片段** - AI 识别精彩片段，自动生成短视频

## 快速开始

### 安装依赖

```bash
# 安装 auto-editor
pip install auto-editor

# 安装 FFmpeg（如果还没有）
# Windows: 下载 https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 安装 PySceneDetect（第二阶段）
pip install scenedetect[opencv]

# 安装 Whisper（第三阶段）
pip install openai-whisper
```

### 基础用法

```bash
# 自动删除静音片段
python main.py your_video.mp4

# 查看帮助
python main.py --help
```

## 项目结构

```
ai-video-editor/
├── PROJECT_PLAN.md     # 开发计划
├── README.md           # 本文件
├── config.yaml         # 配置文件
├── main.py             # 主入口
└── modules/            # 功能模块
```

## 开发进度

| 阶段 | 功能 | 状态 |
|------|------|------|
| V1 | 自动删除静音/静止片段 | ⏳ 进行中 |
| V2 | 场景自动分割 | 待开始 |
| V3 | 自动生成字幕 | 待开始 |
| V4 | 智能精彩片段 | 待开始 |

## 配置说明

```yaml
# config.yaml
silence:
  threshold: 0.02      # 静音阈值
  margin: 0.2s         # 保留空白时长

output:
  format: mp4          # 输出格式
  quality: high        # 输出质量
```

## 贡献

欢迎提交 Issue 和 Pull Request！

---

_Last updated: 2026-03-23_
