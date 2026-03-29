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


def run_operation(operation: str, input_video, output_path: str, params: dict) -> tuple[str, str]:
    """Run edit_video.py operation.
    
    Args:
        operation: Operation name.
        input_video: Input video path.
        output_path: Output path.
        params: Operation parameters.
    
    Returns:
        (output_info, command)
    """
    if input_video is None:
        return "请先上传视频", ""
    
    # Build command
    cmd = [
        "python", os.path.join(PROJECT_DIR, "edit_video.py"),
        "--operation", operation,
        "--input", input_video,
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
        )
        
        if result.returncode == 0:
            return result.stdout, " ".join(cmd)
        else:
            return f"错误: {result.stderr}", " ".join(cmd)
    except Exception as e:
        return f"执行失败: {e}", ""


def on_auto_subtitle(
    input_video,
    language: str,
    model: str,
    extract_vocals: bool,
    initial_prompt: str,
    temperature: float,
) -> tuple[str, str]:
    """Handle auto_subtitle operation."""
    params = {
        "language": language,
        "model": model,
        "extract_vocals": extract_vocals,
        "temperature": temperature,
    }
    if initial_prompt:
        params["initial_prompt"] = initial_prompt
    
    output_path = os.path.join(PROJECT_DIR, "output_subtitled.mp4")
    return run_operation("auto_subtitle", input_video, output_path, params)


def on_transcribe(
    input_video,
    language: str,
    model: str,
) -> tuple[str, str]:
    """Handle transcribe operation."""
    params = {
        "language": language,
        "model": model,
    }
    return run_operation("transcribe", input_video, None, params)


def on_separate_vocals(input_video) -> tuple[str, str]:
    """Handle separate_vocals operation."""
    return run_operation("separate_vocals", input_video, None, {})


def on_info(input_video) -> tuple[str, str]:
    """Handle info operation."""
    return run_operation("info", input_video, None, {})


# Create Gradio interface
with gr.Blocks(title="AI Video Editor") as app:
    gr.Markdown("# AI Video Editor 测试界面")
    gr.Markdown("上传视频，选择功能，点击执行")
    
    with gr.Row():
        with gr.Column(scale=1):
            # Input
            input_video = gr.File(label="上传视频", file_types=[".mp4", ".mkv", ".avi", ".mov"])
            
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
        outputs=[output, command],
    )
    
    btn_separate.click(
        fn=on_separate_vocals,
        inputs=[input_video],
        outputs=[output, command],
    )
    
    btn_transcribe.click(
        fn=on_transcribe,
        inputs=[input_video, language, model],
        outputs=[output, command],
    )
    
    btn_auto_subtitle.click(
        fn=on_auto_subtitle,
        inputs=[input_video, language, model, extract_vocals, initial_prompt, temperature],
        outputs=[output, command],
    )
    
    # Examples
    gr.Markdown("## 使用说明")
    gr.Markdown("""
    1. 上传视频文件（支持 mp4, mkv, avi, mov）
    2. 选择语言和模型
    3. 点击功能按钮执行
    
    **功能说明：**
    - **获取视频信息**：查看视频时长、分辨率等信息
    - **提取人声**：去除背景音乐，提取人声
    - **语音识别**：使用 Whisper 识别语音
    - **一键字幕**：自动完成人声提取 + 语音识别 + 字幕烧录
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