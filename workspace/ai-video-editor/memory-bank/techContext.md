# 技术上下文

## 技术栈

| 层级 | 技术 | 版本 | 备注 |
|---|---|---|---|
| 语言 | Python | 3.12 | |
| 视频处理 | FFmpeg | 7.x | 必须在系统 PATH 中 |
| 帧分析 | OpenCV | `opencv-python` | Analyzer 使用 |
| 音频分析 | NumPy | 最新版 | Analyzer 中 PCM 处理 |
| 视频下载 | yt-dlp | 最新版 | 独立工具，不在核心模块中 |

## 开发环境
- 操作系统：Windows 10 x64
- Shell：PowerShell
- 工作目录：`C:\Users\admin\.qclaw\workspace\ai-video-editor`

## 关键依赖

| 包 | 用途 |
|---|---|
| `opencv-python` | 场景检测和静止帧删除的帧差分析 |
| `numpy` | `analyze_audio_energy` 中的音频 PCM 缓冲处理 |
| `ffmpeg`（系统级） | 所有视频/音频操作 |

## 约束
- FFmpeg 需单独安装，不随项目打包
- 传给 FFmpeg 的 Windows 路径分隔符必须转为 `/`（`_normalize_path()` 处理）
- PowerShell 不支持 `&&`，链式命令用 `;`
- CLI 中通过 `--params` 传入的 JSON 必须使用双引号，单引号在 PowerShell 中会失败

## 运行方式

```bash
# 安装 Python 依赖
pip install opencv-python numpy

# 执行视频操作
python edit_video.py --operation info --input tests/1.mp4

# 查看所有支持的操作
python edit_video.py --list-operations
```

## 代码仓库
- 远程：`github.com:qianwei1003/qclaw.git`
- 分支：`main`
- 项目路径：`workspace/ai-video-editor/`
