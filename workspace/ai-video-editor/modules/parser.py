"""
Parser 模块 - 需求解析
将用户的自然语言指令转换为结构化指令
"""

import re
from typing import Dict, Any, List, Tuple, Optional


class ParseError(Exception):
    """解析错误异常"""
    pass


class Parser:
    """
    需求解析器
    将自然语言指令解析为结构化指令
    """
    
    # 动作关键词映射
    OPERATION_KEYWORDS = {
        "删除": ["trim_start", "trim_end"],
        "保留": ["trim_range"],
        "合并": ["concat"],
        "转换": ["convert"],
        "静音": ["remove_silence"],
    }
    
    # 时间单位转换
    TIME_UNITS = {
        "秒": 1,
        "分": 60,
        "分钟": 60,
        "时": 3600,
        "小时": 3600,
    }
    
    # 常见分辨率
    RESOLUTION_MAP = {
        "4k": (3840, 2160),
        "1080p": (1920, 1080),
        "720p": (1280, 720),
        "480p": (854, 480),
        "360p": (640, 360),
    }
    
    def __init__(self):
        """初始化解析器"""
        self.last_error = None
    
    def parse(self, instruction: str) -> Dict[str, Any]:
        """
        解析用户指令
        
        Args:
            instruction: 用户的自然语言指令
            
        Returns:
            结构化指令字典
            
        Raises:
            ParseError: 无法解析指令
        """
        instruction = instruction.strip()
        if not instruction:
            raise ParseError("指令不能为空")
        
        # 分词
        words = self.tokenize(instruction)
        
        # 识别操作类型
        operation = self.identify_operation(words, instruction)
        
        # 根据操作类型提取参数
        params = self.extract_params(words, instruction, operation)
        
        return {
            "operation": operation,
            "params": params,
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        分词：将文本拆分为词语列表
        
        Args:
            text: 输入文本
            
        Returns:
            词语列表
        """
        # 移除多余空格，保留标点
        text = re.sub(r'\s+', '', text)
        
        # 按常见分隔符分割
        # 包括：逗号、顿号、顿号、引号、括号等
        text = re.sub(r'[，、；：""''（）【】]', ' ', text)
        
        # 用空格分割
        words = text.split()
        
        return words
    
    def identify_operation(self, words: List[str], original_text: str) -> str:
        """
        识别操作类型
        
        Args:
            words: 分词后的词语列表
            original_text: 原始文本
            
        Returns:
            操作类型字符串
            
        Raises:
            ParseError: 无法识别操作类型
        """
        text = original_text
        
        # 检测操作类型
        if "删除" in text and "前" in text:
            return "trim_start"
        
        if "删除" in text and ("最后" in text or "结尾" in text or "末尾" in text):
            return "trim_end"
        
        if "保留" in text and "到" in text:
            return "trim_range"
        
        if "合并" in text or "拼接" in text:
            return "concat"
        
        if "转换" in text or "转为" in text:
            return "convert"
        
        if "静音" in text or "无声" in text:
            return "remove_silence"
        
        # 无法识别
        self.last_error = f"无法理解指令：'{text}'"
        raise ParseError(
            f"无法理解指令：'{text}'\n"
            f"支持的指令类型：\n"
            f"  - 删除前 X 秒\n"
            f"  - 删除最后 X 秒\n"
            f"  - 只保留 X 到 Y\n"
            f"  - 合并 视频1 和 视频2\n"
            f"  - 转换为 1080p\n"
            f"  - 删除静音段"
        )
    
    def extract_params(
        self, 
        words: List[str], 
        original_text: str,
        operation: str
    ) -> Dict[str, Any]:
        """
        提取参数
        
        Args:
            words: 分词后的词语列表
            original_text: 原始文本
            operation: 操作类型
            
        Returns:
            参数字典
        """
        params = {}
        
        if operation == "trim_start":
            # 删除前 X 秒
            time_value = self._extract_time_value(original_text)
            if time_value is None:
                raise ParseError("未找到时间值，请说 '删除前 10 秒' 这样的格式")
            params["start_time"] = time_value
            
        elif operation == "trim_end":
            # 删除最后 X 秒
            time_value = self._extract_time_value(original_text)
            if time_value is None:
                raise ParseError("未找到时间值，请说 '删除最后 10 秒' 这样的格式")
            params["end_time"] = time_value
            
        elif operation == "trim_range":
            # 只保留 X 到 Y（支持多段）
            segments = self._extract_multiple_ranges(original_text)
            if not segments:
                raise ParseError(
                    "未找到时间范围，请说 '只保留 1:00 到 3:00' 这样的格式"
                )
            if len(segments) == 1:
                # 单段：保持兼容
                params["start_time"] = segments[0][0]
                params["end_time"] = segments[0][1]
            else:
                # 多段：使用 segments 列表
                params["segments"] = segments
            
        elif operation == "concat":
            # 合并视频
            files = self._extract_file_names(original_text)
            if len(files) < 2:
                raise ParseError("至少需要两个视频文件才能合并")
            params["files"] = files
            
        elif operation == "convert":
            # 转换分辨率
            resolution = self._extract_resolution(original_text)
            if resolution is None:
                # 默认转换为 1080p
                resolution = (1920, 1080)
            params["width"] = resolution[0]
            params["height"] = resolution[1]
            
        elif operation == "remove_silence":
            # 删除静音段（暂无额外参数）
            params["threshold"] = -40  # 默认阈值 -40dB
        
        return params
    
    def _extract_time_value(self, text: str) -> Optional[float]:
        """
        从文本中提取时间值（秒）
        
        支持格式：
        - "10 秒" -> 10
        - "1分30秒" -> 90
        - "1:30" -> 90
        - "1:00:00" -> 3600
        """
        # 格式: HH:MM:SS 或 MM:SS
        match = re.search(r'(\d+):(\d{2})(?::(\d{2}))?', text)
        if match:
            groups = match.groups()
            if groups[2]:  # HH:MM:SS
                hours = int(groups[0])
                minutes = int(groups[1])
                seconds = int(groups[2])
                return hours * 3600 + minutes * 60 + seconds
            else:  # MM:SS
                minutes = int(groups[0])
                seconds = int(groups[1])
                return minutes * 60 + seconds
        
        # 格式: X分X秒 或 X秒
        match = re.search(r'(\d+)\s*分', text)
        minutes = int(match.group(1)) if match else 0
        
        match = re.search(r'(\d+)\s*秒', text)
        seconds = int(match.group(1)) if match else 0
        
        if minutes > 0 or seconds > 0:
            return minutes * 60 + seconds
        
        # 纯数字格式（默认秒）
        match = re.search(r'^(\d+)$', text.strip())
        if match:
            return float(match.group(1))
        
        return None
    
    def _extract_time_range(self, text: str) -> Optional[Tuple[float, float]]:
        """
        从文本中提取时间范围
        
        支持格式：
        - "1:00 到 3:00" -> (60, 180)
        - "1分 到 3分" -> (60, 180)
        """
        # 格式: HH:MM:SS 到 HH:MM:SS 或 MM:SS 到 MM:SS
        pattern = r'(\d+:?\d*:?\d*)\s*到\s*(\d+:?\d*:?\d*)'
        match = re.search(pattern, text)
        if match:
            start = self._extract_time_value(match.group(1))
            end = self._extract_time_value(match.group(2))
            if start is not None and end is not None:
                return (start, end)
        
        # 格式: X分 到 Y分
        pattern = r'(\d+)\s*分.*?(\d+)\s*分'
        match = re.search(pattern, text)
        if match:
            start = int(match.group(1)) * 60
            end = int(match.group(2)) * 60
            return (start, end)
        
        return None
    
    def _extract_file_names(self, text: str) -> List[str]:
        """
        从文本中提取文件名
        
        支持格式：
        - "合并 video1.mp4 和 video2.mp4"
        - "合并video1.mp4和video2.mp4"
        """
        # 移除"合并"、"和"、"与"等词
        text = re.sub(r'[合并和与]', ' ', text)
        
        # 提取常见的视频文件扩展名
        video_extensions = ['mp4', 'avi', 'mov', 'mkv', 'flv', 'wmv', 'webm']
        
        files = []
        for ext in video_extensions:
            pattern = rf'[^\s]+\.{ext}'
            matches = re.findall(pattern, text, re.IGNORECASE)
            files.extend(matches)
        
        return list(set(files))  # 去重
    
    def _extract_multiple_ranges(self, text: str) -> List[Tuple[float, float]]:
        """
        从文本中提取多个时间范围（支持多段截取）
        
        支持格式：
        - "0到10和30到50" -> [(0, 10), (30, 50)]
        - "0:00到0:10和0:30到0:50" -> [(0, 10), (30, 50)]
        - "0分到10分和30分到50分" -> [(0, 60), (30, 60)]
        """
        segments = []
        
        # 移除"只保留"等前缀
        text = re.sub(r'[只保留]', '', text)
        
        # 按"和"分割多个范围
        # 处理 "0到10和30到50" 格式
        parts = re.split(r'\s*和\s*', text)
        
        for part in parts:
            # 尝试匹配各种时间格式
            # 格式1: HH:MM:SS 到 HH:MM:SS
            match = re.search(r'(\d+):(\d{2}):(\d{2})\s*到\s*(\d+):(\d{2}):(\d{2})', part)
            if match:
                start = int(match.group(1)) * 3600 + int(match.group(2)) * 60 + int(match.group(3))
                end = int(match.group(4)) * 3600 + int(match.group(5)) * 60 + int(match.group(6))
                segments.append((start, end))
                continue
            
            # 格式2: MM:SS 到 MM:SS
            match = re.search(r'(\d+):(\d{2})\s*到\s*(\d+):(\d{2})', part)
            if match:
                start = int(match.group(1)) * 60 + int(match.group(2))
                end = int(match.group(3)) * 60 + int(match.group(4))
                segments.append((start, end))
                continue
            
            # 格式3: X分Y秒 到 Z分W秒
            match = re.search(r'(\d+)分(\d+)秒\s*到\s*(\d+)分(\d+)秒', part)
            if match:
                start = int(match.group(1)) * 60 + int(match.group(2))
                end = int(match.group(3)) * 60 + int(match.group(4))
                segments.append((start, end))
                continue
            
            # 格式4: X分 到 Y分
            match = re.search(r'(\d+)\s*分.*?(\d+)\s*分', part)
            if match:
                start = int(match.group(1)) * 60
                end = int(match.group(2)) * 60
                segments.append((start, end))
                continue
            
            # 格式5: X秒 到 Y秒
            match = re.search(r'(\d+)\s*秒.*?(\d+)\s*秒', part)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                segments.append((start, end))
                continue
            
            # 格式6: 纯数字到数字
            match = re.search(r'(\d+)\s*到\s*(\d+)', part)
            if match:
                start = int(match.group(1))
                end = int(match.group(2))
                segments.append((start, end))
        
        return segments
    
    def _extract_resolution(self, text: str) -> Optional[Tuple[int, int]]:
        """
        从文本中提取分辨率
        
        支持格式：
        - "1080p" -> (1920, 1080)
        - "720p" -> (1280, 720)
        - "4k" -> (3840, 2160)
        - "1920x1080" -> (1920, 1080)
        """
        text_lower = text.lower()
        
        # 检查预设分辨率
        for name, resolution in self.RESOLUTION_MAP.items():
            if name in text_lower:
                return resolution
        
        # 格式: WIDTHxHEIGHT
        match = re.search(r'(\d+)\s*[x×]\s*(\d+)', text)
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            return (width, height)
        
        return None
    
    def validate(self, instruction_dict: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """
        验证指令的合法性
        
        Args:
            instruction_dict: 结构化指令
            
        Returns:
            (是否合法, 错误信息)
        """
        if "operation" not in instruction_dict:
            return False, "缺少操作类型"
        
        if "params" not in instruction_dict:
            return False, "缺少参数"
        
        operation = instruction_dict["operation"]
        params = instruction_dict["params"]
        
        # 根据操作类型验证参数
        if operation == "trim_start":
            if "start_time" not in params:
                return False, "缺少 start_time 参数"
            if params["start_time"] < 0:
                return False, "start_time 必须大于等于 0"
                
        elif operation == "trim_end":
            if "end_time" not in params:
                return False, "缺少 end_time 参数"
            if params["end_time"] < 0:
                return False, "end_time 必须大于等于 0"
                
        elif operation == "trim_range":
            if "start_time" not in params or "end_time" not in params:
                return False, "缺少时间范围参数"
            if params["start_time"] >= params["end_time"]:
                return False, "开始时间必须小于结束时间"
                
        elif operation == "concat":
            if "files" not in params:
                return False, "缺少文件列表"
            if len(params["files"]) < 2:
                return False, "合并操作至少需要两个文件"
                
        elif operation == "convert":
            if "width" not in params or "height" not in params:
                return False, "缺少分辨率参数"
        
        elif operation == "remove_silence":
            if "threshold" not in params:
                params["threshold"] = -40  # 设置默认值
        
        return True, None


# 测试代码
if __name__ == "__main__":
    parser = Parser()
    
    test_cases = [
        "删除前 10 秒",
        "删除最后 5 秒",
        "只保留 1:00 到 3:00",
        "合并 video1.mp4 和 video2.mp4",
        "转换为 1080p",
        "删除静音段",
        "1分30秒到2分",
    ]
    
    print("=" * 50)
    print("Parser 模块测试")
    print("=" * 50)
    
    for test in test_cases:
        print(f"\n输入: {test}")
        try:
            result = parser.parse(test)
            print(f"输出: {result}")
        except ParseError as e:
            print(f"错误: {e}")
    
    print("\n" + "=" * 50)
