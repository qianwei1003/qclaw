# 错误处理规范

## 1. 错误分类

### 1.1 错误类型层次

```
BaseError
├── UserError (用户错误)
│   ├── FileNotFoundError
│   ├── InvalidFormatError
│   ├── InvalidParameterError
│   └── PermissionError
│
├── ProcessingError (处理错误)
│   ├── AnalysisError
│   ├── EditError
│   ├── ExportError
│   └── SubtitleError
│
├── SystemError (系统错误)
│   ├── OutOfMemoryError
│   ├── DiskFullError
│   ├── DependencyError
│   └── TimeoutError
│
└── RecoverableError (可恢复错误)
    ├── NetworkError
    └── ResourceBusyError
```

---

## 2. 错误码定义

### 2.1 错误码范围

| 范围 | 类型 | 说明 |
|------|------|------|
| 1000-1999 | 用户错误 | 用户可解决的问题 |
| 2000-2999 | 处理错误 | 处理过程中的错误 |
| 3000-3999 | 系统错误 | 系统资源问题 |
| 4000-4999 | 可恢复错误 | 可重试的错误 |

### 2.2 详细错误码

```python
# errors.py

class ErrorCode:
    # 用户错误 (1000-1999)
    FILE_NOT_FOUND = 1001
    INVALID_FORMAT = 1002
    FILE_TOO_LARGE = 1003
    FILE_CORRUPTED = 1004
    INVALID_PARAMETER = 1005
    PERMISSION_DENIED = 1006
    UNSUPPORTED_CODEC = 1007
    
    # 处理错误 (2000-2999)
    ANALYSIS_FAILED = 2001
    AUDIO_EXTRACTION_FAILED = 2002
    EDIT_FAILED = 2003
    EXPORT_FAILED = 2004
    SUBTITLE_GENERATION_FAILED = 2005
    NO_AUDIO_TRACK = 2006
    NO_VIDEO_TRACK = 2007
    
    # 系统错误 (3000-3999)
    OUT_OF_MEMORY = 3001
    DISK_FULL = 3002
    FFMPEG_NOT_FOUND = 3003
    TEMP_DIR_ERROR = 3004
    PROCESS_TIMEOUT = 3005
    
    # 可恢复错误 (4000-4999)
    NETWORK_ERROR = 4001
    RESOURCE_BUSY = 4002
    RATE_LIMIT = 4003
```

---

## 3. 异常类定义

```python
# exceptions.py

class VideoEditorError(Exception):
    """基础异常类"""
    
    def __init__(self, code: int, message: str, details: dict = None):
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(self.message)
    
    def to_dict(self) -> dict:
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details
        }


class UserError(VideoEditorError):
    """用户错误"""
    pass


class FileNotFoundError(UserError):
    """文件不存在"""
    
    def __init__(self, path: str):
        super().__init__(
            code=ErrorCode.FILE_NOT_FOUND,
            message=f"文件不存在: {path}",
            details={"path": path}
        )


class InvalidFormatError(UserError):
    """格式无效"""
    
    def __init__(self, path: str, expected: list):
        super().__init__(
            code=ErrorCode.INVALID_FORMAT,
            message=f"文件格式不支持，支持: {', '.join(expected)}",
            details={"path": path, "expected": expected}
        )


class ProcessingError(VideoEditorError):
    """处理错误"""
    pass


class AnalysisError(ProcessingError):
    """分析错误"""
    
    def __init__(self, reason: str, video_path: str = None):
        super().__init__(
            code=ErrorCode.ANALYSIS_FAILED,
            message=f"视频分析失败: {reason}",
            details={"reason": reason, "video_path": video_path}
        )


class SystemError(VideoEditorError):
    """系统错误"""
    pass


class OutOfMemoryError(SystemError):
    """内存不足"""
    
    def __init__(self, required_mb: int, available_mb: int):
        super().__init__(
            code=ErrorCode.OUT_OF_MEMORY,
            message=f"内存不足: 需要 {required_mb}MB，可用 {available_mb}MB",
            details={"required_mb": required_mb, "available_mb": available_mb}
        )


class RecoverableError(VideoEditorError):
    """可恢复错误"""
    
    def __init__(self, code: int, message: str, retry_after: int = None):
        self.retry_after = retry_after
        super().__init__(code, message)
```

---

## 4. 错误处理策略

### 4.1 处理流程

```python
def handle_error(error: Exception) -> dict:
    """统一错误处理"""
    
    if isinstance(error, RecoverableError):
        # 可恢复错误：自动重试
        return handle_recoverable(error)
    
    elif isinstance(error, UserError):
        # 用户错误：返回友好提示
        return handle_user_error(error)
    
    elif isinstance(error, SystemError):
        # 系统错误：记录日志，清理资源
        return handle_system_error(error)
    
    elif isinstance(error, ProcessingError):
        # 处理错误：尝试恢复或报告
        return handle_processing_error(error)
    
    else:
        # 未知错误：记录详细信息
        return handle_unknown_error(error)
```

### 4.2 可恢复错误处理

```python
def handle_recoverable(error: RecoverableError, max_retries: int = 3):
    """处理可恢复错误"""
    
    for attempt in range(max_retries):
        wait_time = error.retry_after or (2 ** attempt)
        
        logger.warning(f"可恢复错误，{wait_time}秒后重试 ({attempt+1}/{max_retries})")
        time.sleep(wait_time)
        
        try:
            # 重试操作
            return retry_operation()
        except RecoverableError as e:
            continue
        except Exception as e:
            raise e
    
    # 重试次数用尽
    raise ProcessingError(
        code=ErrorCode.PROCESS_TIMEOUT,
        message="操作超时，请稍后重试"
    )
```

### 4.3 用户错误处理

