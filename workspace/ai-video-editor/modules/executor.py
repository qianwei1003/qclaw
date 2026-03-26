"""
Executor 模块 - 视频处理执行器
根据结构化指令调用 FFmpeg 执行视频处理
"""

from __future__ import annotations

import os
import re
import subprocess
import tempfile
from typing import Any, Optional


class ExecutionError(Exception):
    """执行错误异常"""
    pass


class Executor:
    """
    视频处理执行器
    将结构化指令转换为 FFmpeg 命令并执行
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        self.ffmpeg_path = ffmpeg_path
        self.last_command: str | None = None
        self.last_output: str | None = None
    
    def execute(
        self, 
        instruction: dict[str, Any], 
        input_video: str, 
        output_video: str,
    ) -> bool:
        """
        执行视频处理指令
        
        Args:
            instruction: Parser 生成的结构化指令
            input_video: 输入视频路径
            output_video: 输出视频路径
            
        Returns:
            True 成功，False 失败
            
        Raises:
            ExecutionError: 执行过程中出错
        """
        # 验证输入文件
        if not os.path.exists(input_video):
            raise ExecutionError(f"输入文件不存在: {input_video}")
        
        # 标准化路径（Windows 兼容）
        input_video = self._normalize_path(input_video)
        output_video = self._normalize_path(output_video)
        
        # 获取视频时长
        duration = self.get_video_duration(input_video)
        if duration is None:
            raise ExecutionError(f"无法读取视频信息: {input_video}")
        
        # 根据操作类型执行
        operation = instruction["operation"]
        params = instruction["params"]
        
        if operation == "trim_start":
            return self._trim_start(params, input_video, output_video, duration)
        
        elif operation == "trim_end":
            return self._trim_end(params, input_video, output_video, duration)
        
        elif operation == "trim_range":
            # 检查是否是多段截取
            if "segments" in params:
                return self._trim_segments(params["segments"], input_video, output_video)
            return self._trim_range(params, input_video, output_video)
        
        elif operation == "concat":
            return self._concat(params, input_video, output_video)
        
        elif operation == "convert":
            return self._convert(params, input_video, output_video)
        
        elif operation == "remove_silence":
            return self._remove_silence(params, input_video, output_video)
        
        elif operation == "remove_static":
            return self._remove_static(params, input_video, output_video)

        elif operation == "split_by_scenes":
            return self._split_by_scenes(params, input_video, output_video)
        
        else:
            raise ExecutionError(f"不支持的操作类型: {operation}")
    
    def _normalize_path(self, path: str) -> str:
        """标准化路径格式"""
        return path.replace('\\', '/')
    
    def _build_command(
        self, 
        input_video: str, 
        output_video: str, 
        extra_args: list[str],
    ) -> list[str]:
        """构建 FFmpeg 命令"""
        cmd = [
            self.ffmpeg_path,
            "-i", input_video,  # 输入文件
            "-y",  # 覆盖输出文件
            *extra_args,  # 其他参数
            output_video  # 输出文件
        ]
        return cmd
    
    def _run_ffmpeg(self, cmd: list[str]) -> tuple[bool, str]:
        """
        运行 FFmpeg 命令
        
        Args:
            cmd: FFmpeg 命令列表
            
        Returns:
            (是否成功, 输出信息)
        """
        self.last_command = " ".join(cmd)
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            self.last_output = result.stderr
            
            if result.returncode == 0:
                return True, "成功"
            else:
                error_msg = result.stderr.split("\n")[-3] if result.stderr else "未知错误"
                return False, error_msg
                
        except Exception as e:
            return False, str(e)
    
    def get_video_duration(self, video_path: str) -> Optional[float]:
        """
        获取视频时长（秒）
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            时长（秒），失败返回 None
        """
        cmd = [
            self.ffmpeg_path,
            "-i", video_path
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                timeout=30
            )
            
            # 从输出中提取时长
            # 格式: Duration: 00:01:30.50
            match = re.search(
                r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})',
                result.stderr
            )
            
            if match:
                hours = int(match.group(1))
                minutes = int(match.group(2))
                seconds = int(match.group(3))
                centiseconds = int(match.group(4))
                return hours * 3600 + minutes * 60 + seconds + centiseconds / 100
            
            return None
            
        except Exception:
            return None
    
    def _trim_start(
        self, 
        params: dict[str, Any], 
        input_video: str, 
        output_video: str,
        total_duration: float,
    ) -> bool:
        """
        删除视频开头部分
        
        Args:
            params: 参数 (start_time)
            input_video: 输入视频
            output_video: 输出视频
            total_duration: 视频总时长
        """
        start_time = params["start_time"]
        
        # 构建命令：从 start_time 开始到结束
        cmd = self._build_command(
            input_video,
            output_video,
            [
                "-ss", str(start_time),  # 起始时间
                "-c", "copy",  # 快速复制（不重新编码）
            ]
        )
        
        success, message = self._run_ffmpeg(cmd)
        
        if not success:
            # 尝试不用 -c copy（更慢但更稳定）
            cmd = self._build_command(
                input_video,
                output_video,
                ["-ss", str(start_time)]
            )
            success, message = self._run_ffmpeg(cmd)
        
        return success
    
    def _trim_end(
        self, 
        params: dict[str, Any], 
        input_video: str, 
        output_video: str,
        total_duration: float,
    ) -> bool:
        """
        删除视频结尾部分
        
        Args:
            params: 参数 trim_seconds (int): 要删除的秒数。
                    兼容旧参数名 end_time。
        """
        # trim_seconds: how many seconds to remove from the end
        trim_seconds = params.get("trim_seconds", params.get("end_time", 0))
        
        # 计算实际结束时间
        actual_end = total_duration - trim_seconds
        
        if actual_end <= 0:
            raise ExecutionError("删除时长不能超过视频总时长")
        
        # 构建命令：从 0 到 actual_end
        cmd = self._build_command(
            input_video,
            output_video,
            [
                "-to", str(actual_end),  # 结束时间
                "-c", "copy",  # 快速复制
            ]
        )
        
        success, message = self._run_ffmpeg(cmd)
        
        if not success:
            # 尝试不用 -c copy
            cmd = self._build_command(
                input_video,
                output_video,
                ["-to", str(actual_end)]
            )
            success, message = self._run_ffmpeg(cmd)
        
        return success
    
    def _trim_range(
        self, 
        params: Dict[str, Any], 
        input_video: str, 
        output_video: str
    ) -> bool:
        """
        截取视频片段
        
        Args:
            params: 参数 (start_time, end_time)
            input_video: 输入视频
            output_video: 输出视频
        """
        start_time = params["start_time"]
        end_time = params["end_time"]
        
        if start_time >= end_time:
            raise ExecutionError("开始时间必须小于结束时间")
        
        # 构建命令：从 start_time 到 end_time
        cmd = self._build_command(
            input_video,
            output_video,
            [
                "-ss", str(start_time),  # 起始时间
                "-to", str(end_time),  # 结束时间
                "-c", "copy",  # 快速复制
            ]
        )
        
        success, message = self._run_ffmpeg(cmd)
        
        if not success:
            # 尝试不用 -c copy
            cmd = self._build_command(
                input_video,
                output_video,
                ["-ss", str(start_time), "-to", str(end_time)]
            )
            success, message = self._run_ffmpeg(cmd)
        
        return success
    
    def _trim_segments(
        self, 
        segments: List[Tuple[float, float]], 
        input_video: str, 
        output_video: str
    ) -> bool:
        """
        多段截取并合并
        
        Args:
            segments: 时间段列表 [(start1, end1), (start2, end2), ...]
            input_video: 输入视频
            output_video: 输出视频
        """
        import os
        import tempfile
        
        if not segments:
            raise ExecutionError("没有指定要截取的时间段")
        
        # 验证时间段
        for i, (start, end) in enumerate(segments):
            if start >= end:
                raise ExecutionError(f"时间段 {i+1}: 开始时间必须小于结束时间")
        
        # 如果只有一段，直接截取
        if len(segments) == 1:
            start, end = segments[0]
            return self._trim_range(
                {"start_time": start, "end_time": end},
                input_video,
                output_video
            )
        
        # 多段：先截取各片段，再合并
        temp_dir = tempfile.mkdtemp(prefix="video_edit_")
        temp_files = []
        
        try:
            # 1. 截取各片段
            for i, (start, end) in enumerate(segments):
                temp_file = os.path.join(temp_dir, f"segment_{i}.mp4")
                temp_files.append(temp_file)
                
                # 截取片段
                cmd = self._build_command(
                    input_video,
                    temp_file,
                    ["-ss", str(start), "-to", str(end)]
                )
                success, msg = self._run_ffmpeg(cmd)
                if not success:
                    raise ExecutionError(f"截取片段 {i+1} 失败: {msg}")
            
            # 2. 创建合并文件列表
            concat_list_file = os.path.join(temp_dir, "concat_list.txt")
            with open(concat_list_file, 'w', encoding='utf-8') as f:
                for temp_file in temp_files:
                    f.write(f"file '{self._normalize_path(temp_file)}'\n")
            
            # 3. 合并片段
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", concat_list_file,
                "-c", "copy",  # 直接复制，不重新编码
                "-y",
                output_video
            ]
            
            success, msg = self._run_ffmpeg(cmd)
            
            if not success:
                # 尝试重新编码合并
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", concat_list_file,
                    "-y",
                    output_video
                ]
                success, msg = self._run_ffmpeg(cmd)
                if not success:
                    raise ExecutionError(f"合并片段失败: {msg}")
            
            return True
            
        finally:
            # 清理临时文件
            for temp_file in temp_files:
                if os.path.exists(temp_file):
                    try:
                        os.remove(temp_file)
                    except:
                        pass
            
            # 删除临时目录
            try:
                os.rmdir(temp_dir)
            except:
                pass
    
    def _concat(
        self, 
        params: dict[str, Any], 
        input_video: str, 
        output_video: str,
    ) -> bool:
        """
        合并多个视频
        
        Args:
            params: 参数 (files)
            input_video: 主输入视频（会被 params["files"] 替代）
            output_video: 输出视频
        """
        files = params["files"]
        
        if len(files) < 2:
            raise ExecutionError("合并操作至少需要两个视频文件")
        
        # Use tempfile for the concat list (concurrency-safe)
        fd, temp_list_file = tempfile.mkstemp(suffix=".txt", prefix="concat_")
        os.close(fd)
        
        try:
            # 写入文件列表
            with open(temp_list_file, 'w', encoding='utf-8') as f:
                for file in files:
                    file = self._normalize_path(file)
                    f.write(f"file '{file}'\n")
            
            # 构建命令：使用 concat demuxer
            cmd = [
                self.ffmpeg_path,
                "-f", "concat",
                "-safe", "0",
                "-i", temp_list_file,
                "-c", "copy",
                "-y",
                output_video
            ]
            
            self.last_command = " ".join(cmd)
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace'
            )
            
            if result.returncode != 0:
                # 如果 concat demuxer 失败，尝试重新编码
                cmd = [
                    self.ffmpeg_path,
                    "-f", "concat",
                    "-safe", "0",
                    "-i", temp_list_file,
                    "-y",
                    output_video
                ]
                success, message = self._run_ffmpeg(cmd)
                return success
            
            return True
            
        finally:
            if os.path.exists(temp_list_file):
                os.remove(temp_list_file)
    
    def _convert(
        self, 
        params: Dict[str, Any], 
        input_video: str, 
        output_video: str
    ) -> bool:
        """
        转换视频分辨率
        
        Args:
            params: 参数 (width, height)
            input_video: 输入视频
            output_video: 输出视频
        """
        width = params["width"]
        height = params["height"]
        
        # 构建命令：改变分辨率
        cmd = self._build_command(
            input_video,
            output_video,
            [
                "-vf", f"scale={width}:{height}",
                "-c:a", "copy",  # 音频直接复制
            ]
        )
        
        success, message = self._run_ffmpeg(cmd)
        return success
    
    def _remove_silence(
        self, 
        params: Dict[str, Any], 
        input_video: str, 
        output_video: str
    ) -> bool:
        """
        删除静音段
        
        使用 FFmpeg silencedetect 检测静音段时间，
        再用 trim 截取非静音段，最后合并。
        
        Args:
            params: 参数 (threshold，单位 dB)
            input_video: 输入视频
            output_video: 输出视频
        """
        import tempfile
        
        threshold = params.get("threshold", -40)  # dB 值，如 -40
        
        # Step 1: 用 silencedetect 检测静音段时间
        cmd_detect = [
            self.ffmpeg_path,
            "-i", input_video,
            "-af", f"silencedetect=noise={threshold}dB:d=0.05",
            "-f", "null", "-"
        ]
        
        result = subprocess.run(
            cmd_detect,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',
            timeout=120
        )
        
        # 解析 silencedetect 输出，找出静音段时间
        silent_ranges = []  # [(start, end), ...]
        for line in result.stderr.split("\n"):
            if "silence_start:" in line:
                start = float(line.split("silence_start:")[1].strip())
                silent_ranges.append({"start": start, "end": None})
            elif "silence_end:" in line and silent_ranges:
                parts = line.split("silence_end:")[1].strip().split("|")[0].strip()
                end = float(parts)
                silent_ranges[-1]["end"] = end
        
        # 没有检测到静音，直接复制
        if not silent_ranges:
            cmd = self._build_command(
                input_video,
                output_video,
                ["-c", "copy"]
            )
            return self._run_ffmpeg(cmd)[0]
        
        # Step 2: 获取视频总时长
        duration = self.get_video_duration(input_video)
        
        # Step 3: 计算保留的非静音段
        keep_segments = []
        prev_end = 0.0
        for sr in silent_ranges:
            if sr["end"] is not None:
                if prev_end < sr["start"]:
                    keep_segments.append((prev_end, sr["start"]))
                prev_end = sr["end"]
        
        # 末尾的非静音段
        if prev_end < duration:
            keep_segments.append((prev_end, duration))
        
        # 没有可保留的段
        if not keep_segments:
            raise ExecutionError("整个视频都是静音，无法处理")
        
        # Step 4: 单段直接截取
        if len(keep_segments) == 1:
            start, end = keep_segments[0]
            cmd = self._build_command(
                input_video,
                output_video,
                ["-ss", str(start), "-to", str(end)]
            )
            return self._run_ffmpeg(cmd)[0]
        
        # Step 5: 多段截取并合并
        return self._trim_segments(keep_segments, input_video, output_video)
    
    def _remove_static(
        self,
        params: Dict[str, Any],
        input_video: str,
        output_video: str,
    ) -> bool:
        """Remove static (frozen-frame) segments using OpenCV frame-diff analysis.

        Args:
            params: Optional keys:
                - threshold (float): per-pixel diff threshold 0–1, default 0.01
                - min_static_duration (float): min seconds to count as static, default 1.0
            input_video:  Source video path.
            output_video: Destination video path.
        """
        from modules.analyzer import Analyzer, AnalyzerError

        threshold = params.get("threshold", 0.01)
        min_static_duration = params.get("min_static_duration", 1.0)

        analyzer = Analyzer(ffmpeg_path=self.ffmpeg_path)

        try:
            static_segments = analyzer.detect_static_segments(
                input_video,
                threshold=threshold,
                min_static_duration=min_static_duration,
            )
        except AnalyzerError as e:
            raise ExecutionError(f"Static segment detection failed: {e}") from e

        if not static_segments:
            # No static segments — copy as-is
            cmd = self._build_command(input_video, output_video, ["-c", "copy"])
            return self._run_ffmpeg(cmd)[0]

        # Build keep-segments (inverse of static_segments)
        duration = self.get_video_duration(input_video)
        if duration is None:
            raise ExecutionError(f"Cannot read duration: {input_video}")

        keep_segments: list[tuple[float, float]] = []
        prev_end = 0.0
        for start, end in sorted(static_segments):
            if prev_end < start:
                keep_segments.append((prev_end, start))
            prev_end = end
        if prev_end < duration:
            keep_segments.append((prev_end, duration))

        if not keep_segments:
            raise ExecutionError("Entire video is static — nothing to keep.")

        if len(keep_segments) == 1:
            s, e = keep_segments[0]
            cmd = self._build_command(
                input_video, output_video,
                ["-ss", str(s), "-to", str(e), "-c", "copy"],
            )
            success, _ = self._run_ffmpeg(cmd)
            return success

        return self._trim_segments(keep_segments, input_video, output_video)

    def _split_by_scenes(
        self,
        params: Dict[str, Any],
        input_video: str,
        output_video: str,
    ) -> bool:
        """Split video into scene clips.

        Args:
            params: Optional keys:
                - threshold (float): scene-detection sensitivity, default 0.4 (0–1, lower=more sensitive)
                - min_scene_duration (float): minimum scene length in seconds, default 1.0
            input_video:  Source video path.
            output_video: Destination directory path (will be created if missing).

        Returns:
            True on success.

        Raises:
            ExecutionError: If detection or any FFmpeg split step fails.
        """
        from modules.analyzer import Analyzer, AnalyzerError

        threshold = params.get("threshold", 0.4)
        min_scene_duration = params.get("min_scene_duration", 1.0)

        # Resolve output directory: output_video is the directory path here
        output_dir = self._normalize_path(output_video)
        os.makedirs(output_dir, exist_ok=True)

        # Step 1: detect scenes
        analyzer = Analyzer(ffmpeg_path=self.ffmpeg_path)
        try:
            scenes = analyzer.detect_scenes(
                input_video,
                threshold=threshold,
                min_scene_duration=min_scene_duration,
            )
        except AnalyzerError as e:
            raise ExecutionError(f"Scene detection failed: {e}") from e

        if not scenes:
            raise ExecutionError("No scenes detected in this video.")

        # Step 2: split each scene into a separate file
        for scene in scenes:
            start = scene["start"]
            duration = scene["duration"]
            filename = f"scene_{scene['index']:03d}.mp4"
            scene_path = os.path.join(output_dir, filename)

            cmd = [
                self.ffmpeg_path, "-y",
                "-ss", str(start),
                "-i", input_video,
                "-t", str(duration),
                "-c", "copy",
                scene_path,
            ]

            success, err = self._run_ffmpeg(cmd)
            if not success:
                raise ExecutionError(
                    f"Failed to extract scene {scene['index']} ({start}s–{start+duration}s): {err}"
                )

        return True

    def burn_subtitle(
        self,
        params: Dict[str, Any],
        input_video: str,
        output_video: str,
    ) -> bool:
        """Burn subtitles into video using FFmpeg.

        Args:
            params: {
                "srt_file": str,  # Path to SRT file
                "style": dict,    # Optional style config
            }
            input_video: Source video path.
            output_video: Output video path with subtitles.

        Returns:
            True on success.

        Raises:
            ExecutionError: If FFmpeg fails.
        """
        from modules.analyzer import Analyzer

        srt_file = params.get("srt_file")
        if not srt_file or not os.path.exists(srt_file):
            raise ExecutionError(f"SRT file not found: {srt_file}")

        # Get style from params or use default
        style_config = params.get("style", {})
        analyzer = Analyzer(ffmpeg_path=self.ffmpeg_path)
        style_str = analyzer.format_subtitle_style(style_config)

        # Build FFmpeg command with subtitles filter
        # Use subtitles filter with force_style for customization
        cmd = [
            self.ffmpeg_path, "-y",
            "-i", input_video,
            "-vf", f"subtitles={srt_file.replace(':', '\\:')}:{style_str}",
            "-c:a", "copy",  # Copy audio without re-encoding
            output_video,
        ]

        success, err = self._run_ffmpeg(cmd)
        if not success:
            raise ExecutionError(f"Failed to burn subtitles: {err}")

        return True


# 测试代码
if __name__ == "__main__":
    executor = Executor()
    
    print("=" * 50)
    print("Executor 模块测试")
    print("=" * 50)
    
    # 测试获取视频信息
    print("\nFFmpeg 路径:", executor.ffmpeg_path)
    print("模块已加载成功")
    
    print("\n支持的指令类型:")
    print("  - trim_start: 删除视频开头部分")
    print("  - trim_end: 删除视频结尾部分")
    print("  - trim_range: 截取视频片段")
    print("  - concat: 合并多个视频")
    print("  - convert: 改变分辨率")
    print("  - remove_silence: 删除静音段")
    
    print("\n" + "=" * 50)
