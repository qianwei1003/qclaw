# API 设计文档

## 1. 命令行接口 (CLI)

### 1.1 基础命令

```bash
python main.py <input_video> [options]
```

### 1.2 参数说明

| 参数 | 短参数 | 类型 | 默认值 | 说明 |
|------|--------|------|--------|------|
| `--output` | `-o` | string | `./output/` | 输出目录 |
| `--silence-threshold` | `-s` | float | 0.02 | 静音检测阈值 (0.0-1.0) |
| `--silence-margin` | `-m` | float | 0.2 | 静音边缘保留时长（秒） |
| `--remove-static` | | bool | True | 是否删除静止片段 |
| `--detect-scenes` | | bool | False | 是否检测场景变化 |
| `--generate-subtitles` | | bool | False | 是否生成字幕 |
| `--language` | `-l` | string | `zh` | 字幕语言 |
| `--format` | `-f` | string | `mp4` | 输出格式 |
| `--quality` | `-q` | string | `high` | 输出质量 (low/medium/high) |
| `--config` | `-c` | string | `config.yaml` | 配置文件路径 |
| `--verbose` | `-v` | bool | False | 详细日志输出 |
| `--dry-run` | | bool | False | 仅分析不执行 |
| `--help` | `-h` | | | 显示帮助信息 |

### 1.3 使用示例

```bash
# 基础用法：自动删除静音
python main.py video.mp4

# 指定输出路径
python main.py video.mp4 -o ./edited/

# 调整静音检测灵敏度
python main.py video.mp4 --silence-threshold 0.01

# 完整功能：场景检测 + 字幕生成
python main.py video.mp4 --detect-scenes --generate-subtitles --language zh

# 使用配置文件
python main.py video.mp4 -c my_config.yaml

# 仅分析不执行
python main.py video.mp4 --dry-run
```

---

## 2. Python API

### 2.1 快速开始

```python
from ai_video_editor import VideoEditor

# 创建编辑器实例
editor = VideoEditor()

# 基础剪辑
result = editor.edit("input.mp4")

# 带配置的剪辑
result = editor.edit(
    "input.mp4",
    silence_threshold=0.02,
    silence_margin=0.2,
    output_path="output.mp4"
)

# 完整功能
result = editor.edit(
    "input.mp4",
    detect_scenes=True,
    generate_subtitles=True,
    language="zh"
)
```

### 2.2 核心类定义

#### VideoEditor 类

```python
class VideoEditor:
    """视频编辑器主类"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化编辑器
        
        Args:
            config_path: 配置文件路径，可选
        """
        pass
    
    def edit(
        self,
        input_path: str,
        output_path: Optional[str] = None,
        silence_threshold: float = 0.02,
        silence_margin: float = 0.2,
        remove_static: bool = True,
        detect_scenes: bool = False,
        generate_subtitles: bool = False,
        language: str = "zh",
        output_format: str = "mp4",
        quality: str = "high"
    ) -> EditResult:
        """
        执行视频编辑
        
        Args:
            input_path: 输入视频路径
            output_path: 输出路径，可选，默认自动生成
            silence_threshold: 静音阈值
            silence_margin: 静音边缘保留
            remove_static: 是否删除静止片段
            detect_scenes: 是否检测场景
            generate_subtitles: 是否生成字幕
            language: 字幕语言
            output_format: 输出格式
            quality: 输出质量
            
        Returns:
            EditResult: 编辑结果
            
        Raises:
            FileNotFoundError: 输入文件不存在
            InvalidVideoError: 视频格式无效
            ProcessingError: 处理过程出错
        """
        pass
    
    def analyze(self, input_path: str) -> AnalysisResult:
        """
        仅分析视频，不执行编辑
        
        Args:
            input_path: 输入视频路径
            
        Returns:
            AnalysisResult: 分析结果
        """
        pass
```

#### 返回类型定义

```python
from dataclasses import dataclass
from typing import List, Tuple

@dataclass
class EditResult:
    """编辑结果"""
    success: bool                          # 是否成功
    output_path: str                       # 输出文件路径
    original_duration: float               # 原视频时长（秒）
    edited_duration: float                 # 编辑后时长（秒）
    removed_segments: int                  # 删除的片段数
    removed_duration: float                # 删除的总时长（秒）
    subtitle_path: Optional[str]           # 字幕文件路径（如果生成）
    processing_time: float                 # 处理耗时（秒）
    error_message: Optional[str]           # 错误信息（如果失败）

@dataclass
class AnalysisResult:
    """分析结果"""
    duration: float                        # 视频总时长（秒）
    resolution: Tuple[int, int]            # 分辨率 (宽, 高)
    fps: float                             # 帧率
    bitrate: int                           # 比特率
    codec: str                             # 编码格式
    silent_segments: List[Segment]         # 静音片段
    static_segments: List[Segment]         # 静止片段
    scene_changes: List[float]             # 场景变化时间点
    
    @property
    def total_silent_duration(self) -> float:
        """总静音时长"""
        return sum(s.duration for s in self.silent_segments)

@dataclass
class Segment:
    """时间片段"""
    start: float                           # 开始时间（秒）
    end: float                             # 结束时间（秒）
    type: str                              # 类型：silent / static / scene
    
    @property
    def duration(self) -> float:
        """片段时长"""
        return self.end - self.start
```

