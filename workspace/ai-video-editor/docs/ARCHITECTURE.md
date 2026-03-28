# AI 视频剪辑器 - 架构文档

## 1. 当前架构

### 1.1 架构总览

```
用户 / AI
    ↓
edit_video.py              # 结构化 CLI 入口
    ↓
Executor                   # 执行引擎（命令路由器）
    ↓
Analyzer                   # 分析层（共用）
    ├── audio.py           # 音频处理
    ├── scene.py           # 场景检测
    ├── content.py         # 内容分析
    └── subtitle.py        # 字幕生成
    ↓
FFmpeg                    # 实际视频处理
```

### 1.2 模块职责

| 模块 | 文件 | 职责 |
|------|------|------|
| `edit_video.py` | 项目根目录 | AI 调用入口；验证参数；路由到 Executor |
| `Executor` | `modules/executor.py` | 将结构化指令转为 FFmpeg 命令；处理重试 |
| `Analyzer` | `modules/analyzer.py` | 视频/音频分析；供 V1–V4 共用 |
| `Validator` | `modules/validator.py` | 执行后验证输出文件 |

### 1.3 当前 Executor 问题

**Executor 本质是一个"命令路由器"**：
- 每种操作独立触发，互不关联
- 操作之间不传上下文
- 不支持链式执行

---

## 2. 目标架构

### 2.1 分层架构

```
AI Agent
    ↓
【分析层】Analyzer        ← 已有，不用改
    ↓
【决策层】Planner        ← 新增：AI 决策
    ↓
【规划层】Pipeline        ← 新增：EditPlan 执行计划
    ↓
【执行层】Executor        ← 重构：从路由器变成 Pipeline 引擎
    ↓
FFmpeg
```

### 2.2 数据流

```
原始视频
    ↓
【分析层】分析场景 → 评估内容密度 → 检测静音
    ↓
【决策层】生成剪辑决策
    ↓
【规划层】转成 EditPlan
    ↓
【执行层】按 Pipeline 执行
    ↓
最终视频
```

---

## 3. V1-V4 功能概览

### V1: 基础自动剪辑 ✅ 完成

| 操作 | 说明 |
|------|------|
| `trim_start` | 删除视频开头 |
| `trim_end` | 删除视频结尾 |
| `trim_range` | 保留单段时间范围 |
| `trim_range` (多段) | 保留多段并自动合并 |
| `concat` | 合并多个视频文件 |
| `convert` | 改变分辨率 |
| `remove_silence` | 检测并删除静音段 |
| `remove_static` | 检测并删除静止帧段 |

### V2: 场景分割 ✅ 完成

| 操作 | 说明 |
|------|------|
| `detect_scenes` | 检测场景切换点 |
| `split_by_scenes` | 按场景切割为多个文件 |
| `extract_scene_thumbnails` | 为每个场景提取缩略图 |
| `analyze_content_density` | 场景+音频联合分析 |
| `select_scenes` | 根据意图推荐场景 |

### V3: 自动字幕 ✅ 完成

| 操作 | 说明 |
|------|------|
| `transcribe` | Whisper 语音识别 |
| `generate_srt` | 生成 SRT 字幕文件 |
| `burn_subtitle` | FFmpeg 字幕烧录 |
| `auto_subtitle` | 一键字幕 |

### V4: 智能剪辑 ⏳ 待开发

| 功能 | 说明 |
|------|------|
| AI 决策层 | 从分析结果生成剪辑决策 |
| Pipeline 执行引擎 | 链式执行、回滚、Dry-run |
| 自动选段 | 根据内容密度自动选择保留片段 |
| 转场效果 | 添加平滑转场 |
| 短视频合成 | 自动生成 60 秒短视频 |

---

## 4. V4 设计：Pipeline 执行引擎

### 4.1 EditPlan 数据结构

```python
@dataclass
class EditStep:
    op: str                     # 操作类型
    params: Dict[str, Any]     # 参数
    input_file: Optional[str]   # 输入文件（None = 用上一步输出）
    output_file: Optional[str]  # 输出文件（None = 自动生成）

@dataclass
class EditPlan:
    steps: List[EditStep]
    metadata: Dict[str, Any]   # 分析结果、决策理由等
```

### 4.2 Pipeline 执行引擎

```python
class PipelineExecutor:
    """Pipeline 执行引擎"""
    
    def execute(self, plan: EditPlan, dry_run: bool = False) -> ExecutionResult:
        """执行编辑计划"""
        pass
    
    def get_intermediate_results(self) -> Dict:
        """获取中间结果（给 AI 预览）"""
        pass
    
    def rollback(self, step_index: int):
        """回滚到某一步"""
        pass
```

### 4.3 示例 EditPlan

```python
plan = EditPlan([
    {"op": "trim_range", "start": 5.2, "end": 30.1},
    {"op": "trim_range", "start": 35.0, "end": 120.0},
    {"op": "concat", "segments": "#auto"},
    {"op": "burn_subtitle", "srtfile": "auto.srt"},
])
```

---

## 5. 关键设计决策

### 5.1 为什么用 FFmpeg？

视频处理行业标准，功能全面，性能优秀。

### 5.2 为什么用 OpenCV 做静止帧检测？

FFmpeg 的 blackframe 滤镜在 FFmpeg 7.x 行为不稳定。
OpenCV 可以精确控制采样间隔和像素差异阈值。

### 5.3 为什么 Analyzer 是独立的共用模块？

V2/V3/V4 所有阶段都需要分析，拆分避免重复代码。

### 5.4 为什么 Windows 路径要用正斜杠传给 FFmpeg？

FFmpeg 在 Windows 上接受正斜杠 `/`，但反斜杠 `\` 需要转义。
通过 `_normalize_path()` 统一处理。

---

## 6. 待开发任务

### 6.1 Pipeline 重构

- [ ] 设计 EditPlan 数据结构
- [ ] 创建 PipelineExecutor 类
- [ ] 支持链式执行
- [ ] 支持 Dry-run
- [ ] 支持回滚机制

### 6.2 决策层设计

- [ ] 设计决策算法（规则引擎 / LLM）
- [ ] 生成剪辑决策
- [ ] 与分析层集成

---

_Last updated: 2026-03-28_
