# 进度

## 当前状态
V1 和 V2 Step 1-5 已完成。下一步：V2 Step 6（AI 辅助场景选择）。

## 已完成

- `trim_start` — 删除视频开头
- `trim_end` — 删除视频结尾
- `trim_range` — 保留单段时间范围
- `trim_range` 多段 — 保留多段并自动合并
- `concat` — 合并多个视频文件
- `convert` — 改变分辨率
- `remove_silence` — 检测并删除静音段（兼容 FFmpeg 7.x）
- `remove_static` — 检测并删除静止帧段（OpenCV 帧差分析）
- `info` — 获取视频元数据
- `detect_scenes` — 检测场景切换点（OpenCV 帧差分析）
- `split_by_scenes` — 按场景切割为多个文件
- `extract_scene_thumbnails` — 为每个场景提取缩略图
- `analyze_content` — 场景+音频联合分析，标记"有内容"场景（V2 Step 5）
- `edit_video.py` — AI 可调用的结构化 CLI，覆盖以上所有操作
- `Analyzer` 模块 — `extract_audio`、`detect_scenes`、`extract_thumbnail`、`analyze_audio_energy`、`detect_static_segments`、`extract_scene_thumbnails`、`analyze_content_density`
- `Validator` — 每次操作后验证输出文件
- `extract_audio` 无音频视频优雅降级（返回空路径，analyze_audio_energy 生成零能量窗口）

## 进行中
- V2 Step 6：AI 辅助场景选择（设计文档：`docs/V2_STEP6_DESIGN.md`）

### V2 Step 6 设计方案

#### 1. 开发理由

**核心问题：**

**问题一：AI 如何判断这是精彩场景？**
- 音频能量高 = 精彩？（不一定，可能是噪音）
- 画面变化大 = 精彩？（不一定，可能是抖动）
- 需要综合判断：音频 + 画面 + 场景类型

**问题二：哪个时间点可以剪辑？**
- 不能在说话中间剪（会切断句子）
- 不能在动作中间剪（会不连贯）
- 最佳剪辑点：场景切换处、静音处、动作停顿处

**问题三：拼接后有没有问题？**
- 两个场景拼接，画面是否跳跃？
- 音频是否突兀？
- 需要检测"剪辑友好度"

**解决方案：**

| 问题 | 解决方案 | 实现方式 |
|------|---------|---------|
| 判断精彩 | 多维度评分 | audio_score + visual_score + 场景类型权重 |
| 剪辑点选择 | 检测安全剪辑点 | 检测静音点、场景切换点、动作停顿点 |
| 拼接检测 | 剪辑友好度评分 | 分析相邻场景的画面相似度、音频连续性 |

**核心价值：**
- AI 不仅推荐场景，还告诉用户"为什么精彩"
- AI 推荐安全剪辑点，避免剪坏
- AI 检测拼接问题，提前预警

#### 2. 功能设计

**核心理念：动态评分，因视频类型而异**

不同类型的视频，"精彩"的标准完全不同：
- 访谈节目：精彩 = 有深度的对话、激烈的辩论
- 体育比赛：精彩 = 进球、高潮时刻
- 电影：精彩 = 情节转折、高潮戏
- 搞笑视频：精彩 = 笑点密集
- 教程视频：精彩 = 干货集中

---

### 2.1 新增：视频类型识别

```python
def detect_video_type(input_video) -> str:
    """
    自动识别视频类型
    
    返回：
    - "interview"    # 访谈
    - "sports"       # 体育
    - "movie"        # 电影/剧
    - "funny"        # 搞笑
    - "tutorial"     # 教程
    - "speech"       # 演讲
    - "vlog"         # 日常/Vlog
    - "news"         # 新闻
    - "unknown"      # 未知
    """
```

**识别依据：**
| 指标 | 判断逻辑 |
|------|---------|
| 场景变化频率 | 高=电影/Vlog，低=访谈/演讲 |
| 人脸数量 | 多人=访谈/新闻，单人=演讲/Vlog |
| 音频特征 | 说话密集=访谈/教程，间歇=体育 |
| 字幕关键词 | "进球"、"哈哈"、"干货" |

---

### 2.2 动态评分系统

根据视频类型，使用不同的评分权重：

