# 测试方案文档

## 1. 测试策略

### 1.1 测试原则

- **单元测试** - 每个模块独立测试
- **集成测试** - 模块组合测试
- **端到端测试** - 完整流程测试
- **性能测试** - 处理速度和资源占用
- **边界测试** - 极限情况测试

### 1.2 测试优先级

| 优先级 | 测试类型 | 说明 |
|--------|----------|------|
| P0 | 核心功能 | 静音检测、视频剪辑 |
| P1 | 重要功能 | 场景检测、字幕生成 |
| P2 | 边界情况 | 大文件、格式兼容 |
| P3 | 性能优化 | 处理速度、内存占用 |

---

## 2. 测试环境

### 2.1 硬件要求

| 配置 | 最低要求 | 推荐配置 |
|------|----------|----------|
| CPU | 4核 | 8核以上 |
| 内存 | 8GB | 16GB以上 |
| 磁盘 | 50GB可用空间 | SSD 100GB以上 |
| GPU | 无 | NVIDIA (字幕加速) |

### 2.2 软件要求

- Python 3.8+
- FFmpeg 4.0+
- Windows 10/11 或 macOS 10.15+ 或 Ubuntu 20.04+

---

## 3. 单元测试

### 3.1 分析模块测试

```python
# tests/test_analyzer.py

import pytest
from modules.analyzer import VideoAnalyzer

class TestVideoAnalyzer:
    
    def test_analyze_basic_info(self):
        """测试基础信息提取"""
        analyzer = VideoAnalyzer()
        result = analyzer.analyze("tests/fixtures/test_video.mp4")
        
        assert result.duration > 0
        assert result.resolution[0] > 0
        assert result.resolution[1] > 0
        assert result.fps > 0
    
    def test_detect_silence(self):
        """测试静音检测"""
        analyzer = VideoAnalyzer()
        result = analyzer.analyze("tests/fixtures/silent_video.mp4")
        
        # 测试视频有明确的静音段
        assert len(result.silent_segments) > 0
        assert result.total_silent_duration > 0
    
    def test_silence_threshold(self):
        """测试不同静音阈值"""
        analyzer = VideoAnalyzer()
        
        result_low = analyzer.analyze(
            "tests/fixtures/test_video.mp4",
            silence_threshold=0.01
        )
        result_high = analyzer.analyze(
            "tests/fixtures/test_video.mp4",
            silence_threshold=0.1
        )
        
        # 低阈值应该检测到更多静音
        assert len(result_low.silent_segments) >= len(result_high.silent_segments)
    
    def test_detect_scenes(self):
        """测试场景检测"""
        analyzer = VideoAnalyzer()
        result = analyzer.analyze(
            "tests/fixtures/multi_scene.mp4",
            detect_scenes=True
        )
        
        assert len(result.scene_changes) > 0
    
    def test_invalid_file(self):
        """测试无效文件处理"""
        analyzer = VideoAnalyzer()
        
        with pytest.raises(FileNotFoundError):
            analyzer.analyze("nonexistent.mp4")
```

### 3.2 编辑模块测试

```python
# tests/test_editor.py

import pytest
import os
from modules.editor import VideoEditor

class TestVideoEditor:
    
    def setup_method(self):
        self.test_video = "tests/fixtures/test_video.mp4"
        self.output_dir = "tests/output"
        os.makedirs(self.output_dir, exist_ok=True)
    
    def teardown_method(self):
        # 清理测试输出
        import shutil
        if os.path.exists(self.output_dir):
            shutil.rmtree(self.output_dir)
    
    def test_basic_edit(self):
        """测试基础剪辑"""
        editor = VideoEditor()
        result = editor.edit(
            self.test_video,
            output_path=f"{self.output_dir}/output.mp4"
        )
        
        assert result.success
        assert os.path.exists(result.output_path)
        assert result.edited_duration <= result.original_duration
    
    def test_remove_silence(self):
        """测试静音删除"""
        editor = VideoEditor()
        result = editor.edit(
            "tests/fixtures/video_with_silence.mp4",
            output_path=f"{self.output_dir}/output.mp4",
            remove_silence=True
        )
        
        assert result.success
        assert result.removed_duration > 0
    
    def test_margin_effect(self):
        """测试边缘保留效果"""
        editor = VideoEditor()
        
        result_small = editor.edit(
            self.test_video,
            output_path=f"{self.output_dir}/small_margin.mp4",
            silence_margin=0.1
        )
        result_large = editor.edit(
            self.test_video,
            output_path=f"{self.output_dir}/large_margin.mp4",
            silence_margin=1.0
        )
        
        # 大边缘保留应该产生更长的视频
        assert result_large.edited_duration >= result_small.edited_duration
    
    def test_dry_run(self):
        """测试仅分析模式"""
        editor = VideoEditor()
        result = editor.edit(
            self.test_video,
            dry_run=True
        )
        
        # 不应该生成输出文件
        assert result.output_path is None or not os.path.exists(result.output_path)
```

### 3.3 字幕模块测试

```python
# tests/test_subtitle.py

import pytest
from modules.subtitle import SubtitleGenerator

class TestSubtitleGenerator:
    
    def test_generate_srt(self):
        """测试字幕生成"""
        generator = SubtitleGenerator()
        srt_path = generator.generate(
            "tests/fixtures/video_with_speech.mp4",
            language="zh"
        )
        
        assert os.path.exists(srt_path)
        
        # 验证 SRT 格式
        with open(srt_path, 'r', encoding='utf-8') as f:
            content = f.read()
            assert "-->" in content  # 时间轴格式
    
    def test_embed_subtitle(self):
        """测试字幕嵌入"""
        generator = SubtitleGenerator()
        result = generator.embed(
            "tests/fixtures/test_video.mp4",
            "tests/fixtures/test.srt"
        )
        
        assert os.path.exists(result)
```

