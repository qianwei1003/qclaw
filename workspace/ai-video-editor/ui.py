"""
ui.py - AI Video Editor Web UI

A simple web interface for testing video editing features.

Usage:
    python ui.py

Then open http://localhost:7860 in your browser.
"""

import os
import subprocess
import json

try:
    import gradio as gr
except ImportError:
    print("Gradio not installed. Run: pip install gradio")
    exit(1)


# Get project directory
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))


def get_local_videos():
    """Get list of video files in videos directory."""
    videos_dir = os.path.join(PROJECT_DIR, "videos")
    if not os.path.exists(videos_dir):
        os.makedirs(videos_dir, exist_ok=True)
    
    video_extensions = ['.mp4', '.mkv', '.avi', '.mov', '.webm']
    videos = []
    for f in os.listdir(videos_dir):
        if any(f.lower().endswith(ext) for ext in video_extensions):
            videos.append(f)
    return sorted(videos)


def run_operation(operation: str, input_video: str, output_path: str, params: dict) -> tuple[str, str, str]:
    """Run edit_video.py operation.
    
    Args:
        operation: Operation name.
        input_video: Input video path (filename or full path).
        output_path: Output path.
        params: Operation parameters.
    
    Returns:
        (output_info, command, output_file)
    """
    if not input_video:
        return "请先选择或输入视频路径", "", ""
    
    # Videos and output directories
    videos_dir = os.path.join(PROJECT_DIR, "videos")
    output_dir = os.path.join(PROJECT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # If input is just a filename, prepend videos directory
    if not os.path.isabs(input_video):
        input_video_path = os.path.join(videos_dir, input_video)
    else:
        input_video_path = input_video
    
    # Check if file exists
    if not os.path.exists(input_video_path):
        return f"视频文件不存在: {input_video_path}", "", ""
    
    # Build command
    cmd = [
        "python", os.path.join(PROJECT_DIR, "edit_video.py"),
        "--operation", operation,
        "--input", input_video_path,
    ]
    
    if output_path:
        cmd.extend(["--output", output_path])
    
    if params:
        cmd.extend(["--params", json.dumps(params, ensure_ascii=False)])
    
    # Run command
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            cwd=PROJECT_DIR,
            timeout=600,  # 10 minutes timeout
        )
        
        # Combine stdout and stderr for complete output
        full_output = result.stdout
        if result.stderr:
            full_output += f"\n[STDERR]\n{result.stderr}"
        
        if result.returncode == 0:
            return full_output, " ".join(cmd), output_path if output_path else ""
        else:
            return f"错误 (code={result.returncode}):\n{full_output}", " ".join(cmd), ""
    except subprocess.TimeoutExpired:
        return "执行超时（超过10分钟）", " ".join(cmd), ""
    except Exception as e:
        return f"执行失败: {e}", " ".join(cmd), ""


def on_auto_subtitle(
    input_video,
    language: str,
    model: str,
    extract_vocals: bool,
    initial_prompt: str,
    temperature: float,
) -> tuple[str, str, str]:
    """Handle auto_subtitle operation."""
    params = {
        "language": language,
        "model": model,
        "extract_vocals": extract_vocals,
        "temperature": temperature,
    }
    if initial_prompt:
        params["initial_prompt"] = initial_prompt
    
    output_dir = os.path.join(PROJECT_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, "output_subtitled.mp4")
    return run_operation("auto_subtitle", input_video, output_path, params)


def on_transcribe(
    input_video,
    language: str,
    model: str,
) -> tuple[str, str, str]:
    """Handle transcribe operation."""
    params = {
        "language": language,
        "model": model,
    }
    return run_operation("transcribe", input_video, None, params)


def on_separate_vocals(input_video) -> tuple[str, str, str]:
    """Handle separate_vocals operation."""
    return run_operation("separate_vocals", input_video, None, {})


def on_info(input_video) -> tuple[str, str, str]:
    """Handle info operation."""
    return run_operation("info", input_video, None, {})