```python
SCORING_PROFILES = {
    "interview": {      # 访谈
        "audio_energy": 0.3,      # 音频能量
        "speech_density": 0.4,    # 说话密度（新指标）
        "face_change": 0.2,       # 人脸切换
        "scene_change": 0.1,      # 场景变化
    },
    "sports": {         # 体育
        "audio_energy": 0.3,      # 观众欢呼
        "visual_intensity": 0.5,  # 画面激烈程度（新指标）
        "scene_change": 0.2,      # 镜头切换
    },
    "movie": {          # 电影
        "audio_energy": 0.2,
        "visual_intensity": 0.3,
        "scene_change": 0.3,      # 镜头切换
        "emotion_score": 0.2,     # 情感强度（新指标）
    },
    "funny": {          # 搞笑
        "audio_energy": 0.4,      # 笑声
        "laugh_detect": 0.4,      # 笑声检测（新指标）
        "scene_change": 0.2,
    },
    "tutorial": {       # 教程
        "speech_clarity": 0.4,    # 说话清晰度（新指标）
        "text_density": 0.3,      # 字幕密度（新指标）
        "face_presence": 0.3,     # 人脸出现
    },
    "speech": {         # 演讲
        "audio_energy": 0.3,
        "speech_clarity": 0.4,    # 说话清晰度
        "face_presence": 0.3,
    },
    "vlog": {           # Vlog
        "scene_change": 0.4,
        "visual_intensity": 0.3,
        "audio_energy": 0.3,
    },
}
```

---

### 2.3 新增指标

| 指标 | 说明 | 实现方式 |
|------|------|---------|
| `speech_density` | 说话密度 | 音频能量 + 静音段占比 |
| `visual_intensity` | 画面激烈程度 | 帧差变化率 |
| `emotion_score` | 情感强度 | 音频频率分析（高音=激动） |
| `laugh_detect` | 笑声检测 | 音频特征识别 |
| `speech_clarity` | 说话清晰度 | 音频能量 + 频率分析 |
| `text_density` | 字幕密度 | 需要OCR或字幕检测 |
| `face_presence` | 人脸出现 | OpenCV人脸检测 |
| `face_change` | 人脸切换 | 连续帧人脸变化 |

---

### 2.4 整体流程

```
视频输入
    ↓
【Step 1】识别视频类型
    ↓
【Step 2】选择对应评分规则
    ↓
【Step 3】计算各项指标
    ↓
【Step 4】加权评分
    ↓
【Step 5】输出精彩片段 + 理由
```

---

### 2.5 示例输出

**访谈节目：**
```
视频类型：访谈
精彩片段推荐：
1. 5:20-6:10（分数0.88）
   - 理由：激烈辩论，说话密度高，人脸频繁切换
   - 安全剪辑点：5:18（静音处）、6:12（停顿处）
   
2. 12:30-13:45（分数0.82）
   - 理由：深度讨论，情绪激动
   - 安全剪辑点：12:28、13:48
```

**体育比赛：**
```
视频类型：体育
精彩片段推荐：
1. 23:15-23:45（分数0.92）
   - 理由：进球时刻，观众欢呼，画面激烈
   - 安全剪辑点：23:10、23:50
   
2. 45:00-45:30（分数0.85）
   - 理由：精彩扑救，镜头快速切换
   - 安全剪辑点：44:58、45:35
```

#### 3. 实现方案

**新增方法列表：**

| 方法 | 功能 | 依赖 |
|------|------|------|
| `detect_video_type()` | 识别视频类型 | OpenCV + 音频分析 |
| `score_scene()` | 单场景评分 | 多指标计算 |
| `find_safe_cut_points()` | 检测安全剪辑点 | 音频静音检测 + 帧分析 |
| `check_splice_compatibility()` | 检测拼接兼容性 | 相邻场景分析 |
| `select_scenes()` | 综合推荐 | 调用以上方法 |

---

### 3.1 detect_video_type() 视频类型识别

```python
def detect_video_type(
    self,
    input_video: str,
    sample_duration: float = 60.0,  # 采样时长（秒）
) -> dict:
    """
    自动识别视频类型
    
    Args:
        input_video: 输入视频路径
        sample_duration: 采样时长（秒），默认60秒
        
    Returns:
        {
            "type": "interview",        # 视频类型
            "confidence": 0.85,         # 置信度
            "features": {               # 检测到的特征
                "scene_change_rate": 0.2,   # 场景切换频率
                "face_count": 2,             # 人脸数量
                "speech_ratio": 0.8,         # 说话占比
                "avg_audio_energy": 0.6,     # 平均音频能量
            }
        }
    """
```

