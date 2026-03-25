# Python Patterns

## 命名规范

| 类型 | 规范 | 禁止 |
|------|------|------|
| 函数/变量 | `snake_case` | `data`、`tmp`、`res` |
| 类 | `PascalCase` | `myClass` |
| 常量 | `UPPER_SNAKE_CASE` | `maxRetry` |
| bool 变量 | `is_` / `has_` / `can_` / `should_` | `valid`、`exists` |
| 私有成员 | `_leading_underscore` | 公开内部状态 |

## 路径处理

```
禁止：folder + "\\" + name  /  f"{folder}/{name}"  /  "/".join([...])
必须：Path(folder) / name  或  os.path.join(folder, name)
```

## 模块组织

单一职责。按依赖方向分层：高层模块依赖低层模块，不反向。

```
project/
├── main.py
├── package/
│   ├── executor.py      # 执行层
│   ├── analyzer.py      # 分析层
│   └── errors.py        # 统一异常
└── tests/
```

## 类型注解

```python
# Python 3.10+
def get_duration(path: str) -> float: ...
def trim(path: str, start: float | None = None) -> bool: ...
@dataclass
class Result:
    success: bool
    duration: float
```

## 日志

```
禁止：print("开始")
必须：logger.info("开始: %s", path)
```

日志级别：`debug` → `info` → `warning` → `error` → `critical`。

Logger 配置（在 main 或模块初始化时设置一次）：
```python
import logging
logger = logging.getLogger(__name__)
# 在 main 中：
logging.basicConfig(level=logging.INFO, format='%(name)s - %(levelname)s - %(message)s')
```

## 上下文管理器

文件/临时目录/连接等有副作用的操作，必须用 `with` 或 `try/finally`。

## 禁止的模式

| 禁止 | 原因 |
|------|------|
| `except:` | 捕获所有异常 |
| `result.stderr.split()[-3]` | 进度条导致读错行 |
| `os.system()` / `shell=True` | 无法捕获输出，有注入风险 |
| 硬编码魔法数字（≥2次出现） | 无法统一调整 |
| 函数超过 50 行 | 信号：问自己"能拆分吗？" |
