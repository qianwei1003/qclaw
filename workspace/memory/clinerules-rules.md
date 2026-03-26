# 2026-03-25 - Cline Rules 优化

## 关键规则（强制）

**clinerules 写完要引入到 clinerules.yaml**

### 流程
1. 在 `C:\Users\admin\.qclaw\cline\rules\` 创建新的 YAML 文件
2. 命名规则：`clinerules.<功能名>.yaml`
3. 格式参考：`clinerules.core.yaml` 或 `clinerules.workflow.yaml`
4. **必须**在 `clinerules.yaml` 的 `includes` 列表中添加新文件

### 示例
```yaml
# clinerules.yaml
rules:
  includes:
    - clinerules.i18n.yaml
    - clinerules.core.yaml
    - clinerules.workflow.yaml  # ← 新增的必须加这里
```

## 已完成
- ✅ `clinerules.workflow.yaml` - Diff First 工作流规则
- ✅ 已引入到 `clinerules.yaml`

## 后续规则计划
- 待定

---
Source: 用户指示 2026-03-25 16:54