**识别逻辑：**
| 视频类型 | 特征组合 |
|---------|---------|
| 访谈 | 人脸≥2 + 说话占比高 + 场景切换少 |
| 演讲 | 人脸=1 + 说话占比高 + 场景切换少 |
| 体育 | 场景切换频繁 + 音频能量波动大 |
| 电影 | 场景切换适中 + 人脸不固定 |
| 搞笑 | 笑声检测 + 短场景 |
| 教程 | 人脸=1 + 说话清晰 + 画面稳定 |

---

### 3.2 score_scene() 场景评分

```python
def score_scene(
    self,
    input_video: str,
    scene: dict,              # 场景信息 {start, end, duration}
    video_type: str,          # 视频类型
    scoring_profile: dict,    # 评分权重
) -> dict:
    """
    对单个场景进行多维度评分
    
    Args:
        input_video: 输入视频
        scene: 场景信息
        video_type: 视频类型
        scoring_profile: 评分权重配置
        
    Returns:
        {
            "score": 0.85,              # 总分
            "metrics": {                # 各项指标
                "audio_energy": 0.8,
                "visual_intensity": 0.7,
                "speech_density": 0.9,
                "face_change": 0.6,
            },
            "reason": "激烈对话，说话密度高",  # 理由
        }
    """
```

---

### 3.3 find_safe_cut_points() 安全剪辑点检测

```python
def find_safe_cut_points(
    self,
    input_video: str,
    scene: dict,
    min_silence_duration: float = 0.3,  # 最小静音时长
) -> list:
    """
    检测场景内的安全剪辑点
    
    Args:
        input_video: 输入视频
        scene: 场景信息
        min_silence_duration: 最小静音时长（秒）
        
    Returns:
        [
            {"time": 5.2, "type": "scene_start", "safe": True, "score": 1.0},
            {"time": 10.5, "type": "silence", "safe": True, "score": 0.9},
            {"time": 15.0, "type": "speech_pause", "safe": True, "score": 0.8},
            {"time": 12.0, "type": "speech_mid", "safe": False, "score": 0.0},
        ]
    """
```

**剪辑点类型优先级：**
| 类型 | 安全度 | 分数 | 说明 |
|------|--------|------|------|
| scene_start | ⭐⭐⭐ | 1.0 | 场景开始，最安全 |
| scene_end | ⭐⭐⭐ | 1.0 | 场景结束，最安全 |
| silence | ⭐⭐⭐ | 0.9 | 静音处，安全 |
| speech_pause | ⭐⭐ | 0.7 | 说话停顿，较安全 |
| action_pause | ⭐⭐ | 0.7 | 动作停顿，较安全 |
| speech_mid | ❌ | 0.0 | 说话中间，禁止 |

---

### 3.4 check_splice_compatibility() 拼接兼容性检测

```python
def check_splice_compatibility(
    self,
    input_video: str,
    scene1: dict,
    scene2: dict,
) -> dict:
    """
    检测两个场景是否可以拼接
    
    Args:
        input_video: 输入视频
        scene1: 前一个场景
        scene2: 后一个场景
        
    Returns:
        {
            "compatible": True,
            "score": 0.8,
            "issues": [],           # 问题列表
            "suggestions": [],      # 建议列表
            "warnings": [
                {"type": "volume_jump", "detail": "音量差异 15dB", "severity": "warning"}
            ]
        }
    """
```

**检测项：**
| 检测项 | 问题 | 严重程度 | 建议 |
|--------|------|---------|------|
| 音量差异 | 差异>10dB | warning | 音量均衡 |
| 分辨率不同 | 不一致 | error | 统一分辨率 |
| 画面跳跃 | 颜色/场景差异大 | warning | 添加过渡 |
| 帧率不同 | 不一致 | warning | 统一帧率 |

---

### 3.5 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `sample_duration` | float | 60.0 | 视频类型识别采样时长 |
| `min_silence_duration` | float | 0.3 | 最小静音时长（秒） |
| `scoring_profile` | dict | 根据视频类型 | 评分权重配置 |
| `safe_threshold` | float | 0.7 | 安全剪辑点最低分数 |

