# Review Checklist

写完后逐项检查，任一 ❌ 必须修复。

## FFmpeg / subprocess

- [ ] `-y` 放在 `-i` 之前
- [ ] 需要快速 seek 时，`-ss` 在 `-i` 之前
- [ ] `subprocess.run()` 有 `timeout`
- [ ] 成功判断：`returncode == 0`
- [ ] 错误信息包含具体值（至少以下两项：命令/路径/参数名、返回码/错误类型）

## 路径处理

- [ ] 没有字符串拼接路径
- [ ] 临时文件用 `tempfile.TemporaryDirectory()` 或 `tempfile.NamedTemporaryFile()`，用 `with` 自动清理

## 错误处理

- [ ] 没有裸 `except:`
- [ ] 异常链用 `from e`
- [ ] 错误信息是具体的，不是 `"失败"`

## 边界条件

- [ ] 参数 `None` / `0` / 空列表有处理
- [ ] 负数、超出范围的值有处理

## Python 惯用写法

- [ ] 命名符合规范
- [ ] 没有 `print`（用 `logger`）
- [ ] 有副作用的操作用了 `with` 或 `try/finally`
- [ ] 公开接口有类型注解
- [ ] 没有 ≥3 行重复代码
- [ ] 魔法数字提取为常量

## 常见错误模式

| 检查 | 说明 |
|------|------|
| `stderr.split()[-3]` | 替换为过滤进度条后取最后一行 |
| `except:` | 替换为具体异常类型 |
| 无 timeout | 必须加 |
| 字符串拼接路径 | 替换为 `pathlib` 或 `os.path.join` |
| 临时文件在当前目录 | 改用 `tempfile` |
| bare `return False` | 改为返回错误信息 |

触发重写信号见 `rewrite-signals.md`