# Create Gradio interface
with gr.Blocks(title="AI Video Editor") as app:
    gr.Markdown("# AI Video Editor 测试界面")
    gr.Markdown("上传视频，选择功能，点击执行")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input - select local video
            input_video = gr.Dropdown(
                choices=get_local_videos(),
                label="选择视频",
                info="从 videos 文件夹选择",
                allow_custom_value=True,
            )
            refresh_btn = gr.Button("🔄 刷新视频列表", size="sm")
            gr.Markdown(f"""
- **原始视频**: `{PROJECT_DIR}\\videos\\`
- **输出文件**: `{PROJECT_DIR}\\output\\`
- 也可以直接输入完整路径
            """)
            
            # Common parameters
            with gr.Accordion("通用参数", open=True):
                language = gr.Dropdown(
                    choices=["zh", "en", "ja", "ko", "auto"],
                    value="zh",
                    label="语言",
                )
                model = gr.Dropdown(
                    choices=["tiny", "base", "small", "medium", "large"],
                    value="medium",
                    label="Whisper 模型",
                )
            
            # Advanced parameters
            with gr.Accordion("高级参数", open=False):
                extract_vocals = gr.Checkbox(
                    value=True,
                    label="提取人声（去除背景音乐）",
                )
                initial_prompt = gr.Textbox(
                    label="初始提示（帮助识别专有名词）",
                    placeholder="例如：这是一段关于哪吒的对话",
                    lines=2,
                )
                temperature = gr.Slider(
                    minimum=0.0,
                    maximum=1.0,
                    value=0.0,
                    step=0.1,
                    label="采样温度（越低越确定）",
                )
        
        with gr.Column(scale=1):
            # Output
            output = gr.Textbox(label="输出结果", lines=10)
            command = gr.Textbox(label="执行命令", lines=2)
            output_file = gr.Textbox(label="输出文件路径", lines=1, interactive=False)
    
    # Buttons
    with gr.Row():
        btn_info = gr.Button("获取视频信息")
        btn_separate = gr.Button("提取人声")
        btn_transcribe = gr.Button("语音识别")
        btn_auto_subtitle = gr.Button("一键字幕", variant="primary")
    
    # Button events
    btn_info.click(
        fn=on_info,
        inputs=[input_video],
        outputs=[output, command, output_file],
    )
    
    btn_separate.click(
        fn=on_separate_vocals,
        inputs=[input_video],
        outputs=[output, command, output_file],
    )
    
    btn_transcribe.click(
        fn=on_transcribe,
        inputs=[input_video, language, model],
        outputs=[output, command, output_file],
    )
    
    btn_auto_subtitle.click(
        fn=on_auto_subtitle,
        inputs=[input_video, language, model, extract_vocals, initial_prompt, temperature],
        outputs=[output, command, output_file],
    )
    
    # Refresh button event
    refresh_btn.click(
        fn=lambda: gr.Dropdown(choices=get_local_videos()),
        outputs=[input_video],
    )
    
    # Examples
    gr.Markdown("## 使用说明")
    gr.Markdown("""
    1. 把视频放到 `videos` 文件夹
    2. 点击刷新按钮
    3. 下拉框选择视频
    4. 点击功能按钮执行
    
    **功能说明：**
    - **获取视频信息**：查看视频时长、分辨率等信息
    - **提取人声**：去除背景音乐，提取人声
    - **语音识别**：使用 Whisper 识别语音
    - **一键字幕**：自动完成人声提取 + 语音识别 + 字幕烧录
    
    **输出文件位置：**
    - 所有输出文件都在 `output` 文件夹
    - 一键字幕: `output/output_subtitled.mp4`
    - 人声提取: `output/{视频名}_vocals.mp3`
    - SRT字幕: `output/{视频名}.srt`
    """)


if __name__ == "__main__":
    print("=" * 50)
    print("AI Video Editor UI")
    print("=" * 50)
    print(f"项目目录: {PROJECT_DIR}")
    print("启动中...")
    print("打开浏览器访问: http://localhost:7861")
    print("=" * 50)
    
    app.launch(server_name="0.0.0.0", server_port=7861)