#### 4. API 设计

**新增操作：**

| 操作 | 说明 | 输入 | 输出 |
|------|------|------|------|
| `detect_type` | 识别视频类型 | video | 类型 + 置信度 + 特征 |
| `select_scenes` | 推荐精彩场景 | video + 类型 | 场景列表 + 评分 + 理由 |
| `find_cuts` | 检测安全剪辑点 | video + 场景 | 剪辑点列表 + 安全度 |
| `check_splice` | 检测拼接兼容性 | scene1 + scene2 | 兼容性 + 问题 + 建议 |
| `export_scenes` | 导出选中场景 | video + 场景列表 | 输出文件列表 |

---

### 4.1 detect_type 识别视频类型

```bash
python edit_video.py --operation detect_type --input video.mp4
```

**返回：**
```json
{
  "success": true,
  "message": "视频类型识别完成",
  "data": {
    "type": "interview",
    "confidence": 0.85,
    "features": {
      "scene_change_rate": 0.2,
      "face_count": 2,
      "speech_ratio": 0.8,
      "avg_audio_energy": 0.6
    }
  }
}
```

---

### 4.2 select_scenes 推荐精彩场景

```bash
python edit_video.py --operation select_scenes --input video.mp4 --params '{
  "video_type": "auto",
  "top_n": 5,
  "min_score": 0.5,
  "with_cut_points": true
}'
```

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `video_type` | str | "auto" | 视频类型，auto=自动识别 |
| `top_n` | int | 5 | 返回前 N 个场景 |
| `min_score` | float | 0.5 | 最低分数阈值 |
| `with_cut_points` | bool | true | 是否包含剪辑点建议 |

**返回：**
```json
{
  "success": true,
  "message": "推荐 5 个精彩场景",
  "data": {
    "video_type": "interview",
    "total_scenes": 12,
    "recommended": [
      {
        "index": 3,
        "start": 45.2,
        "end": 62.8,
        "duration": 17.6,
        "score": 0.89,
        "reason": "激烈对话，说话密度高",
        "cut_points": [
          {"time": 45.0, "type": "scene_start", "safe": true},
          {"time": 63.0, "type": "silence", "safe": true}
        ]
      }
    ]
  }
}
```

---

### 4.3 find_cuts 检测安全剪辑点

```bash
python edit_video.py --operation find_cuts --input video.mp4 --params '{
  "start": 45.2,
  "end": 62.8
}'
```

**返回：**
```json
{
  "success": true,
  "message": "检测到 5 个剪辑点",
  "data": {
    "cut_points": [
      {"time": 45.0, "type": "scene_start", "safe": true, "score": 1.0},
      {"time": 50.2, "type": "silence", "safe": true, "score": 0.9},
      {"time": 55.0, "type": "speech_pause", "safe": true, "score": 0.7},
      {"time": 60.5, "type": "speech_mid", "safe": false, "score": 0.0},
      {"time": 63.0, "type": "scene_end", "safe": true, "score": 1.0}
    ],
    "best_cut": {"in": 45.0, "out": 63.0}
  }
}
```

---

### 4.4 check_splice 检测拼接兼容性

```bash
python edit_video.py --operation check_splice --input video.mp4 --params '{
  "scene1": {"start": 45.0, "end": 63.0},
  "scene2": {"start": 120.0, "end": 145.0}
}'
```

**返回：**
```json
{
  "success": true,
  "message": "拼接兼容性检测完成",
  "data": {
    "compatible": true,
    "score": 0.75,
    "issues": [
      {
        "type": "volume_jump",
        "detail": "音量差异 12dB",
        "severity": "warning",
        "suggestion": "建议音量均衡"
      }
    ],
    "warnings": ["场景画面差异较大，建议添加过渡效果"]
  }
}
```

---

### 4.5 export_scenes 导出选中场景

```bash
python edit_video.py --operation export_scenes --input video.mp4 --output ./output --params '{
  "scenes": [
    {"start": 45.0, "end": 63.0},
    {"start": 120.0, "end": 145.0}
  ],
  "merge": true,
  "add_transitions": true
}'
```

**参数说明：**
| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `scenes` | list | 必填 | 场景列表 |
| `merge` | bool | false | 是否合并为一个文件 |
| `add_transitions` | bool | false | 是否添加过渡效果 |

