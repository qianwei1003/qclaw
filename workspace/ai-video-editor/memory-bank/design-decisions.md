# 设计决策

> 本文档记录每个技术决策背后的原因。不讲"是什么"（那是 systemPatterns.md），只讲"为什么这样做"。

## 为什么用这些工具

| 工具 | 选型理由 |
|------|---------|
| FFmpeg | 视频处理行业标准，功能全面，性能优秀 |
| OpenCV | 帧级分析灵活，精确控制采样间隔和阈值 |
| silencedetect | 返回时间段而非整体统计，可定位静音起止 |
| Analyzer 共用模块 | V2/V3/V4 所有阶段都需要分析，拆分避免重复 |

## 为什么用 OpenCV 做静止帧检测，而不是 FFmpeg 的 blackframe？

FFmpeg 的 blackframe 滤镜在 FFmpeg 7.x 行为不稳定，且不支持自定义像素差异阈值。
OpenCV 可以精确控制采样间隔和像素差异阈值，行为可预测。

## 为什么静止帧阈值是 5.0？

经验值。测试了真实幻灯片视频（1.mp4）：
- 翻页动作的帧间差异：> 10
- 停留画面（静止）的帧间差异：< 3
- 设置阈值为 5.0，能区分翻页动作和停留画面

如遇到问题：幻灯片翻页被误判为静止 → 降低到 3.0。

## 为什么静音检测用 silencedetect 而不是 volumedetect？

volumedetect 只给出整体统计（最大音量、平均音量），无法定位时间段。
silencedetect 可以返回每个静音段的起止时间，用于 trim 操作。

## 为什么多段截取用临时文件合并，而不是 filter_complex？

filter_complex 的 concat 滤镜在处理不同编码的视频时容易失败。
临时文件方案更可靠，且可以用 `-c copy` 避免重新编码，保持原始质量。

## 为什么 Analyzer 是独立的共用模块？

Analyzer 的5个方法（音频提取、场景检测、缩略图、音频能量、静止帧检测）
是 V2/V3/V4 所有阶段的基础，共用避免重复分析。

## 为什么放弃自然语言 Parser，改为结构化 CLI？

Parser 无法可靠地理解用户的自然语言指令（歧义、多义词问题）。
改为结构化 CLI 后，AI 理解用户意图后映射为固定操作，精确可控。

## 所有参数必须有默认值，且可被覆盖

参考 `python-dev-standards` 规范。

每个函数的所有参数都必须有默认值，同时允许调用方传入自定义值。

```python
# 正确
def detect_scenes(video_path, threshold: float = 27.0, min_scene_duration: float = 0.5):
    ...

# 错误
def detect_scenes(video_path, threshold):  # ❌ threshold 没有默认值
    ...
```

例外：必填参数（input_video、operation）不需要默认值。

此原则应用于：
- `Analyzer` 所有方法
- `Executor` 所有方法
- `edit_video.py` 的所有操作参数

stream copy 不重新编码，速度快且保持原始质量。
当 `-c copy` 失败时（编码不兼容），才重新编码。

## 为什么 Windows 路径要用正斜杠传给 FFmpeg？

FFmpeg 在 Windows 上接受正斜杠 `/`，但反斜杠 `\` 需要转义。
通过 `_normalize_path()` 统一处理，避免路径错误。

## 为什么并发安全需要 tempfile？

多个进程同时调用时，如果临时文件写当前目录，会相互覆盖。
`tempfile.mkstemp()` 自动生成唯一文件名，避免冲突。

## 为什么 cap.release() 要在 try/finally 中？

VideoCapture 是系统资源，如果异常发生在 `cap.read()` 之前，`cap.release()` 不会被调用。
在 `finally` 中调用确保资源一定被释放。
