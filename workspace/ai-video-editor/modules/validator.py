"""
Validator 模块 - 视频验证器
检查输出视频是否正确生成
"""

from __future__ import annotations

import os
import re
import subprocess
from typing import Any, Optional


class ValidationError(Exception):
    """验证错误异常"""
    pass


class Validator:
    """
    视频验证器
    检查输出视频是否正确生成
    """
    
    def __init__(self, ffmpeg_path: str = "ffmpeg"):
        """
        初始化验证器
        
        Args:
            ffmpeg_path: FFmpeg 可执行文件路径
        """
        self.ffmpeg_path = ffmpeg_path
    
    def validate(
        self, 
        output_video: str,
        expected_duration: float | None = None,
        expected_resolution: tuple[int, int] | None = None,
        min_file_size: int = 1024,
    ) -> dict[str, Any]:
        """
        验证输出视频
        
        Args:
            output_video: 输出视频路径
            expected_duration: 预期时长（秒）
            expected_resolution: 预期分辨率 (width, height)
            min_file_size: 最小文件大小（字节）
            
        Returns:
            验证结果字典
            {
                "valid": bool,           # 是否通过验证
                "errors": List[str],     # 错误列表
                "warnings": List[str],   # 警告列表
                "metadata": {            # 视频元数据
                    "duration": float,  # 时长（秒）
                    "width": int,       # 宽度
                    "height": int,      # 高度
                    "file_size": int,   # 文件大小（字节）
                    "codec": str,       # 视频编码
                    "fps": float        # 帧率
                }
            }
        """
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "metadata": None
        }
        
        # 1. 检查文件是否存在
        if not os.path.exists(output_video):
            result["valid"] = False
            result["errors"].append(f"输出文件不存在: {output_video}")
            return result
        
        # 2. 检查文件大小
        file_size = os.path.getsize(output_video)
        result["metadata"] = {"file_size": file_size}
        
        if file_size < min_file_size:
            result["valid"] = False
            result["errors"].append(f"文件大小异常 ({file_size} 字节)，可能生成失败")
            return result
        
        if file_size < 1024 * 100:  # 小于 100KB
            result["warnings"].append(f"文件较小 ({file_size} 字节)，请确认输出正确")
        
        # 3. 获取视频元数据
        metadata = self.get_video_metadata(output_video)
        if metadata is None:
            result["valid"] = False
            result["errors"].append("无法读取视频信息，文件可能已损坏")
            return result
        
        result["metadata"].update(metadata)
        
        # 4. 验证时长
        if expected_duration is not None:
            actual_duration = metadata.get("duration", 0)
            
            # 允许 5% 的误差
            tolerance = expected_duration * 0.05
            
            if abs(actual_duration - expected_duration) > tolerance:
                result["valid"] = False
                result["errors"].append(
                    f"时长不符合预期: 预期 {expected_duration:.2f}秒, "
                    f"实际 {actual_duration:.2f}秒"
                )
        
        # 5. 验证分辨率
        if expected_resolution is not None:
            actual_resolution = (
                metadata.get("width", 0),
                metadata.get("height", 0)
            )
            
            if actual_resolution != expected_resolution:
                result["warnings"].append(
                    f"分辨率不符: 预期 {expected_resolution}, "
                    f"实际 {actual_resolution}"
                )
        
        # 6. 检查视频时长是否合理
        duration = metadata.get("duration", 0)
        if duration < 0.1:  # 少于 0.1 秒
            result["valid"] = False
            result["errors"].append("视频时长过短，可能是处理失败")
        
        return result
    
    def get_video_metadata(self, video_path: str) -> dict[str, Any] | None:
        """
        获取视频元数据
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            视频元数据字典，失败返回 None
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
            
            # 解析输出
            output = result.stderr
            
            metadata = {}
            
            # 提取时长
            # 格式: Duration: 00:01:30.50
            duration_match = re.search(
                r'Duration: (\d{2}):(\d{2}):(\d{2})\.(\d{2})',
                output
            )
            if duration_match:
                hours = int(duration_match.group(1))
                minutes = int(duration_match.group(2))
                seconds = int(duration_match.group(3))
                centiseconds = int(duration_match.group(4))
                metadata["duration"] = (
                    hours * 3600 + minutes * 60 + seconds + centiseconds / 100
                )
            
            # 提取视频流信息
            # Match: Stream #0:0: Video: h264, ... 1920x1080, ... 30 fps, 30 tbr
            # Also handles variable fps like: 90000/3002 tbr, 29.97 tbn, 29.97 tbc
            video_stream_match = re.search(
                r'Stream\s+#\d+:\d+.*?Video:\s*\w+.*?(\d{2,5})x(\d{2,5}).*?(\d+(?:\.\d+)?)\s*fps',
                output
            )
            
            if video_stream_match:
                metadata["width"] = int(video_stream_match.group(1))
                metadata["height"] = int(video_stream_match.group(2))
                metadata["fps"] = float(video_stream_match.group(3))
            else:
                # 备选方案：单独提取分辨率
                resolution_match = re.search(r'(\d{3,5})x(\d{3,5})', output)
                if resolution_match:
                    metadata["width"] = int(resolution_match.group(1))
                    metadata["height"] = int(resolution_match.group(2))
            
            # 提取编码格式
            codec_match = re.search(
                r'Stream.*Video:\s*(\w+)',
                output
            )
            if codec_match:
                metadata["codec"] = codec_match.group(1)
            
            # 提取比特率
            bitrate_match = re.search(
                r'bitrate:\s*(\d+\s*\w+/s)',
                output
            )
            if bitrate_match:
                metadata["bitrate"] = bitrate_match.group(1)
            
            return metadata if metadata else None
            
        except Exception as e:
            return None
    
    def is_valid_video(self, video_path: str) -> bool:
        """
        快速检查文件是否是有效的视频
        
        Args:
            video_path: 视频文件路径
            
        Returns:
            True 有效，False 无效
        """
        if not os.path.exists(video_path):
            return False
        
        # 检查文件大小
        if os.path.getsize(video_path) < 1024:
            return False
        
        # 检查是否能读取元数据
        metadata = self.get_video_metadata(video_path)
        return metadata is not None and metadata.get("duration", 0) > 0


# 测试代码
if __name__ == "__main__":
    validator = Validator()
    
    print("=" * 50)
    print("Validator 模块测试")
    print("=" * 50)
    
    print("\nFFmpeg 路径:", validator.ffmpeg_path)
    print("模块已加载成功")
    
    print("\n验证功能:")
    print("  - 文件存在性检查")
    print("  - 文件完整性检查")
    print("  - 视频时长验证")
    print("  - 分辨率验证")
    print("  - 视频元数据提取")
    
    print("\n" + "=" * 50)
