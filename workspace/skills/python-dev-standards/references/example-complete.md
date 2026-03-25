# 完整示例：FFmpeg 包装函数

本示例综合应用所有规范，展示一个符合标准的 FFmpeg 调用函数。

## 完整代码

```python
"""
FFmpeg 视频处理模块

符合规范：
- python-patterns.md: 命名、路径、类型注解、日志、临时文件
- ffmpeg-conventions.md: 参数顺序、seek 位置、错误提取
- error-design.md: 异常类设计、异常链
"""

from __future__ import annotations

import logging
import re
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


# 异常类（error-design.md）
class VideoEditError(Exception): pass
class FFmpegError(VideoEditError): pass
class FileNotFound(VideoEditError): pass
class InvalidParameter(VideoEditError): pass


# 数据类（python-patterns.md: 类型注解）
@dataclass
class FFmpegResult:
    success: bool
    duration: float | None
    errors: list[str]


# 错误提取（ffmpeg-conventions.md: 错误提取）
def _extract_error(stderr: str) -> str:
    """提取 stderr 中最后一个真实错误行，跳过进度条"""
    import re
    lines = [l.strip() for l in stderr.splitlines()]
    errors = [
        l for l in lines
        if l and not re.match(r'^frame=', l) and not re.match(r'^\[', l)
    ]
    return errors[-1] if errors else "unknown"


# 内部库函数（error-design.md: 抛异常）
def trim_segment(
    input_video: str,
    output_video: str,
    start: float,
    end: float,
    timeout: int = 60,
) -> float:
    """截取视频片段[start, end)秒。返回实际截取时长。"""
    # 边界检查（error-design.md: 边界条件）
    if not isinstance(start, (int, float)) or not isinstance(end, (int, float)):
        raise InvalidParameter(f"时间必须是数字，got start={start!r}, end={end!r}")
    if start < 0:
        raise InvalidParameter(f"start 不能为负数: {start}")
    if end <= start:
        raise InvalidParameter(f"end({end}) 必须大于 start({start})")

    # 路径处理（python-patterns.md: 路径处理）
    input_path = Path(input_video)
    if not input_path.exists():
        raise FileNotFound(f"文件不存在: {input_path}")

    # FFmpeg 调用（ffmpeg-conventions.md: 参数顺序 + seek）
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start), "-to", str(end),  # seek 在 -i 前（快速）
        "-i", str(input_path),
        "-c", "copy",
        str(output_video),
    ]

    logger.info("执行: %s", " ".join(cmd))

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        raise FFmpegError(f"FFmpeg 超时（{timeout}秒）") from None

    if result.returncode != 0:
        error_msg = _extract_error(result.stderr)
        raise FFmpegError(
            f"FFmpeg 失败（code {result.returncode}）\n"
            f"命令: {' '.join(cmd)}\n"
            f"错误: {error_msg}"
        )

    # 验证输出
    out_path = Path(output_video)
    if not out_path.exists() or out_path.stat().st_size < 1024:
        raise FFmpegError(f"输出文件无效: {output_video}")

    return end - start


# CLI 包装层（error-design.md: 捕获异常）
def main():
    import sys
    try:
        duration = trim_segment(
            input_video="input.mp4",
            output_video="output.mp4",
            start=10.0,
            end=30.0,
        )
        print(f"成功: 截取 {duration:.2f} 秒")
        sys.exit(0)
    except VideoEditError as e:
        print(f"失败: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
```

## 规范对应检查

| 检查项 | 对应规范 | 位置 |
|--------|---------|------|
| 专用异常类继承链 | `error-design.md` 异常类设计 | L18-21 |
| 内部库函数抛异常 | `error-design.md` CLI vs 内部 | L38 |
| 类型注解 | `python-patterns.md` 类型注解 | L15-16 |
| 路径用 Path | `python-patterns.md` 路径处理 | L42 |
| seek 在 -i 前 | `ffmpeg-conventions.md` seek 位置 | L50 |
| -y 在最前 | `ffmpeg-conventions.md` 参数顺序 | L49 |
| timeout | `ffmpeg-conventions.md` subprocess | L54 |
| returncode 判断成功 | `ffmpeg-conventions.md` 成功判断 | L59 |
| 异常链 from e | `error-design.md` 异常链 | L64 |
| 错误信息含具体值 | `error-design.md` 错误信息质量 | L65-67 |
| 临时文件（trim_segment无需临时文件） | `review-checklist.md` 临时文件 | — |
