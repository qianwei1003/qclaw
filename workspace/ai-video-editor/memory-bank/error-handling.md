# 错误处理规范

## 异常类层次

```python
# modules/executor.py
class ExecutionError(Exception): pass
class ValidationError(Exception): pass

# modules/analyzer.py
class AnalyzerError(Exception): pass
```

```python
# 捕获顺序：从小到大
from modules.executor import ExecutionError
from modules.validator import ValidationError
from modules.analyzer import AnalyzerError

try:
    executor.execute(...)
except ExecutionError as e:
    # 处理执行错误
except ValidationError as e:
    # 处理验证错误
except AnalyzerError as e:
    # 处理分析错误
except Exception as e:
    # 未知错误，记录后上报
```

## 错误信息质量

好的错误信息必须包含：
1. **发生了什么**（不是"失败"，而是具体错误类型）
2. **在哪里**（文件路径、参数名）
3. **已知原因**（如有）

```
差：FFmpeg 失败
好：FFmpeg 返回码 1。命令: ffmpeg -i input.mp4。错误: Invalid data found
```

## 边界条件的错误处理

| 情况 | 处理 |
|------|------|
| 类型错误 | 抛 `InvalidParameter` |
| 值超出范围 | 抛 `InvalidParameter` |
| 逻辑冲突（如 start > end） | 抛 `InvalidParameter` |
| 文件不存在 | 抛 `FileNotFound` |
| 可恢复（网络超时） | 重试（有限次、有间隔） |
| 不可恢复（参数错误） | 直接抛异常 |

## CLI 层错误返回

`edit_video.py` 的 JSON 输出中，`success: false` 时：

```json
{
  "success": false,
  "message": "Missing required params for 'trim_start': ['start_time']",
  "data": {
    "example": {"start_time": 5.0}
  }
}
```

AI 应根据 `data.example` 补充参数后重试。

## FFmpeg 错误处理

FFmpeg subprocess 必须：
- 设置 `timeout`
- 用 `returncode == 0` 判断成功
- 失败时提取 stderr 中的真实错误（跳过进度条）

```python
def _extract_error(stderr: str) -> str:
    import re
    lines = [l.strip() for l in stderr.splitlines()]
    errors = [
        l for l in lines
        if l and not re.match(r'^frame=', l) and not re.match(r'^\[', l)
    ]
    return errors[-1] if errors else "unknown"
```

## 日志规范

```
禁止：print("开始")
必须：logger.info("开始: %s", path)
```

日志级别：`debug` → `info` → `warning` → `error` → `critical`。

禁止同时记录又抛出（重复报告）。
