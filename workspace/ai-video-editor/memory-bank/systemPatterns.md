# 系统架构

## 架构总览

```
用户 / AI
    ↓
edit_video.py          ← AI 调用入口（结构化 CLI，JSON 输出）
    ↓
Executor               ← 将操作映射为 FFmpeg 命令
    ↓
FFmpeg                 ← 实际视频处理

Analyzer               ← 共用分析层（供 Executor 和后续阶段使用）
    ├── extract_audio          提取音频
    ├── detect_scenes          场景检测
    ├── extract_thumbnail      提取缩略图
    ├── analyze_audio_energy   音频能量分析
    └── detect_static_segments 静止帧检测

Validator              ← 每次操作后验证输出
```

## 模块职责

| 模块 | 文件 | 职责 |
|---|---|---|
| `edit_video.py` | 项目根目录 | AI 调用入口；验证参数；路由到 Executor |
| `Executor` | `modules/executor.py` | 将结构化指令转为 FFmpeg 命令；处理重试 |
| `Analyzer` | `modules/analyzer.py` | 视频/音频分析；供 V1–V4 共用 |
| `Validator` | `modules/validator.py` | 执行后验证输出文件 |
| `Parser` | `modules/parser.py` | **已废弃** — 自然语言解析器，AI 流程不再使用 |

## 关键设计模式

- **结构化指令约定**：所有操作使用 `{"operation": str, "params": dict}`，Executor 不接收原始文本
- **纯 JSON 输出**：`edit_video.py` 始终返回 `{success, message, data}`，AI 可确定性解析
- **报错附带示例**：参数缺失时返回示例参数，AI 无需人工介入即可自我纠正
- **共用分析层**：`Analyzer` 由 Executor 内部实例化，调用方不直接调用 Analyzer
- **FFmpeg 自动降级**：优先尝试 `-c copy`，失败后自动重新编码

## 数据流

```
AI 调用 → edit_video.py
  → 验证参数
  → 构建 instruction dict
  → Executor.execute(instruction, input, output)
      → Analyzer（按需，如 remove_static、remove_silence）
      → 构建 FFmpeg 命令
      → _run_ffmpeg()
  → Validator.validate(output)
  → 返回 JSON 结果给 AI
```

## 关键约束
- 传给 FFmpeg 的路径必须使用正斜杠（Windows 兼容，通过 `_normalize_path()` 处理）
- 临时文件必须使用 `tempfile.mkstemp()`，禁止硬编码路径（并发安全）
- 使用 OpenCV VideoCapture 时，`cap.release()` 必须在 `try/finally` 中执行
