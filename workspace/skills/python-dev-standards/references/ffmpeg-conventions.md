# FFmpeg Conventions

> 注意：本文档是 FFmpeg 操作知识手册，独立于 Python 语言规范。仅在"调用 FFmpeg"时查阅。

## 参数顺序

```
ffmpeg [全局参数] -i [输入文件] [输出参数] [输出文件]
```

- 全局参数（`-y`、`-loglevel`）放在最前
- `-i` 紧跟输入文件
- 输出参数在输入文件之后
- 输出文件在最后

## seek（-ss）位置

| 位置 | 速度 | 适用场景 |
|------|------|---------|
| `-i` **前** | 快（关键帧 seek） | 截取、预览 |
| `-i` **后** | 慢（逐帧读取） | 需要精确帧级定位 |

## 成功判断

**唯一标准：** `returncode == 0`

FFmpeg 所有输出（正常输出和错误信息）都在 **stderr**，不在 stdout。

## 退出码

| returncode | 含义 | 处理 |
|-----------|------|------|
| 0 | 成功 | 返回成功 |
| 1 | 参数错误 | 输出完整命令和 stderr |
| 255 | 用户中断 | 告知用户中断 |
| 其他 | 未知 | 提取 stderr 最后一行真实错误 |

## 错误信息提取

FFmpeg stderr 结构：元数据 → 进度条 → **错误信息**（末尾）。

```python
def extract_error(stderr: str) -> str:
    """提取 stderr 中最后一个真实错误行（跳过进度条和元数据行）"""
    import re
    lines = [l.strip() for l in stderr.splitlines()]
    errors = [
        l for l in lines
        if l and not re.match(r'^frame=', l) and not re.match(r'^\[', l)
    ]
    return errors[-1] if errors else "unknown"
```

## subprocess 调用规范

FFmpeg 通过 subprocess 调用时，必须：
- 设置 `timeout`（无则禁止执行）
- 用 `returncode == 0` 判断成功（不看输出内容）
- 失败时提取 stderr 中的真实错误（见上方 `extract_error`）

## 常用滤镜

**视频：** `scale=W:H`（缩放）、`trim=start=X:end=Y`（截取，需重新编码）

**音频：** `silencedetect=noise=XdB:d=X`（检测静音）

## 流选择（-map）

`-map 0:v`（选视频）、`-map 0:a`（选音频）、`-vn`（仅视频）、`-an`（仅音频）

## 合并（concat）

```bash
ffmpeg -y -f concat -safe 0 -i filelist.txt -c copy output.mp4
```

文件列表格式：`file 'video1.mp4'\nfile 'video2.mp4'`

## ffprobe（获取元数据）

```bash
# 单字段
ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 input.mp4

# 多字段
ffprobe -v error -show_entries format=duration,size:stream=codec_type,width,height -of default input.mp4
```

## 常见错误

| 错误 | 原因 | 解决 |
|------|------|------|
| `-c copy` 失败 | 编码格式不兼容 | 去掉 `-c copy` 重新编码 |
| 画面异常 | `-ss` 在输入后 | 移到 `-i` 前 |
| 命令挂起 | 无 timeout | 必须设置 timeout |
