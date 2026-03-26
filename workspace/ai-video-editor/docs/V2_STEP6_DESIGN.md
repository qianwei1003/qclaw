# V2 Step 6: AI 辅助场景选择 - 设计文档

**版本：** 1.0  
**日期：** 2026-03-26  
**状态：** 设计中

---

## 1. 开发理由

### 1.1 用户痛点

当视频有几十个场景时，用户不知道该选哪些场景：
- "我想要精彩片段" → 哪些是精彩？
- "我想要有说话的部分" → 哪些场景有人说话？
- "我想要动作部分" → 哪些场景动作多？

### 1.2 解决方案

AI 根据用户意图，自动分析场景内容，推荐最匹配的场景：
- 用户说 "我要精彩片段" → AI 分析音频能量 + 画面变化，推荐高分场景
- 用户说 "我要安静的部分" → AI 推荐低能量场景
- 用户说 "我要有动作的部分" → AI 推荐画面变化频繁的场景

### 1.3 核心价值

| 用户输入 | AI 分析 | 输出 |
|---------|--------|------|
| "精彩片段" | 音频能量高 + 画面变化大 | 推荐场景列表 |
| "安静部分" | 音频能量低 | 推荐场景列表 |
| "有动作的部分" | 画面变化频率高 | 推荐场景列表 |
| "前半部分" | 时间范围筛选 | 推荐场景列表 |

---

## 2. 功能设计

### 2.1 整体流程

```
用户输入意图
    ↓
【意图识别】AI 判断用户想要什么类型的内容
    ↓
【场景分析】调用 analyze_content_density 获取场景评分
    ↓
【场景筛选】根据意图类型筛选场景
    ↓
【输出结果】推荐场景列表 + 理由
```

### 2.2 新增操作

| 操作 | 说明 | 输入 | 输出 |
|------|------|------|------|
| `select_scenes` | 根据意图推荐场景 | intent, top_n, min_score | 推荐场景列表 |
| `export_scenes` | 导出选中的场景 | scene_indices, output_dir | 多个视频文件 |

---

## 3. 实现方案

### 3.1 新增方法：Analyzer.select_scenes()

```python
def select_scenes(
    self,
    input_video: str,
    intent: str,                    # 用户意图：exciting/quiet/action/dialogue/custom
    top_n: int = 5,                 # 返回前 N 个场景
    min_score: float = 0.3,         # 最低分数阈值
    scene_threshold: float = 0.4,   # 场景检测敏感度
    min_scene_duration: float = 1.0,# 最小场景时长
    audio_weight: float = 0.6,      # 音频权重
    visual_weight: float = 0.4,     # 视觉权重
) -> list[dict]:
    """
    根据用户意图推荐场景
    
    Args:
        input_video: 输入视频路径
        intent: 用户意图类型
            - "exciting": 精彩片段（高能量 + 高变化）
            - "quiet": 安静部分（低能量）
            - "action": 动作部分（高视觉变化）
            - "dialogue": 对话部分（中等能量 + 低变化）
            - "intro": 开头部分（时间筛选）
            - "outro": 结尾部分（时间筛选）
        top_n: 返回前 N 个场景
        min_score: 最低分数阈值（0-1）
        scene_threshold: 场景检测敏感度（越低越敏感）
        min_scene_duration: 最小场景时长（秒）
        audio_weight: 音频能量权重
        visual_weight: 视觉变化权重
        
    Returns:
        推荐场景列表，每个场景包含：
        {
            "index": int,           # 场景编号
            "start": float,         # 开始时间
            "end": float,           # 结束时间
            "duration": float,      # 时长
            "score": float,         # 匹配分数
            "reason": str,          # 推荐理由
        }
    """
```

### 3.2 参数详解

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `input_video` | str | 必填 | 输入视频路径 |
| `intent` | str | 必填 | 用户意图类型 |
| `top_n` | int | 5 | 返回前 N 个场景 |
| `min_score` | float | 0.3 | 最低分数阈值，低于此值的场景不推荐 |
| `scene_threshold` | float | 0.4 | 场景检测敏感度，越低越敏感 |
| `min_scene_duration` | float | 1.0 | 最小场景时长（秒） |
| `audio_weight` | float | 0.6 | 音频能量在评分中的权重 |
| `visual_weight` | float | 0.4 | 视觉变化在评分中的权重 |

