# AI 视频剪辑器

通过自然语言指令自动完成视频剪辑，组合现有开源工具，用 AI 做决策。

## 功能特点

- 🎬 **自然语言控制** — 说话就能剪辑，不用记命令
- ✂️ **智能多段剪辑** — 支持只保留多个时间段，自动合并
- 🔇 **自动删除静音** — 去掉视频里的空白静音段
- 🎥 **场景自动分割** — 检测镜头切换，自动分割场景（规划中）
- 📝 **自动生成字幕** — 语音识别生成字幕（规划中）
- ✨ **智能精彩片段** — AI 识别精彩片段（规划中）

## 快速开始

### 安装依赖

```bash
# 安装 FFmpeg（必须）
# Windows: https://ffmpeg.org/download.html
# Mac: brew install ffmpeg
# Linux: sudo apt install ffmpeg

# 安装 auto-editor（可选，用于静音检测）
pip install auto-editor
```

### 基础用法

```bash
# 自然语言指令剪辑
python main.py "删除前 10 秒" input.mp4 output.mp4
python main.py "只保留 0分到30分" input.mp4 output.mp4
python main.py "只保留0到10和30到50" input.mp4 output.mp4   # 多段截取
python main.py "删除静音段" input.mp4 output.mp4

# 合并多个视频
python main.py "合并 video1.mp4 和 video2.mp4" video1.mp4 output.mp4

# 转换分辨率
python main.py "转换为 1080p" input.mp4 output.mp4
```

### Python API

```python
from ai_video_editor import VideoEditor

editor = VideoEditor()

result = editor.edit(
    instruction="删除静音段",
    input_video="input.mp4",
    output_video="output.mp4"
)

if result["success"]:
    print(f"完成! 耗时 {result['execution_time']:.2f} 秒")
else:
    for err in result["errors"]:
        print(f"错误: {err}")
```

## 支持的指令

| 指令 | 示例 |
|------|------|
| 删除开头 | "删除前 10 秒" |
| 删除结尾 | "删除最后 5 秒" |
| 单段截取 | "只保留 1:00 到 3:00" |
| 多段截取 | "只保留 0到10和30到50" |
| 合并视频 | "合并 video1.mp4 和 video2.mp4" |
| 转换分辨率 | "转换为 1080p" / "转换为 4k" |
| 删除静音 | "删除静音段" |

## 项目结构

```
ai-video-editor/
├── main.py                 # 主入口（VideoEditor 类 + CLI）
├── modules/
│   ├── parser.py          # 需求解析（自然语言 → 结构化指令）
│   ├── executor.py        # 执行器（调用 FFmpeg）
│   └── validator.py       # 验证器（检查输出）
├── tests/                  # 测试视频和脚本
└── docs/                   # 详细文档
```

## 文档

- [PROJECT_PLAN.md](PROJECT_PLAN.md) — 开发计划与进度
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — 技术架构
- [docs/API_DESIGN.md](docs/API_DESIGN.md) — API 设计
- [docs/WORKFLOW.md](docs/WORKFLOW.md) — 处理流程
- [docs/TEST_PLAN.md](docs/TEST_PLAN.md) — 测试方案
- [docs/ERROR_HANDLING.md](docs/ERROR_HANDLING.md) — 错误处理

## 当前进度

| 阶段 | 功能 | 状态 |
|------|------|------|
| 通用基础设施 | Parser / Executor / Validator | ✅ 已完成 |
| V1 基础剪辑 | 删除静音 / 多段截取 / 合并 / 转换 | ✅ 已完成 |
| V2 场景分割 | 镜头切换检测 | ⏳ 规划中 |
| V3 自动字幕 | Whisper 语音识别 | ⏳ 规划中 |
| V4 智能剪辑 | 精彩片段检测 | ⏳ 规划中 |

---

_Last updated: 2026-03-24_