```python
def handle_user_error(error: UserError) -> dict:
    """处理用户错误"""
    
    user_messages = {
        ErrorCode.FILE_NOT_FOUND: "请检查文件路径是否正确",
        ErrorCode.INVALID_FORMAT: "请使用支持的视频格式：MP4, MOV, AVI",
        ErrorCode.FILE_TOO_LARGE: "文件过大，请分割后处理",
        ErrorCode.PERMISSION_DENIED: "没有文件访问权限",
    }
    
    return {
        "success": False,
        "error": {
            "code": error.code,
            "message": error.message,
            "suggestion": user_messages.get(error.code, "请检查输入参数")
        }
    }
```

---

## 5. 日志记录规范

### 5.1 日志级别

| 级别 | 用途 | 示例 |
|------|------|------|
| DEBUG | 详细调试信息 | 变量值、函数调用 |
| INFO | 正常流程信息 | 开始处理、完成阶段 |
| WARNING | 警告但不影响运行 | 配置使用默认值、跳过可选功能 |
| ERROR | 错误但可继续 | 单个文件处理失败 |
| CRITICAL | 严重错误需停止 | 内存溢出、磁盘满 |

### 5.2 日志格式

```python
# logging_config.py

LOG_FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

def setup_logging(log_file: str = None, level: str = "INFO"):
    """配置日志"""
    
    handlers = [logging.StreamHandler()]
    
    if log_file:
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=getattr(logging, level),
        format=LOG_FORMAT,
        datefmt=LOG_DATE_FORMAT,
        handlers=handlers
    )
```

### 5.3 日志记录示例

```python
import logging

logger = logging.getLogger(__name__)

def process_video(video_path: str):
    """处理视频"""
    
    logger.info(f"开始处理视频: {video_path}")
    
    try:
        # 分析
        logger.debug("开始视频分析")
        analysis = analyze(video_path)
        logger.info(f"分析完成: 检测到 {len(analysis.silent_segments)} 个静音片段")
        
        # 剪辑
        logger.debug("开始视频剪辑")
        result = edit(video_path, analysis)
        logger.info(f"剪辑完成: 输出 {result.output_path}")
        
    except FileNotFoundError as e:
        logger.error(f"文件不存在: {e.details['path']}")
        raise
    
    except Exception as e:
        logger.exception(f"处理失败: {str(e)}")
        raise
```

---

## 6. 错误恢复策略

### 6.1 检查点机制

```python
class Checkpoint:
    """处理检查点"""
    
    def __init__(self, work_dir: str):
        self.checkpoint_file = os.path.join(work_dir, ".checkpoint")
    
    def save(self, stage: str, data: dict):
        """保存检查点"""
        checkpoint = {
            "stage": stage,
            "timestamp": time.time(),
            "data": data
        }
        with open(self.checkpoint_file, 'w') as f:
            json.dump(checkpoint, f)
    
    def load(self) -> dict:
        """加载检查点"""
        if os.path.exists(self.checkpoint_file):
            with open(self.checkpoint_file, 'r') as f:
                return json.load(f)
        return None
    
    def clear(self):
        """清除检查点"""
        if os.path.exists(self.checkpoint_file):
            os.remove(self.checkpoint_file)
```

### 6.2 恢复流程

```python
def resume_from_checkpoint(checkpoint: dict):
    """从检查点恢复"""
    
    stage = checkpoint["stage"]
    data = checkpoint["data"]
    
    logger.info(f"从检查点恢复: {stage}")
    
    if stage == "analysis_complete":
        # 分析已完成，直接开始剪辑
        return resume_editing(data)
    
    elif stage == "edit_complete":
        # 剪辑已完成，直接开始导出
        return resume_export(data)
    
    else:
        # 无法恢复，重新开始
        logger.warning("无法从检查点恢复，重新开始处理")
        return start_fresh()
```

---

## 7. 用户提示信息

### 7.1 错误提示模板

```python
ERROR_MESSAGES = {
    ErrorCode.FILE_NOT_FOUND: """
文件不存在: {path}

请检查：
1. 文件路径是否正确
2. 文件是否已被移动或删除
3. 是否有文件访问权限
    """,
    
    ErrorCode.INVALID_FORMAT: """
不支持的视频格式: {format}

支持的格式：
- MP4 (推荐)
- MOV
- AVI
- MKV
- WebM

建议使用 FFmpeg 转换格式：
ffmpeg -i input.{format} output.mp4
    """,
    
    ErrorCode.OUT_OF_MEMORY: """
内存不足

建议：
1. 关闭其他程序释放内存
2. 处理较小的视频片段
3. 降低处理质量设置
    """,
    
    ErrorCode.FFMPEG_NOT_FOUND: """
未找到 FFmpeg

请安装 FFmpeg：
- Windows: 下载 https://ffmpeg.org/download.html
- Mac: brew install ffmpeg
- Linux: sudo apt install ffmpeg
    """
}
```

---

## 8. 资源清理

### 8.1 清理策略

```python
import atexit
import shutil

class TempManager:
    """临时文件管理器"""
    
    def __init__(self, temp_dir: str):
        self.temp_dir = temp_dir
        self.files = []
        
        # 注册退出清理
        atexit.register(self.cleanup)
    
    def create_file(self, name: str) -> str:
        """创建临时文件"""
        path = os.path.join(self.temp_dir, name)
        self.files.append(path)
        return path
    
    def cleanup(self):
        """清理所有临时文件"""
        for f in self.files:
            try:
                if os.path.isfile(f):
                    os.remove(f)
                elif os.path.isdir(f):
                    shutil.rmtree(f)
            except Exception as e:
                logger.warning(f"清理临时文件失败: {f}, {e}")
```

---

_Last updated: 2026-03-23_