**返回：**
```json
{
  "success": true,
  "message": "导出 2 个场景",
  "data": {
    "output_files": ["output/scene_001.mp4", "output/scene_002.mp4"],
    "merged_file": "output/merged.mp4"
  }
}
```

#### 5. 后续优化

**短期优化（V2.6）：**
- 更多视频类型识别（游戏、美食、旅行等）
- 自定义评分权重
- 批量导出 + 自动合并

**中期优化（V3）：**
- Whisper 语音内容分析
- 字幕关键词匹配
- 人脸表情识别

**长期优化（V4）：**
- 深度学习场景分类
- 多模态综合分析
- 用户反馈学习

#### 6. 测试计划

**单元测试：**

| 测试项 | 测试内容 | 预期结果 |
|--------|---------|---------|
| `test_detect_video_type` | 识别访谈视频 | type=interview, confidence>0.7 |
| `test_detect_video_type_sports` | 识别体育视频 | type=sports |
| `test_score_scene` | 场景评分 | 0 <= score <= 1 |
| `test_find_safe_cut_points` | 检测剪辑点 | 返回列表，包含 safe=True 的点 |
| `test_check_splice_compatibility` | 拼接检测 | 返回 compatible 和 issues |

**集成测试：**

```bash
# 1. 视频类型识别
python edit_video.py --operation detect_type --input tests/test1.mp4

# 2. 精彩场景推荐
python edit_video.py --operation select_scenes --input tests/test1.mp4 --params '{"top_n": 5}'

# 3. 安全剪辑点检测
python edit_video.py --operation find_cuts --input tests/test1.mp4 --params '{"start": 0, "end": 60}'

# 4. 拼接兼容性检测
python edit_video.py --operation check_splice --input tests/test1.mp4 --params '{"scene1": {"start": 0, "end": 30}, "scene2": {"start": 60, "end": 90}}'

# 5. 完整流程测试
python edit_video.py --operation select_scenes --input tests/test1.mp4 --params '{"top_n": 3, "with_cut_points": true}'
```

**验收标准：**

| 功能 | 验收标准 |
|------|---------|
| 视频类型识别 | 准确率 > 80% |
| 精彩场景推荐 | 推荐场景确实精彩（人工验证） |
| 安全剪辑点 | 不切断说话、动作 |
| 拼接检测 | 能发现音量差异、画面跳跃问题 |

#### 7. 开发清单

**第一阶段：视频类型识别**
| 任务 | 文件 | 状态 |
|------|------|------|
| 实现 detect_video_type() | modules/analyzer.py | ⏳ 待开发 |
| 添加人脸检测辅助方法 | modules/analyzer.py | ⏳ 待开发 |
| 更新 edit_video.py 操作表 | edit_video.py | ⏳ 待开发 |
| 单元测试 | tests/test_detect_type.py | ⏳ 待开发 |

**第二阶段：场景评分系统**
| 任务 | 文件 | 状态 |
|------|------|------|
| 实现 score_scene() | modules/analyzer.py | ⏳ 待开发 |
| 实现 select_scenes() | modules/analyzer.py | ⏳ 待开发 |
| 添加评分权重配置 | modules/analyzer.py | ⏳ 待开发 |
| 更新 edit_video.py 操作表 | edit_video.py | ⏳ 待开发 |
| 单元测试 | tests/test_score_scene.py | ⏳ 待开发 |

**第三阶段：安全剪辑点**
| 任务 | 文件 | 状态 |
|------|------|------|
| 实现 find_safe_cut_points() | modules/analyzer.py | ⏳ 待开发 |
| 实现 check_splice_compatibility() | modules/analyzer.py | ⏳ 待开发 |
| 更新 edit_video.py 操作表 | edit_video.py | ⏳ 待开发 |
| 单元测试 | tests/test_cut_points.py | ⏳ 待开发 |

**第四阶段：导出功能**
| 任务 | 文件 | 状态 |
|------|------|------|
| 实现 export_scenes() | modules/executor.py | ⏳ 待开发 |
| 更新 edit_video.py 操作表 | edit_video.py | ⏳ 待开发 |
| 单元测试 | tests/test_export.py | ⏳ 待开发 |

