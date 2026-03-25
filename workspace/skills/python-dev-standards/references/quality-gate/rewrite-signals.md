# 触发重写的信号

满足任一 → 推翻重来，不修补。

## 1. 同一类错误出现 2 次以上

同一类错误定义：
- 同一个异常类型（如 2 个 `except ValueError`）
- 同一个失败模式（如 2 个无 timeout 的 subprocess 调用）

以下不算"同一类"：
- 两个独立函数各自 `try/except` 捕获同一异常，但**处理逻辑不同**（如 A 重试、B 创建新文件）

以下**算**同一类：
- 两个函数各自 `except ValueError` 处理**相同的参数校验逻辑** → 应该抽取为公共函数
- 业务逻辑中必要的重复异常处理

## 2. 路径用字符串拼接

禁止：
- `folder + "\\" + name`
- `f"{folder}/{name}"`
- `"/".join([...])`

必须：`Path(folder) / name` 或 `os.path.join(folder, name)`

## 3. 正则表达式 ≥3 个，或字符串解析 ≥3 层嵌套

满足任一则触发。

这意味着应该用专门的解析库：
- JSON → `json.loads()`
- YAML → `yaml.safe_load()`
- 复杂文本 → 正则和解析函数分离

## 4. subprocess 调用没有 timeout

无论外层是否有 timeout，内层 subprocess 必须有独立的 timeout。

timeout 是代码正确性的保证，不是"兜底"。

## 5. 错误信息没有具体值

必须包含：
- 命令 / 文件路径 / 参数名（至少一项）
- 返回码 / 具体错误类型（至少一项）

不是 `"失败"`、"操作失败"这类无意义的文字。
