# Cline 改动日志规范流程

## 一、核心流程

```
用户需求 → Cline 改代码 → 自动生成改动档案 → 用户确认 → 存档 → Git 提交
```

---

## 二、.clinerules 规则（写入项目根目录）

```markdown
## 📋 改动档案（强制执行）

每次代码改动完成后，**必须**按以下流程执行：

### 第一步：输出改动档案
格式如下：

---
## 改动档案：[功能名称]

**时间**：YYYY-MM-DD HH:mm
**需求来源**：用户需求 / Issue #xxx / Bug #xxx

### 改动文件
| 文件路径 | 改动类型 | 行号范围 | 说明 |
|----------|---------|---------|------|
| src/views/UserList.vue | 新增 | 45-60 | 搜索框组件 |
| src/api/user.js | 修改 | 12-15 | 新增 searchUser 接口 |

### 改动详情
1. **UserList.vue**
   - 新增：搜索框组件（第 45-52 行）
   - 新增：filteredUsers 计算属性（第 53-58 行）
   - 修改：列表渲染改为 filteredUsers（第 60 行）

2. **api/user.js**
   - 新增：searchUser(params) 函数

### 潜在影响范围
- [ ] 用户列表分页逻辑（搜索时需重置页码）
- [ ] 用户列表性能（大数据量时需考虑防抖）
- [ ] 无

### 测试要点
- [ ] 搜索功能正常
- [ ] 清空搜索恢复原列表
- [ ] 分页重置正常
- [ ] 其他：___

### 关联信息
- Issue：#123
- PR：#124
- 相关文档：docs/user-module.md
---

### 第二步：等待用户确认
用户确认内容无误后，回复「确认存档」。

### 第三步：保存档案
将档案保存至：
```
docs/change-logs/YYYY-MM-DD-[功能名称].md
```

示例：
```
docs/change-logs/2024-03-24-用户搜索功能.md
```

### 第四步：Git 提交时关联
提交信息格式：
```
feat(user): 添加用户搜索功能

改动档案: docs/change-logs/2024-03-24-用户搜索功能.md
Issue: #123
```

---

## 三、目录结构

```
项目根目录/
├── .clinerules              # Cline 行为约束规则
├── docs/
│   └── change-logs/         # 改动档案存放位置
│       ├── README.md        # 使用说明
│       ├── 2024-03-24-用户搜索功能.md
│       ├── 2024-03-25-订单导出功能.md
│       └── ...
└── src/
```

---

## 四、查询方式

### 方式一：VSCode 全局搜索
1. `Ctrl + Shift + F`
2. 搜索关键词（如「用户列表」）
3. 限定范围：`docs/change-logs/`

### 方式二：命令行
```bash
# 搜索包含"用户列表"的改动档案
grep -r "用户列表" docs/change-logs/

# 使用 ripgrep（更快）
rg "用户列表" docs/change-logs/
```

### 方式三：Python 查询脚本
```bash
python scripts/search-changes.py "用户列表"
```

输出示例：
```
找到 3 个相关改动：

1. docs/change-logs/2024-03-24-用户搜索功能.md
   - 第 3 行：改动档案：用户搜索功能
   - 第 15 行：| src/views/UserList.vue | 新增 | 45-60 |

2. docs/change-logs/2024-03-20-用户列表优化.md
   - 第 3 行：改动档案：用户列表分页优化
```

---

## 五、关键约束（写入 .clinerules）

```markdown
## 🚫 改动档案约束

### 必须生成档案的场景
- 新增功能
- 修改功能
- Bug 修复
- 重构代码
- 配置变更

### 可跳过档案的场景
- 仅修改注释
- 仅修改文档
- 仅修改样式（不影响逻辑）

### 档案质量要求
- 文件路径必须完整（相对于项目根目录）
- 行号范围必须准确
- 影响范围必须列出（即使写「无」）
- 测试要点必须列出（至少 3 条）
```

---

## 六、一个月后查 Bug 的使用场景

**场景**：测试报告「用户列表分页有问题」

**步骤**：
1. 搜索改动档案：
   ```bash
   rg "用户列表.*分页" docs/change-logs/
   ```
2. 找到：`2024-03-24-用户搜索功能.md`
3. 查看改动详情：
   - 改了 UserList.vue 第 60 行
   - 潜在影响范围写了「用户列表分页逻辑」
4. 定位问题：搜索功能改动了分页逻辑，但当时没处理重置

**耗时**：2 分钟（不用翻代码、不用回忆）

---

## 七、进阶（可选）

### 自动生成索引
每次存档时，自动更新 `docs/change-logs/index.json`：

```json
{
  "logs": [
    {
      "file": "2024-03-24-用户搜索功能.md",
      "date": "2024-03-24",
      "keywords": ["用户列表", "搜索", "UserList"],
      "files_changed": ["src/views/UserList.vue", "src/api/user.js"]
    }
  ]
}
```

查询时可直接按关键词、文件名、日期过滤。

### 语义搜索（需 Python + embeddings）
安装：
```bash
pip install sentence-transformers
```

查询：
```bash
python scripts/search-changes.py --semantic "哪个改动可能影响分页"
```

---

## 八、落地检查清单

- [ ] 在项目根目录创建 `.clinerules`，写入上述规则
- [ ] 创建 `docs/change-logs/` 目录
- [ ] 创建 `docs/change-logs/README.md`（使用说明）
- [ ] 下次改动时，要求 Cline 按流程输出档案
- [ ] 确认无误后存档
- [ ] Git 提交时带上档案