**第五阶段：文档更新**
| 任务 | 文件 | 状态 |
|------|------|------|
| 更新 api-reference.md | memory-bank/api-reference.md | ⏳ 待开发 |
| 更新 progress.md | memory-bank/progress.md | ⏳ 待开发 |
| 集成测试 | tests/ | ⏳ 待开发 |

#### 8. 风险评估

**技术风险：**

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 视频类型识别不准 | 中 | 高 | 提供手动选择类型选项，降低依赖 |
| 评分权重不合理 | 中 | 中 | 提供自定义权重接口，用户可调整 |
| 安全剪辑点误判 | 中 | 高 | 保守策略：宁可多留，不可少留 |
| 拼接检测漏报 | 低 | 中 | 提供预览功能，用户确认后再执行 |
| 性能问题（长视频） | 中 | 低 | 采样分析，不处理全部帧 |

**用户体验风险：**

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 推荐场景用户不满意 | 中 | 中 | 提供"重新推荐"选项，收集反馈 |
| 剪辑点不自然 | 低 | 高 | 安全边距 + 预览确认 |
| 操作流程复杂 | 中 | 中 | 简化步骤，一键智能剪辑 |

**兼容性风险：**

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| OpenCV 人脸检测失败 | 低 | 中 | 降级处理，不影响其他功能 |
| 音频分析失败（无音轨） | 低 | 低 | 已有优雅降级处理 |
| FFmpeg 版本兼容 | 低 | 中 | 已测试 FFmpeg 7.x 兼容 |

#### 9. 时间估算

| 阶段 | 任务 | 预计时间 |
|------|------|---------|
| **第一阶段** | 视频类型识别 | 2 小时 |
| | - detect_video_type() 实现 | 1 小时 |
| | - 人脸检测辅助方法 | 30 分钟 |
| | - 测试 + 调试 | 30 分钟 |
| **第二阶段** | 场景评分系统 | 2.5 小时 |
| | - score_scene() 实现 | 1 小时 |
| | - select_scenes() 实现 | 1 小时 |
| | - 评分权重配置 | 30 分钟 |
| **第三阶段** | 安全剪辑点 | 1.5 小时 |
| | - find_safe_cut_points() | 1 小时 |
| | - check_splice_compatibility() | 30 分钟 |
| **第四阶段** | 导出功能 | 1 小时 |
| | - export_scenes() | 1 小时 |
| **第五阶段** | 文档 + 测试 | 1 小时 |
| | - 文档更新 | 30 分钟 |
| | - 集成测试 | 30 分钟 |
| **总计** | | **8 小时** |

**建议开发顺序：**
1. 先完成第一阶段（视频类型识别），独立可用
2. 再完成第二阶段（场景评分），核心功能
3. 第三、四阶段可并行开发
4. 最后统一测试和文档更新

## 未开始

**V2 Step 6 — AI 辅助场景选择**
- AI 根据用户意图推荐场景
- 批量操作多个场景

**V3 — 自动字幕**
- `transcribe()` — Whisper 语音识别
- 生成 SRT 字幕文件
- FFmpeg 字幕烧录

**V4 — 智能剪辑**
- `score_segments()` — 结合音频能量 + 场景变化频率打分
- `select_highlights()` — 选出最佳片段
- 短视频合成
- 背景音乐添加

## 已知问题
- `concat` 临时文件写在当前目录 — 并发使用前需修复，改用 `tempfile.mkstemp()`
- `Parser` 模块仍存在但已废弃 — 后续可清理

## 里程碑

| 里程碑 | 状态 | 日期 |
|---|---|---|
| V1 基础剪辑（裁剪/合并/转换） | ✅ 完成 | 2026-03-24 |
| remove_silence（FFmpeg 7.x） | ✅ 完成 | 2026-03-24 |
| remove_static（OpenCV） | ✅ 完成 | 2026-03-25 |
| Analyzer 共用模块 | ✅ 完成 | 2026-03-25 |
| edit_video.py AI 入口 | ✅ 完成 | 2026-03-25 |
| memory-bank 初始化 | ✅ 完成 | 2026-03-25 |
| V2 detect_scenes + split_by_scenes | ✅ 完成 | 2026-03-25 |
| V2 场景+音频联合分析 | ✅ 完成 | 2026-03-25 |
| V3 自动字幕 | ⏳ 计划中 | — |
| V4 智能剪辑 | ⏳ 计划中 | — |
