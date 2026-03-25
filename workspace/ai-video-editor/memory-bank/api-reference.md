# API 参考

## 入口脚本

| 脚本 | 位置 | 输入 | 输出 |
|------|------|------|------|
| `edit_video.py` | 项目根目录 | `--operation`、`--input`、`--output`、`--params JSON` | `{"success": bool, "message": str, "data": dict}` |

```bash
python edit_video.py --operation trim_start --input video.mp4 --output out.mp4 --params '{"start_time": 5.0}'
```

## 支持的操作

| 操作 | 必填参数 | 可选参数 |
|------|---------|---------|
| `trim_start` | `start_time`（浮点数，秒） | — |
| `trim_end` | `end_time`（浮点数，秒） | — |
| `trim_range` | `start_time`、`end_time`（浮点数） | — |
| `concat` | `files`（路径列表） | — |
| `convert` | `width`、`height`（整数，像素） | — |
| `remove_silence` | — | `threshold`（dB，默认 -40） |
| `remove_static` | — | `threshold`（像素差异均值，默认 5.0）、`min_static_duration`（秒，默认 0.3） |
| `detect_scenes` | — | `threshold`（敏感度，默认 0.4，越低越敏感）、`min_scene_duration`（秒，默认 1.0） |
| `split_by_scenes` | — | `threshold`、`min_scene_duration`。`--output` 是目录，不是文件 |
| `info` | —（不需要 `--output`） | — |

## 返回值结构

### 成功
```json
{
  "success": true,
  "message": "Clip success! (12.34s)",
  "data": {
    "output_path": "C:/path/to/output.mp4",
    "duration": 12.34,
    "resolution": [1920, 1080],
    "file_size": 1048576
  }
}
```

### 失败
```json
{
  "success": false,
  "message": "Missing required params for 'trim_start': ['start_time']",
  "data": {
    "example": {"start_time": 5.0}
  }
}
```

### info 操作
```json
{
  "success": true,
  "message": "Video info retrieved",
  "data": {
    "duration": 195.54,
    "resolution": [1920, 1080],
    "fps": 30.0,
    "has_audio": true,
    "codec": "h264"
  }
}
```

## 调用约定

- 所有路径必须是**绝对路径**
- `--params` 值必须是合法 JSON，使用**双引号**
- 时间值统一用**浮点秒数**（调用前将 "1:30" 转为 90.0）
- 先检查 `success` 字段，再读取 `data`
- 参数缺失时，响应中包含 `data.example`，可直接用于重试

## 错误自纠正

```json
// AI 收到：
{"success": false, "message": "Missing required params for 'trim_start': ['start_time']",
 "data": {"example": {"start_time": 5.0}}}

// AI 应：补充 start_time 参数后重试
```

## 内部模块

### Analyzer

```python
from modules.analyzer import Analyzer

analyzer = Analyzer()

# 检测静止帧段
segments = analyzer.detect_static_segments(
    video_path,
    threshold=5.0,        # 像素差异均值 0-255
    min_duration=0.3,    # 最少持续秒数
    skip_seconds=0.5      # 采样间隔
)
# 返回: [(start, end), ...]

# 检测静音段
silent = analyzer.detect_audio_silence(
    video_path,
    noise_db=-40          # 低于此分贝视为静音
)

# 提取音频
wav_path = analyzer.extract_audio(video_path)

# 提取缩略图
thumb_path = analyzer.extract_thumbnail(video_path, timestamp=5.0)

# 分析音频能量
energy_curve = analyzer.analyze_audio_energy(video_path)
```

### Executor

```python
from modules.executor import Executor, ExecutionError

executor = Executor()

try:
    result = executor.execute(
        operation="trim_range",
        input_video="input.mp4",
        output_video="output.mp4",
        params={"start_time": 10.0, "end_time": 60.0}
    )
except ExecutionError as e:
    print(f"执行失败: {e}")
```

### Validator

```python
from modules.validator import Validator, ValidationError

validator = Validator()
is_valid = validator.validate(output_video)
# 返回: True / False
```

## 禁止行为

- ❌ 不要将自然语言传给 `--params`，必须是结构化 JSON
- ❌ 不要使用相对路径，调用前必须转为绝对路径
- ❌ 不要直接调用 Analyzer，通过 `edit_video.py` 间接调用