---

## 4. 集成测试

### 4.1 完整流程测试

```python
# tests/test_integration.py

import pytest
from ai_video_editor import VideoEditor

class TestIntegration:
    
    def test_full_workflow(self):
        """测试完整工作流程"""
        editor = VideoEditor()
        result = editor.edit(
            "tests/fixtures/integration_test.mp4",
            output_path="tests/output/full_workflow.mp4",
            detect_scenes=True,
            generate_subtitles=True,
            language="zh"
        )
        
        assert result.success
        assert os.path.exists(result.output_path)
        assert result.subtitle_path is not None
        assert os.path.exists(result.subtitle_path)
    
    def test_different_formats(self):
        """测试不同输出格式"""
        editor = VideoEditor()
        
        for fmt in ["mp4", "mov", "avi"]:
            result = editor.edit(
                "tests/fixtures/test_video.mp4",
                output_path=f"tests/output/test.{fmt}",
                output_format=fmt
            )
            assert result.success
            assert result.output_path.endswith(f".{fmt}")
```

---

## 5. 性能测试

### 5.1 处理速度测试

```python
# tests/test_performance.py

import pytest
import time
from ai_video_editor import VideoEditor

class TestPerformance:
    
    def test_processing_time(self):
        """测试处理时间"""
        editor = VideoEditor()
        
        start = time.time()
        result = editor.edit("tests/fixtures/10min_video.mp4")
        elapsed = time.time() - start
        
        # 10分钟视频应该在 5 分钟内处理完
        assert elapsed < 300
        assert result.success
    
    def test_memory_usage(self):
        """测试内存占用"""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB
        
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/large_video.mp4")
        
        peak_memory = process.memory_info().rss / 1024 / 1024
        memory_increase = peak_memory - initial_memory
        
        # 内存增长不应超过 2GB
        assert memory_increase < 2048
```

### 5.2 并发测试

```python
def test_concurrent_processing():
    """测试并发处理"""
    from concurrent.futures import ThreadPoolExecutor
    
    videos = [f"tests/fixtures/video_{i}.mp4" for i in range(4)]
    
    def process(video):
        editor = VideoEditor()
        return editor.edit(video)
    
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(process, videos))
    
    for result in results:
        assert result.success
```

---

## 6. 边界条件测试

### 6.1 极端情况测试

```python
# tests/test_edge_cases.py

class TestEdgeCases:
    
    def test_empty_video(self):
        """测试空视频"""
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/empty.mp4")
        
        # 应该优雅地失败
        assert not result.success
        assert "error" in result.error_message.lower()
    
    def test_very_short_video(self):
        """测试极短视频（<1秒）"""
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/0.5s.mp4")
        
        assert result.success
    
    def test_very_long_video(self):
        """测试超长视频（>2小时）"""
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/3h_video.mp4")
        
        assert result.success
        assert result.processing_time < 1800  # 30分钟内
    
    def test_no_audio_video(self):
        """测试无声视频"""
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/no_audio.mp4")
        
        assert result.success
        assert result.removed_duration == 0  # 无静音可删
    
    def test_corrupted_video(self):
        """测试损坏视频"""
        editor = VideoEditor()
        result = editor.edit("tests/fixtures/corrupted.mp4")
        
        assert not result.success
```

### 6.2 格式兼容性测试

```python
def test_format_compatibility():
    """测试多种视频格式"""
    editor = VideoEditor()
    
    formats = ["mp4", "mov", "avi", "mkv", "webm", "flv"]
    
    for fmt in formats:
        video = f"tests/fixtures/test.{fmt}"
        if os.path.exists(video):
            result = editor.edit(video)
            assert result.success, f"Failed for format: {fmt}"
```

---

## 7. 测试数据准备

### 7.1 测试视频清单

| 文件名 | 时长 | 特点 | 用途 |
|--------|------|------|------|
| test_video.mp4 | 30s | 普通视频 | 基础测试 |
| silent_video.mp4 | 1min | 含明显静音 | 静音检测测试 |
| multi_scene.mp4 | 2min | 多场景切换 | 场景检测测试 |
| video_with_speech.mp4 | 1min | 含清晰人声 | 字幕测试 |
| no_audio.mp4 | 30s | 无音轨 | 边界测试 |
| 10min_video.mp4 | 10min | 中等长度 | 性能测试 |
| large_video.mp4 | 1h | 大文件 | 内存测试 |

### 7.2 生成测试视频

```python
# scripts/generate_test_videos.py

import subprocess

def generate_test_video(output, duration, with_silence=False):
    """生成测试视频"""
    cmd = [
        "ffmpeg", "-f", "lavfi",
        "-i", f"testsrc=duration={duration}:size=1280x720:rate=30",
        "-f", "lavfi",
        "-i", f"sinewave=frequency=1000:duration={duration}",
        "-c:v", "libx264", "-c:a", "aac",
        output
    ]
    subprocess.run(cmd)
```

---

## 8. 测试执行

### 8.1 运行测试

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_analyzer.py

# 运行带标记的测试
pytest -m "not slow" tests/

# 生成覆盖率报告
pytest --cov=modules tests/
```

### 8.2 测试报告

```bash
# 生成 HTML 报告
pytest --html=report.html tests/
```

---

## 9. 持续集成

### 9.1 GitHub Actions 配置

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install FFmpeg
        run: sudo apt install ffmpeg
      
      - name: Install dependencies
        run: pip install -r requirements.txt
      
      - name: Run tests
        run: pytest tests/
```

---

_Last updated: 2026-03-23_
