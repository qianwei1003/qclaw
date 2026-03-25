# AI 调用上下文

## AI 如何使用本工具
AI 接收用户的自然语言剪辑需求，映射为结构化操作和参数，调用 `edit_video.py`，解析 JSON 结果，向用户报告。

## 工具接口

| 脚本 | 位置 | 输入 | 输出 |
|---|---|---|---|
| `edit_video.py` | 项目根目录 | `--operation`、`--input`、`--output`、`--params JSON` | `{"success": bool, "message": str, "data": dict}` |

## 支持的操作

| 操作 | 必填参数 | 可选参数 |
|---|---|---|
| `trim_start` | `start_time`（浮点数，秒） | — |
| `trim_end` | `end_time`（浮点数，秒） | — |
| `trim_range` | `start_time`、`end_time`（浮点数） | — |
| `concat` | `files`（路径列表） | — |
| `convert` | `width`、`height`（整数，像素） | — |
| `remove_silence` | — | `threshold`（dB，默认 -40） |
| `remove_static` | — | `threshold`（0–1，默认 0.01）、`min_static_duration`（秒，默认 1.0） |
| `info` | —（不需要 `--output`） | — |

## 调用约定
- 所有路径必须是**绝对路径**
- `--params` 值必须是合法 JSON，使用**双引号**
- 时间值统一用**浮点秒数**（调用前将 "1:30" 转为 90.0）
- 先检查 `success` 字段，再读取 `data`
- 参数缺失时，响应中包含 `data.example`，可直接用于重试

## AI 职责划分

| AI 负责 | 工具负责 |
|---|---|
| 判断用户意图对应哪个操作 | FFmpeg 命令构建 |
| 从自然语言中提取参数值 | 路径格式标准化 |
| 输出文件命名（用户未指定时） | 临时文件管理 |
| 错误恢复策略 | 输出验证 |

## 输出文件命名规范
用户未指定输出路径时：
```
<输入文件名>_<操作名>.<扩展名>
例：interview_trim_start.mp4
```

## 错误自纠正模式
```json
// AI 收到：
{"success": false, "message": "Missing required params for 'trim_start': ['start_time']",
 "data": {"example": {"start_time": 5.0}}}

// AI 应：补充 start_time 参数后重试
```

## 禁止行为
- ❌ 不要将自然语言传给 `--params`，必须是结构化 JSON
- ❌ 不要使用相对路径，调用前必须转为绝对路径
- ❌ 不要直接调用 Analyzer，`edit_video.py` 是唯一入口