---

## 3. 配置文件格式

### 3.1 config.yaml 结构

```yaml
# 分析配置
analysis:
  silence_threshold: 0.02        # 静音阈值 (0.0-1.0)
  silence_margin: 0.2            # 静音边缘保留（秒）
  static_threshold: 0.01         # 静止画面阈值
  scene_threshold: 27.0          # 场景变化阈值

# 编辑配置
editing:
  remove_silence: true           # 是否删除静音
  remove_static: true             # 是否删除静止画面
  detect_scenes: false            # 是否检测场景
  add_transitions: false          # 是否添加转场
  transition_duration: 0.5       # 转场时长（秒）

# 字幕配置
subtitle:
  enabled: false                 # 是否启用字幕
  language: "zh"                 # 语言
  model: "base"                  # Whisper 模型大小
  font: "Arial"                  # 字体
  font_size: 24                  # 字号
  position: "bottom"             # 位置：top/bottom

# 输出配置
output:
  directory: "./output/"         # 输出目录
  format: "mp4"                  # 格式：mp4/mov/avi
  quality: "high"                # 质量：low/medium/high
  codec: "h264"                  # 编码器
  keep_temp: false               # 是否保留临时文件

# 日志配置
logging:
  level: "INFO"                 # 日志级别
  file: "./logs/editor.log"      # 日志文件路径
  verbose: false                 # 详细输出

# 性能配置
performance:
  max_workers: 4                 # 最大并行数
  chunk_duration: 60             # 分块时长（秒）
  max_memory_gb: 4               # 最大内存使用（GB）
```

---

## 4. 错误码定义

| 错误码 | 名称 | 说明 | 解决方案 |
|--------|------|------|----------|
| 1001 | `FILE_NOT_FOUND` | 输入文件不存在 | 检查文件路径 |
| 1002 | `INVALID_FORMAT` | 视频格式不支持 | 转换为 MP4/MOV |
| 1003 | `FILE_TOO_LARGE` | 文件超过大小限制 | 分割后处理 |
| 1004 | `FILE_CORRUPTED` | 文件损坏 | 修复或更换文件 |
| 2001 | `FFMPEG_ERROR` | FFmpeg 执行失败 | 检查 FFmpeg 安装 |
| 2002 | `ANALYSIS_FAILED` | 视频分析失败 | 检查视频是否有效 |
| 2003 | `EDIT_FAILED` | 编辑操作失败 | 查看详细日志 |
| 3001 | `OUT_OF_MEMORY` | 内存不足 | 减小 chunk_duration |
| 3002 | `DISK_FULL` | 磁盘空间不足 | 清理磁盘空间 |
| 4001 | `CONFIG_ERROR` | 配置文件错误 | 检查 YAML 语法 |

---

## 5. 日志格式

### 5.1 标准日志格式

```
[2024-01-15 10:30:45] [INFO] [main] 开始处理视频: input.mp4
[2024-01-15 10:30:46] [INFO] [analyzer] 分析视频信息...
[2024-01-15 10:30:48] [INFO] [analyzer] 检测到 15 个静音片段，总时长 45.2 秒
[2024-01-15 10:30:49] [INFO] [editor] 开始剪辑...
[2024-01-15 10:31:20] [INFO] [editor] 剪辑完成，删除了 15 个片段
[2024-01-15 10:31:21] [INFO] [exporter] 输出视频: output.mp4
[2024-01-15 10:31:22] [INFO] [main] 处理完成，耗时 37 秒
```

### 5.2 JSON 日志格式（可选）

```json
{
  "timestamp": "2024-01-15T10:30:45",
  "level": "INFO",
  "module": "analyzer",
  "message": "检测到 15 个静音片段",
  "data": {
    "silent_count": 15,
    "total_duration": 45.2
  }
}
```

---

## 6. 进度回调

### 6.1 进度事件

```python
class ProgressEvent:
    """进度事件"""
    stage: str           # 当前阶段：analyzing/editing/exporting
    progress: float      # 进度 0.0-1.0
    message: str         # 进度消息
    elapsed: float       # 已用时间（秒）
    estimated_remaining: float  # 预计剩余时间（秒）
```

### 6.2 使用回调

```python
def on_progress(event: ProgressEvent):
    print(f"[{event.stage}] {event.progress*100:.1f}% - {event.message}")

editor = VideoEditor()
result = editor.edit("input.mp4", progress_callback=on_progress)
```

---

_Last updated: 2026-03-23_
