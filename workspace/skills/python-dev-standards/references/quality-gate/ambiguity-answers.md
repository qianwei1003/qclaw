# 歧义解答

## "职责单一"的判断标准

如果能用一句话描述，不包含"和"或"或"，则职责单一。

- ❌ "处理视频和音频" → 拆分
- ❌ "读取文件或解析内容" → 拆分
- ✅ "处理视频" → 单一

## "魔法数字"的判断标准

出现 ≥2 次且会同时改变 → 提取为命名常量。

例外（语义清晰，不需要提取）：
- `0`、`1`、`-1`、`None`、`True`、`False`、空字符串 `""`

## "函数 ≤50 行"的理解

50 行是信号，不是硬限。超过时，满足任一则拆分：
1. 有 ≥2 个独立的 try/except 块
2. 有 ≥3 个 if/elif 分支
3. 有 ≥2 层嵌套循环

## "同一类错误"的判断标准

同一异常类型，或同一失败模式。

- 2 个 `except ValueError` → 同一类
- 2 个无 timeout 的 subprocess → 同一类
- `except ValueError` 和 `except TypeError` → 不同类

防御性重复（两个函数各自 `try/except`）不算同一类。

## "正则表达式 ≥3 个"的判断标准

正则表达式数量 ≥3，或字符串解析逻辑 ≥3 层嵌套，满足任一则触发。

## "路径用字符串拼接"的完整禁止列表

以下全部禁止：

```python
folder + "\\" + name           # 反斜杠拼接
folder + "/" + name             # 正斜杠拼接
f"{folder}/{name}"             # f-string
"/".join([folder, name])       # 混用
```

正确做法：
```python
Path(folder) / name
os.path.join(folder, name)
```

## "具体异常类型"的判断标准

禁止：`except:`、`except Exception:`（范围过大）

推荐：
- 文件不存在 → `FileNotFoundError`
- 参数类型错误 → `TypeError`
- 参数值无效 → `ValueError`
- 网络错误 → `ConnectionError`、`TimeoutError`

## "具体错误信息"的最低标准

必须同时包含以下至少两项：
1. 命令 / 文件路径 / 参数名
2. 返回码 / 具体错误类型 / 已知原因

## timeout 上下级关系

内层 subprocess 必须有独立 timeout。外层 timeout 不免除内层规范。

timeout 是代码正确性的保证，不是兜底。
