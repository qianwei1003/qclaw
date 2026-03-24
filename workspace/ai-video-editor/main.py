"""
AI 视频剪辑工具 - 主入口
整合 Parser、Executor、Validator，提供简单的使用接口
"""

import os
import sys
from typing import Dict, Any, List, Optional

# 添加 modules 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from modules.parser import Parser, ParseError
from modules.executor import Executor, ExecutionError
from modules.validator import Validator, ValidationError


class VideoEditorError(Exception):
    """视频编辑器错误基类"""
    pass


class VideoEditor:
    """
    AI 视频剪辑工具主类
    
    使用示例:
    
    ```python
    editor = VideoEditor()
    
    # 简单用法
    result = editor.edit(
        instruction="删除前 10 秒",
        input_video="input.mp4",
        output_video="output.mp4"
    )
    
    if result["success"]:
        print("剪辑成功!")
    else:
        print(f"失败: {result['errors']}")
    ```
    """
    
    def __init__(self):
        """初始化视频编辑器"""
        self.parser = Parser()
        self.executor = Executor()
        self.validator = Validator()
        
        # 记录历史
        self.history = []
    
    def edit(
        self, 
        instruction: str,
        input_video: str,
        output_video: str,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        执行视频剪辑
        
        Args:
            instruction: 用户的自然语言指令
            input_video: 输入视频路径
            output_video: 输出视频路径
            validate: 是否验证输出，默认 True
            
        Returns:
            执行结果字典
            {
                "success": bool,           # 是否成功
                "operation": str,          # 执行的操作
                "input_video": str,        # 输入文件
                "output_video": str,       # 输出文件
                "parsed_instruction": dict, # 解析后的指令
                "validation": dict,        # 验证结果
                "errors": List[str],       # 错误列表
                "execution_time": float    # 执行耗时（秒）
            }
        """
        import time
        start_time = time.time()
        
        result = {
            "success": False,
            "operation": None,
            "input_video": input_video,
            "output_video": output_video,
            "parsed_instruction": None,
            "validation": None,
            "errors": [],
            "execution_time": 0
        }
        
        # 1. 解析指令
        try:
            parsed = self.parser.parse(instruction)
            result["parsed_instruction"] = parsed
            result["operation"] = parsed["operation"]
            
        except ParseError as e:
            result["errors"].append(f"解析失败: {str(e)}")
            result["execution_time"] = time.time() - start_time
            self.history.append(result)
            return result
        
        # 2. 执行剪辑
        try:
            success = self.executor.execute(
                parsed, 
                input_video, 
                output_video
            )
            
            if not success:
                result["errors"].append("执行失败，FFmpeg 返回错误")
                result["execution_time"] = time.time() - start_time
                self.history.append(result)
                return result
                
        except ExecutionError as e:
            result["errors"].append(f"执行失败: {str(e)}")
            result["execution_time"] = time.time() - start_time
            self.history.append(result)
            return result
        
        # 3. 验证结果
        if validate:
            try:
                validation = self.validator.validate(output_video)
                result["validation"] = validation
                
                if not validation["valid"]:
                    result["errors"].extend(validation["errors"])
                    result["execution_time"] = time.time() - start_time
                    self.history.append(result)
                    return result
                    
            except Exception as e:
                result["errors"].append(f"验证失败: {str(e)}")
                result["execution_time"] = time.time() - start_time
                self.history.append(result)
                return result
        
        # 4. 成功
        result["success"] = True
        result["execution_time"] = time.time() - start_time
        self.history.append(result)
        return result
    
    def batch_edit(self, tasks: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        批量执行视频剪辑
        
        Args:
            tasks: 任务列表，每个任务包含:
                - instruction: 指令
                - input_video: 输入视频
                - output_video: 输出视频
                
        Returns:
            结果列表
        """
        results = []
        
        for i, task in enumerate(tasks):
            print(f"\n[{i+1}/{len(tasks)}] Processing: {task.get('input_video', 'unknown')}")
            
            result = self.edit(
                instruction=task["instruction"],
                input_video=task["input_video"],
                output_video=task["output_video"]
            )
            
            results.append(result)
            
            if result["success"]:
                print(f"  [OK] Success ({result['execution_time']:.2f}s)")
            else:
                print(f"  [FAIL] Failed: {result['errors']}")
        
        return results
    
    def get_history(self) -> List[Dict[str, Any]]:
        """获取执行历史"""
        return self.history
    
    def clear_history(self):
        """清空执行历史"""
        self.history = []


def main():
    """命令行入口"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="AI 视频剪辑工具 - 通过自然语言自动剪辑视频"
    )
    
    parser.add_argument(
        "instruction", 
        help="剪辑指令，如 '删除前 10 秒'"
    )
    
    parser.add_argument(
        "input_video",
        help="输入视频路径"
    )
    
    parser.add_argument(
        "output_video",
        help="输出视频路径"
    )
    
    parser.add_argument(
        "--no-validate",
        action="store_true",
        help="跳过验证"
    )
    
    args = parser.parse_args()
    
    # 创建编辑器
    editor = VideoEditor()
    
    # 执行剪辑
    print(f"\n[INPUT] {args.input_video}")
    print(f"[CMD] {args.instruction}")
    print(f"[OUTPUT] {args.output_video}\n")
    
    result = editor.edit(
        instruction=args.instruction,
        input_video=args.input_video,
        output_video=args.output_video,
        validate=not args.no_validate
    )
    
    # 输出结果
    if result["success"]:
        print(f"\n[OK] Clip success! ({result['execution_time']:.2f}s)")
        
        if result.get("validation"):
            metadata = result["validation"].get("metadata", {})
            if metadata:
                print(f"\n[INFO] Output video info:")
                duration = metadata.get('duration', 'N/A')
                if isinstance(duration, (int, float)):
                    print(f"   - Duration: {duration:.2f}s")
                else:
                    print(f"   - Duration: {duration}")
                print(f"   - Resolution: {metadata.get('width', 'N/A')}x{metadata.get('height', 'N/A')}")
                print(f"   - File size: {metadata.get('file_size', 0) / 1024 / 1024:.2f} MB")
    else:
        print(f"\n[ERROR] Clip failed:")
        for error in result["errors"]:
            print(f"   - {error}")
        
        sys.exit(1)


if __name__ == "__main__":
    main()
