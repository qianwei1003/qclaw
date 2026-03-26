# V3: 自动字幕 - 设计文档

**版本：** 1.0  
**日期：** 2026-03-27  
**状态：** 设计中

---

## 1. 开发理由

### 用户痛点
- 手动添加字幕费时费力
- 专业字幕软件操作复杂
- 外包字幕成本高

### 解决方案
- AI 自动识别语音生成字幕
- 一键生成 SRT 文件
- 可选直接嵌入视频

### 核心价值
| 用户输入 | AI 输出 |
|---------|---------|
| "给这个视频加字幕" | 带字幕的新视频 + SRT 文件 |
| "导出字幕文件" | SRT 文件（可编辑） |

---

## 2. 功能设计

### 2.1 整体流程

```
视频输入
    ↓
【Step 1】提取音频
    ↓
【Step 2】Whisper 语音识别
    ↓
【Step 3】生成 SRT 字幕
    ↓
【Step 4】（可选）嵌入视频
    ↓
输出：SRT 文件 + 带字幕视频
```

### 2.2 新增功能

| 功能 | 说明 | 输入 | 输出 |
|------|------|------|------|
| `transcribe` | 语音识别 | video | 带时间轴的文字列表 |
| `generate_srt` | 生成 SRT | transcription | SRT 文件 |
| `burn_subtitle` | 字幕嵌入 | video + srt | 带字幕视频 |
| `auto_subtitle` | 一键字幕 | video | SRT + 视频 |

---

## 3. 实现方案

### 3.1 依赖安装

```bash
pip install openai-whisper
```

### 3.2 新增方法：Analyzer.transcribe()

```python
def transcribe(
    self,
    input_video: str,
    language: str = "zh",
    model: str = "base",
) -> list[dict]:
    """
    语音识别，返回带时间轴的文字
    
    Args:
        input_video: 输入视频路径
        language: 语言代码（zh=中文，en=英文）
        model: Whisper 模型（tiny/base/small/medium/large）
        
    Returns:
        [
            {
                "start": 0.0,      # 开始时间（秒）
                "end": 3.5,        # 结束时间（秒）
                "text": "大家好",   # 识别文字
            },
            ...
        ]
    """
```

### 3.3 新增方法：generate_srt()

```python
def generate_srt(
    self,
    transcription: list[dict],
    output_path: str,
) -> str:
    """
    生成 SRT 格式字幕文件
    
    Args:
        transcription: transcribe() 的输出
        output_path: SRT 文件输出路径
        
    Returns:
        SRT 文件路径
    """
```

**SRT 格式示例：**
```
1
00:00:00,000 --> 00:00:03,500
大家好，欢迎来到本期视频

2
00:00:03,500 --> 00:00:07,200
今天我们要讲的是...
```

### 3.4 新增方法：burn_subtitle()

```python
def burn_subtitle(
    self,
    input_video: str,
    srt_file: str,
    output_video: str,
    style_config: dict = None,
) -> bool:
    """
    用 FFmpeg 把字幕烧录到视频
    
    Args:
        input_video: 输入视频
        srt_file: SRT 字幕文件
        output_video: 输出视频路径
        style_config: 字幕样式配置
        {
            "font": "微软雅黑",
            "size": 24,
            "color": "white",
            "position": "bottom",  # bottom/top/center
            "background": false,
        }
        
    Returns:
        True 成功
    """
```

### 3.5 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `language` | str | "zh" | 语言代码 |
| `model` | str | "base" | Whisper 模型：tiny/base/small/medium/large |
| `font` | str | "微软雅黑" | 字体名称 |
| `size` | int | 24 | 字体大小（1080p视频推荐） |
| `color` | str | "white" | 字体颜色：white/yellow/red等 |
| `position` | str | "bottom" | 位置：bottom/top/center |
| `background` | bool | false | 是否添加背景色块 |
| `max_line_length` | int | 20 | 每行最大字数，超过自动换行 |
| `min_duration` | float | 1.0 | 最短显示时长（秒） |
| `max_duration` | float | 7.0 | 最长显示时长（秒） |