### 3.3 意图类型说明

| intent | 含义 | 评分逻辑 |
|--------|------|---------|
| `exciting` | 精彩片段 | audio_score × audio_weight + visual_score × visual_weight |
| `quiet` | 安静部分 | 1 - audio_score（音频能量越低分数越高） |
| `action` | 动作部分 | visual_score（只看画面变化） |
| `dialogue` | 对话部分 | 中等音频能量 + 低视觉变化 |
| `intro` | 开头部分 | 按时间筛选前 20% |
| `outro` | 结尾部分 | 按时间筛选后 20% |

### 3.4 实现代码

```python
def select_scenes(
    self,
    input_video: str,
    intent: str,
    top_n: int = 5,
    min_score: float = 0.3,
    scene_threshold: float = 0.4,
    min_scene_duration: float = 1.0,
    audio_weight: float = 0.6,
    visual_weight: float = 0.4,
) -> list[dict]:
    """根据用户意图推荐场景"""
    
    # 1. 获取场景和内容分析
    scenes = self.detect_scenes(input_video, scene_threshold, min_scene_duration)
    content_analysis = self.analyze_content_density(
        input_video, 
        scene_threshold, 
        min_scene_duration,
        audio_weight,
        visual_weight
    )
    
    if not scenes:
        return []
    
    # 2. 根据意图计算匹配分数
    for scene in scenes:
        content = content_analysis[scene["index"]]
        
        if intent == "exciting":
            # 高能量 + 高变化
            scene["score"] = content["content_score"]
            scene["reason"] = f"高能量场景（分数: {scene['score']:.2f}）"
            
        elif intent == "quiet":
            # 低能量
            scene["score"] = 1 - content["audio_score"]
            scene["reason"] = f"安静场景（音频能量: {content['audio_score']:.2f}）"
            
        elif intent == "action":
            # 高视觉变化
            scene["score"] = content["visual_score"]
            scene["reason"] = f"动作场景（视觉变化: {scene['score']:.2f}）"
            
        elif intent == "dialogue":
            # 中等能量 + 低变化
            audio_factor = 1 - abs(content["audio_score"] - 0.5) * 2
            visual_factor = 1 - content["visual_score"]
            scene["score"] = audio_factor * 0.6 + visual_factor * 0.4
            scene["reason"] = f"对话场景（音频适中，变化少）"
            
        elif intent == "intro":
            # 前 20%
            total_duration = scenes[-1]["end"]
            if scene["start"] < total_duration * 0.2:
                scene["score"] = 1.0
            else:
                scene["score"] = 0.0
            scene["reason"] = "开头部分"
            
        elif intent == "outro":
            # 后 20%
            total_duration = scenes[-1]["end"]
            if scene["end"] > total_duration * 0.8:
                scene["score"] = 1.0
            else:
                scene["score"] = 0.0
            scene["reason"] = "结尾部分"
            
        else:
            # 未知意图，使用默认分数
            scene["score"] = content["content_score"]
            scene["reason"] = f"默认推荐（分数: {scene['score']:.2f}）"
    
    # 3. 过滤低分场景
    filtered = [s for s in scenes if s["score"] >= min_score]
    
    # 4. 按分数排序
    filtered.sort(key=lambda x: x["score"], reverse=True)
    
    # 5. 返回前 N 个
    return filtered[:top_n]
```

### 3.5 新增方法：Executor._export_scenes()

```python
def _export_scenes(
    self,
    params: Dict[str, Any],
    input_video: str,
    output_dir: str,
) -> bool:
    """
    导出选中的场景
    
    Args:
        params: {
            "scene_indices": [0, 2, 5],  # 要导出的场景编号列表
            "scene_threshold": 0.4,
            "min_scene_duration": 1.0,
        }
        input_video: 输入视频
        output_dir: 输出目录
        
    Returns:
        True 成功
    """
```

---

## 4. API 设计

### 4.1 select_scenes 操作

```bash
python edit_video.py --operation select_scenes --input video.mp4 --params '{"intent": "exciting", "top_n": 5}'
```

