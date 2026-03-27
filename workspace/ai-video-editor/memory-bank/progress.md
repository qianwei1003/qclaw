# 进度

## 当前状态
**V1、V2、V3 已完成。V4 待开始。**

最新更新: 2026-03-27

---

## 已完成 ✅

### V1: 基础自动剪辑
- `trim_start` — 删除视频开头
- `trim_end` — 删除视频结尾
- `trim_range` — 保留单段时间范围
- `trim_range` 多段 — 保留多段并自动合并
- `concat` — 合并多个视频文件
- `convert` — 改变分辨率
- `remove_silence` — 检测并删除静音段
- `remove_static` — 检测并删除静止帧段

### V2: 场景分割
- `detect_scenes` — 检测场景切换点
- `split_by_scenes` — 按场景切割为多个文件
- `extract_scene_thumbnails` — 为每个场景提取缩略图
- `analyze_content` — 场景+音频联合分析

### V2 Step 6: AI辅助场景选择
- `detect_video_type()` — 视频类型识别
- `score_scene()` — 多维度场景评分
- `find_safe_cut_points()` — 安全剪辑点检测
- `check_splice_compatibility()` — 拼接兼容性检测
- `select_scenes()` — 精彩场景推荐

### V3: 自动字幕
- `transcribe()` — Whisper语音识别
- `generate_srt()` — 生成SRT字幕文件
- `burn_subtitle()` — FFmpeg字幕烧录
- `auto_subtitle` — 一键字幕

---

## 进行中 ⏳
- V4: 智能剪辑（待设计）

## 未开始 📋
**V4 — 智能剪辑**
- 自动选段算法
- 转场效果
- 背景音乐
- 短视频合成

---

## 配置文件
- `config.yaml` — 所有参数可配置

## 设计文档
- `docs/V2_STEP6_DESIGN.md` — AI辅助场景选择
- `docs/V3_SUBTITLE_DESIGN.md` — 自动字幕