---

## 4. API 设计

### 4.1 transcribe 语音识别

```bash
python edit_video.py --operation transcribe --input video.mp4 --params '{"language": "zh", "model": "base"}'
```

**返回：**
```json
{
  "success": true,
  "message": "Transcription complete",
  "data": {
    "segments": [
      {"start": 0.0, "end": 3.5, "text": "大家好"},
      {"start": 3.5, "end": 7.2, "text": "欢迎来到本期视频"}
    ],
    "language": "zh",
    "duration": 195.5
  }
}
```

### 4.2 generate_srt 生成字幕文件

```bash
# 自动生成文件名：video.mp4 → video.srt
python edit_video.py --operation generate_srt --input video.mp4

# 或指定输出文件名
python edit_video.py --operation generate_srt --input video.mp4 --output mysubtitle.srt
```

**返回：**
```json
{
  "success": true,
  "message": "SRT file generated",
  "data": {
    "srt_file": "video.srt",
    "segment_count": 45
  }
}
```

### 4.3 burn_subtitle 字幕嵌入

```bash
# 自动生成输出文件名：video.mp4 → video_subtitled.mp4
python edit_video.py --operation burn_subtitle --input video.mp4 --params '{"srt_file": "video.srt"}'

# 或指定输出文件名
python edit_video.py --operation burn_subtitle --input video.mp4 --output final.mp4 --params '{"srt_file": "video.srt"}'
```

**返回：**
```json
{
  "success": true,
  "message": "Subtitle burned",
  "data": {
    "output_video": "video_subtitled.mp4",
    "style": {...}
  }
}
```

### 4.4 auto_subtitle 一键字幕

```bash
python edit_video.py --operation auto_subtitle --input video.mp4 --output video_subtitled.mp4
```

**返回：**
```json
{
  "success": true,
  "message": "Auto subtitle complete",
  "data": {
    "srt_file": "video.srt",
    "output_video": "video_subtitled.mp4"
  }
}
```

---

## 5. 配置文件

```yaml
# config.yaml 新增
subtitle:
  # 语音识别
  language: "zh"
  model: "base"           # tiny/base/small/medium/large（越大越准越慢）
  
  # 字幕样式
  font: "微软雅黑"
  size: 24
  color: "white"
  position: "bottom"      # bottom/top/center
  background: false
  
  # 时间轴
  max_line_length: 20     # 每行最大字数
  min_duration: 1.0       # 最短显示时长（秒）
  max_duration: 7.0       # 最长显示时长（秒）
```

---

## 6. 后续优化

**短期（V3.1）：**
- 多语言支持（自动检测语言）
- 字幕样式预设（电影风格、综艺风格等）
- 字幕校对界面

**中期（V3.2）：**
- 说话人识别（区分不同人）
- 关键词高亮
- 智能断句优化

**长期（V3.3）：**
- 实时字幕（直播场景）
- 翻译字幕（中英双语）
- AI 字幕润色

---

## 7. 开发清单

| 任务 | 文件 | 预计时间 |
|------|------|---------|
| 安装 Whisper | - | 10 分钟 |
| 实现 transcribe() | modules/analyzer.py | 1 小时 |
| 实现 generate_srt() | modules/analyzer.py | 30 分钟 |
| 实现 burn_subtitle() | modules/executor.py | 1 小时 |
| 更新 edit_video.py | edit_video.py | 30 分钟 |
| 更新 config.yaml | config.yaml | 15 分钟 |
| 测试 | tests/ | 30 分钟 |
| **总计** | | **4 小时** |

---

## 8. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| Whisper 安装失败 | 低 | 高 | 提供安装脚本，备选方案 |
| 识别准确率低 | 中 | 中 | 使用更大的模型，后期校对 |
| 中文字体显示问题 | 中 | 中 | 指定常见字体，提供字体检测 |
| 长视频处理慢 | 高 | 低 | 分段处理，进度提示 |

---

**确认后开始开发？**