**返回：**
```json
{
  "success": true,
  "message": "Found 5 scenes matching 'exciting'",
  "data": {
    "intent": "exciting",
    "total_scenes": 12,
    "recommended": [
      {
        "index": 3,
        "start": 45.2,
        "end": 62.8,
        "duration": 17.6,
        "score": 0.89,
        "reason": "高能量场景（分数: 0.89）"
      },
      ...
    ]
  }
}
```

### 4.2 export_scenes 操作

```bash
python edit_video.py --operation export_scenes --input video.mp4 --output ./output --params '{"scene_indices": [0, 2, 5]}'
```

**返回：**
```json
{
  "success": true,
  "message": "Exported 3 scenes",
  "data": {
    "exported_files": [
      "output/scene_000.mp4",
      "output/scene_002.mp4",
      "output/scene_005.mp4"
    ]
  }
}
```

---

## 5. 后续优化

### 5.1 短期优化（V2.1）

| 优化项 | 说明 |
|--------|------|
| 更多意图类型 | 添加 "funny"、"sad"、"romantic" 等情感意图 |
| 自定义权重 | 允许用户自定义 audio_weight 和 visual_weight |
| 时间范围筛选 | 支持 "10秒到30秒之间的精彩片段" |
| 批量导出 | 导出后自动合并成一个视频 |

### 5.2 中期优化（V3）

| 优化项 | 说明 |
|--------|------|
| 语音内容分析 | 结合 Whisper，识别 "有人说话" 的场景 |
| 字幕匹配 | 根据 subtitle 关键词匹配场景 |
| 人脸检测 | 识别 "有人脸" 的场景 |

### 5.3 长期优化（V4）

| 优化项 | 说明 |
|--------|------|
| 深度学习 | 使用预训练模型识别场景类型 |
| 多模态分析 | 结合图像、音频、字幕综合分析 |
| 用户反馈学习 | 根据用户选择优化推荐算法 |

---

## 6. 测试计划

### 6.1 单元测试

```python
def test_select_scenes_exciting():
    """测试精彩片段选择"""
    result = analyzer.select_scenes(video, "exciting", top_n=3)
    assert len(result) <= 3
    for scene in result:
        assert scene["score"] >= 0.3
        assert "reason" in scene

def test_select_scenes_quiet():
    """测试安静片段选择"""
    result = analyzer.select_scenes(video, "quiet", top_n=3)
    for scene in result:
        # 安静场景的分数应该是 1 - audio_score
        assert scene["score"] >= 0.3
```

### 6.2 集成测试

```bash
# 测试精彩片段选择
python edit_video.py --operation select_scenes --input test1.mp4 --params '{"intent": "exciting", "top_n": 5}'

# 测试导出场景
python edit_video.py --operation export_scenes --input test1.mp4 --output ./test_output --params '{"scene_indices": [0, 1, 2]}'
```

---

## 7. 开发清单

| 任务 | 文件 | 状态 |
|------|------|------|
| 实现 Analyzer.select_scenes() | modules/analyzer.py | ⏳ 待开发 |
| 实现 Executor._export_scenes() | modules/executor.py | ⏳ 待开发 |
| 更新 edit_video.py 操作表 | edit_video.py | ⏳ 待开发 |
| 更新 api-reference.md | memory-bank/api-reference.md | ⏳ 待开发 |
| 单元测试 | tests/test_select_scenes.py | ⏳ 待开发 |
| 集成测试 | tests/ | ⏳ 待开发 |

---

## 8. 风险评估

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 意图识别不准确 | 中 | 中 | 提供多种预设意图，允许自定义权重 |
| 场景评分不准确 | 中 | 中 | 结合多种指标（音频+视觉）综合评分 |
| 性能问题 | 低 | 低 | 场景分析已优化，select_scenes 只是计算 |

---

## 9. 时间估算

| 阶段 | 时间 |
|------|------|
| 开发 Analyzer.select_scenes() | 1 小时 |
| 开发 Executor._export_scenes() | 30 分钟 |
| 更新文档 | 30 分钟 |
| 测试 | 1 小时 |
| **总计** | **3 小时** |

---

**确认后开始开发？**
