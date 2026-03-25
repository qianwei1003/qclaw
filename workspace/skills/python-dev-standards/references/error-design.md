# Error Design

## 异常 vs 返回值的分界线

**CLI 包装层**（main 函数或 click/argparse 命令）：捕获异常，返回 `(bool, str)`

**内部库函数**（被其他函数调用）：抛异常

不允许在同一个函数中同时使用两种方式。

```python
# CLI 包装层：捕获异常，返回 tuple
def main():
    try:
        ok, msg = process_video(input_path, output_path)
        print(f"成功: {msg}" if ok else f"失败: {msg}")
    except VideoEditError as e:
        print(f"失败: {e}")

# 内部库函数：抛异常，不返回 tuple
def process_video(input_path, output_path) -> bool:
    if not Path(input_path).exists():
        raise FileNotFound(f"文件不存在: {input_path}")
    return True
```

## 异常类设计

每类错误定义一个专用异常。不使用通用 `Exception`。

```python
class VideoEditError(Exception): pass
class FFmpegError(VideoEditError): pass
class FileNotFound(VideoEditError): pass
class InvalidParameter(VideoEditError): pass
```

## 异常链

异常向上传递时，必须保留原始异常。

```python
# 禁止：丢失原始异常
except Exception:
    raise VideoEditError("失败")

# 必须：保留原始异常
except Exception as e:
    raise VideoEditError(f"失败: {e}") from e
```

## 错误信息质量

好的错误信息包含：
- **发生了什么**（不是"失败"）
- **在哪里**（文件路径、参数名、函数名）
- **已知原因**（如有）
- **如何修复**（如用户可操作）

## 函数参数设计原则

**所有参数都必须有默认值，且可被调用方覆盖。**

```python
# 错误：没有默认值
def detect_scenes(video_path, threshold):  # ❌ threshold 必须传
    ...

# 正确：有默认值，可选传
def detect_scenes(video_path, threshold: float = 27.0):
    ...
    return scenes
```

例外：必填参数（文件路径、操作类型）不需要默认值，但调用方必须传值。

此原则适用于所有函数，包括内部函数。

| 情况 | 处理 |
|------|------|
| 类型错误 | 抛 `InvalidParameter` |
| 值超出范围 | 抛 `InvalidParameter` |
| 逻辑冲突（如 start > end） | 抛 `InvalidParameter` |
| 文件不存在 | 抛 `FileNotFound` |
| 可恢复（网络超时） | 重试（有限次、有间隔） |
| 不可恢复（参数错误） | 直接抛异常 |

## 记录 vs 抛出

| 情况 | 动作 |
|------|------|
| 用户可修复的问题 | 抛异常，说明如何修复 |
| 异常但不影响结果 | `logger.warning` |
| 严重到程序无法继续 | 抛异常，不吞掉 |

禁止同时记录又抛出。
