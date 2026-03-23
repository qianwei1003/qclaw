# 技术架构文档

## 1. 系统概述

AI 视频剪辑器是一个模块化的视频处理系统，通过组合开源工具实现自动化剪辑。

### 1.1 设计原则

- **模块化** - 各功能独立，可单独使用
- **可扩展** - 方便添加新功能
- **可配置** - 用户可自定义参数
- **容错性** - 优雅处理各种异常

---

## 2. 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                        用户界面层                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   CLI 接口    │  │  Python API  │  │  配置文件     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        核心控制层                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                    main.py (主控制器)                 │  │
│  │  - 参数解析                                           │  │
│  │  - 流程调度                                           │  │
│  │  - 错误处理                                           │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        功能模块层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Analyzer │  │  Editor  │  │ Subtitle │  │ Exporter │   │
│  │ 视频分析  │  │ 剪辑处理  │  │ 字幕生成  │  │ 输出渲染  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                        工具依赖层                            │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │auto-editor│  │PyScene   │  │ Whisper  │  │ FFmpeg   │   │
│  │ 静音检测  │  │Detect    │  │ 语音识别  │  │ 视频处理  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. 模块详解

### 3.1 主控制器 (main.py)

**职责：**
- 解析命令行参数
- 加载配置文件
- 协调各模块执行顺序
- 处理全局异常
- 输出日志和进度

**输入：**
- 命令行参数
- 配置文件 (config.yaml)

**输出：**
- 处理后的视频文件
- 日志文件
- 状态报告

---

### 3.2 分析模块 (modules/analyzer.py)

**职责：**
- 分析视频基本信息（时长、分辨率、帧率）
- 检测静音片段
- 检测静止画面
- 检测场景变化

**依赖：**
- auto-editor (静音检测)
- PySceneDetect (场景检测)

**接口：**
```python
class VideoAnalyzer:
    def analyze(self, video_path: str) -> AnalysisResult:
        """
        分析视频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            AnalysisResult: 包含静音片段、场景变化等信息
        """
        pass
```

**输出数据结构：**
```python
@dataclass
class AnalysisResult:
    duration: float                    # 视频总时长（秒）
    resolution: Tuple[int, int]        # 分辨率 (宽, 高)
    fps: float                         # 帧率
    silent_segments: List[Segment]     # 静音片段列表
    static_segments: List[Segment]     # 静止片段列表
    scene_changes: List[float]         # 场景变化时间点

@dataclass
class Segment:
    start: float   # 开始时间（秒）
    end: float     # 结束时间（秒）
    type: str      # 类型：silent / static / scene
```

---

### 3.3 编辑模块 (modules/editor.py)

**职责：**
- 根据分析结果生成剪辑决策
- 执行剪辑操作
- 添加转场效果

**依赖：**
- FFmpeg
- MoviePy

**接口：**
```python
class VideoEditor:
    def edit(
        self, 
        video_path: str, 
        analysis: AnalysisResult,
        config: EditConfig
    ) -> str:
        """
        执行剪辑
        
        Args:
            video_path: 原视频路径
            analysis: 分析结果
            config: 剪辑配置
            
        Returns:
            str: 剪辑后的视频路径
        """
        pass
```

**配置参数：**
```python
@dataclass
class EditConfig:
    silence_threshold: float = 0.02      # 静音阈值
    silence_margin: float = 0.2          # 静音边缘保留（秒）
    remove_static: bool = True           # 是否删除静止片段
    add_transitions: bool = False        # 是否添加转场
    transition_duration: float = 0.5     # 转场时长（秒）
```

---

### 3.4 字幕模块 (modules/subtitle.py)

**职责：**
- 提取音频
- 语音识别
- 生成字幕文件
- 将字幕嵌入视频

**依赖：**
- Whisper (语音识别)
- FFmpeg (音频提取、字幕嵌入)

**接口：**
```python
class SubtitleGenerator:
    def generate(
        self, 
        video_path: str,
        language: str = "zh"
    ) -> str:
        """
        生成字幕
        
        Args:
            video_path: 视频路径
            language: 语言代码
            
        Returns:
            str: 字幕文件路径 (SRT格式)
        """
        pass
    
    def embed(
        self, 
        video_path: str, 
        subtitle_path: str
    ) -> str:
        """
        将字幕嵌入视频
        
        Args:
            video_path: 视频路径
            subtitle_path: 字幕路径
            
        Returns:
            str: 嵌入字幕后的视频路径
        """
        pass
```

---

### 3.5 输出模块 (modules/exporter.py)

**职责：**
- 渲染最终视频
- 生成不同格式输出
- 生成报告

**依赖：**
- FFmpeg

**接口：**
```python
class VideoExporter:
    def export(
        self,
        video_path: str,
        output_config: OutputConfig
    ) -> ExportResult:
        """
        导出视频
        
        Args:
            video_path: 输入视频路径
            output_config: 输出配置
            
        Returns:
            ExportResult: 导出结果
        """
        pass
```

---

## 4. 数据流设计

### 4.1 主流程数据流

```
输入视频 (MP4/MOV/AVI)
       │
       ▼
┌──────────────┐
│   Analyzer   │──────► AnalysisResult
└──────────────┘              │
                              ▼
┌──────────────┐        ┌──────────────┐
│   Editor     │◄───────│ 剪辑决策生成  │
└──────────────┘        └──────────────┘
       │
       ▼
 剪辑后的视频
       │
       ▼
┌──────────────┐
│   Subtitle   │──────► 带字幕视频
└──────────────┘
       │
       ▼
┌──────────────┐
│   Exporter   │──────► 最终输出
└──────────────┘
```

### 4.2 中间文件管理

```
工作目录结构：
temp/
├── audio.wav          # 提取的音频
├── analysis.json      # 分析结果
├── segments/          # 分割的片段
│   ├── segment_001.mp4
│   ├── segment_002.mp4
│   └── ...
├── subtitles.srt      # 字幕文件
└── output.mp4         # 最终输出
```

---

## 5. 技术选型理由

| 工具 | 选型理由 |
|------|----------|
| auto-editor | 专为自动剪辑设计，成熟稳定，社区活跃 |
| PySceneDetect | 场景检测准确率高，支持多种检测算法 |
| Whisper | 开源语音识别，支持多语言，准确率高 |
| FFmpeg | 行业标准，功能全面，性能优秀 |
| MoviePy | Python 原生，易于集成，文档完善 |

---

## 6. 性能考虑

### 6.1 大文件处理

- **分块处理** - 大视频分块加载，避免内存溢出
- **临时文件清理** - 处理完成后自动清理中间文件
- **进度显示** - 实时显示处理进度

### 6.2 并行处理

- 音频提取和视频分析可并行
- 多个片段可并行处理

---

## 7. 扩展性设计

### 7.1 插件系统

```python
class PluginBase:
    """插件基类"""
    def pre_process(self, video_path: str) -> str:
        """预处理钩子"""
        pass
    
    def post_process(self, video_path: str) -> str:
        """后处理钩子"""
        pass
```

### 7.2 自定义分析器

```python
class CustomAnalyzer(AnalyzerBase):
    def analyze(self, video_path: str) -> AnalysisResult:
        # 自定义分析逻辑
        pass
```

---

## 8. 安全性考虑

- 输入验证：检查文件格式、大小
- 路径安全：防止路径穿越攻击
- 资源限制：限制最大处理时长、最大文件大小

---

_Last updated: 2026-03-23_
