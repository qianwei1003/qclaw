# Cline 高级使用教程

> Cline 是一个集成在 VS Code 中的 AI 编程助手，能够读取文件、编写代码、执行命令、使用浏览器等。本教程涵盖 Cline 的高级功能：Rules（自定义规则）、Workflows（工作流）、Hooks（钩子）、Skills（技能）和 MCP（Model Context Protocol）。

---

## 目录

1. [概述](#概述)
2. [Rules（自定义规则）](#rules自定义规则)
3. [Skills（技能）](#skills技能)
4. [Workflows（工作流）](#workflows工作流)
5. [Hooks（钩子）](#hooks钩子)
6. [MCP（Model Context Protocol）](#mcpmodel-context-protocol)
7. [.clineignore 文件控制](#clineignore-文件控制)
8. [综合示例](#综合示例)
9. [最佳实践](#最佳实践)

---

## 概述

Cline 提供五种核心定制系统，每种在不同场景下发挥作用：

| 功能 | 用途 | 激活时机 | 适用场景 |
|------|------|----------|----------|
| **Rules** | 定义 Cline 的行为方式 | 始终激活（或按条件） | 编码规范、项目约束、团队约定 |
| **Skills** | 按需加载的领域专业知识 | 匹配请求时触发 | 专业知识、复杂流程、机构经验 |
| **Workflows** | 分步骤的任务自动化 | 通过 `/workflow.md` 调用 | 重复流程、发布流程、设置脚本 |
| **Hooks** | 在关键时刻注入自定义逻辑 | 特定事件自动触发 | 验证、强制执行、监控、自动化触发 |
| **.clineignore** | 控制文件访问 | 始终 | 排除依赖、构建产物、大数据文件 |

### 存储位置

所有五种系统都支持全局和项目级配置：

| 系统 | 全局位置 | 项目位置 |
|------|----------|----------|
| Rules | `~/Documents/Cline/Rules/` | `.clinerules/` |
| Skills | `~/.cline/skills/` | `.cline/skills/` |
| Workflows | `~/Documents/Cline/Workflows/` | `.clinerules/workflows/` |
| Hooks | `~/Documents/Cline/Hooks/` | `.clinerules/hooks/` |
| .clineignore | N/A | `.clineignore` |

**使用建议：**
- **项目存储**：团队编码标准、部署工作流、架构约束
- **全局存储**：个人偏好、跨项目通用的生产力工具

---

## Rules（自定义规则）

Rules 是 Markdown 文件，用于在所有对话中提供持久化的指令。与其每次重复相同的偏好设置，不如定义一次让 Cline 自动遵循。

### 支持的规则类型

| 规则类型 | 位置 | 描述 |
|----------|------|------|
| Cline Rules | `.clinerules/` | 主要规则格式 |
| Cursor Rules | `.cursorrules` | 自动检测 |
| Windsurf Rules | `.windsurfrules` | 自动检测 |
| AGENTS.md | `AGENTS.md` | 跨工具兼容标准格式 |

### 创建规则

**方法一：通过 UI 创建**
1. 点击 Cline 面板底部的天平图标（位于模型选择器左侧）
2. 点击 "New rule file..."
3. 输入文件名（如 `coding-standards`），自动添加 `.md` 扩展名

**方法二：手动创建**

在项目根目录创建 `.clinerules/` 文件夹，添加 `.md` 或 `.txt` 文件：

```
your-project/
├── .clinerules/
│   ├── 01-coding.md      # 编码标准
│   ├── 02-testing.md     # 测试要求
│   └── 03-architecture.md # 架构决策
├── src/
└── ...
```

### 规则文件结构

```markdown
# 规则标题

规则存在的简要说明（可选但有帮助）。

## 类别 1
- 具体指令
- 带示例的指令：`像这样`
- 引用文件：参见 /src/utils/example.ts

## 类别 2
- 更多指令
- 在不明显时包含"原因"
```

### 实际示例

**编码规范规则 (coding-standards.md)**

```markdown
# 项目编码规范

## 代码风格
- 所有新文件使用 TypeScript
- 优先使用组合而非继承
- 数据访问使用仓库模式
- 遵循 /src/utils/errors.ts 中的错误处理模式

## 命名约定
- 变量使用 camelCase
- 类名使用 PascalCase
- 常量使用 UPPER_SNAKE_CASE
- 布尔变量使用 is/has/should 前缀

## 文档
- 修改功能时更新相关文档
- 保持 README.md 与新功能同步

## 测试
- 业务逻辑需要单元测试
- API 端点需要集成测试
- 关键用户流程需要 E2E 测试
```

### 条件规则

条件规则只在特定文件匹配时激活，节省上下文令牌。

使用 YAML frontmatter 定义条件：

```yaml
---
paths:
  - "src/components/**"
  - "src/hooks/**"
---

# React 组件规范

创建或修改 React 组件时：
- 使用函数组件和 React Hooks
- 将可复用逻辑提取到自定义 Hooks
- 保持组件专注于单一职责
```

**Glob 模式语法：**

| 模式 | 匹配 |
|------|------|
| `src/**/*.ts` | `src/` 下的所有 TypeScript 文件 |
| `*.md` | 根目录下的 Markdown 文件 |
| `**/*.test.ts` | 项目中任意位置的测试文件 |
| `packages/{web,api}/**` | web 或 api 包中的文件 |

**条件规则示例：**

```yaml
# .clinerules/frontend.md
---
paths:
  - "src/components/**"
  - "src/pages/**"
  - "src/hooks/**"
---

# 前端规范

- 使用 Tailwind CSS 进行样式设置
- 尽可能使用服务端组件
- 保持客户端组件小而专注
```

```yaml
# .clinerules/backend.md
---
paths:
  - "src/api/**"
  - "src/services/**"
  - "src/db/**"
---

# 后端规范

- 服务使用依赖注入
- 所有数据库查询通过仓库层
- 返回类型化错误，不抛出异常
```

---

## Skills（技能）

Skills 是模块化的指令集，用于扩展 Cline 在特定任务上的能力。与始终激活的 Rules 不同，Skills 按需加载，不消耗无关上下文。

### 工作原理

Skills 使用渐进式加载：

| 级别 | 加载时机 | 令牌成本 | 内容 |
|------|----------|----------|------|
| 元数据 | 始终（启动时） | ~100 tokens/技能 | YAML frontmatter 中的 `name` 和 `description` |
| 指令 | 技能触发时 | < 5k tokens | SKILL.md 主体 |
| 资源 | 按需 | 实际上无限制 | 通过 `read_file` 访问的捆绑文件 |

### 技能结构

```
my-skill/
├── SKILL.md          # 必需：主要指令
├── docs/             # 可选：额外文档
│   └── advanced.md
└── scripts/          # 可选：实用脚本
    └── helper.sh
```

### SKILL.md 格式

```markdown
---
name: my-skill
description: 简要描述此技能的作用及何时使用它。
---

# 我的技能

Cline 激活此技能时要遵循的详细指令。

## 步骤
1. 首先，做这个
2. 然后做那个
3. 高级用法参见 [advanced.md](docs/advanced.md)
```

必需字段：
- `name`：必须与目录名完全匹配
- `description`：告诉 Cline 何时使用此技能（最多 1024 字符）

### 创建技能

**方法一：通过 UI 创建**
1. 点击天平图标，切换到 Skills 标签
2. 点击 "New skill..."，输入名称（如 `aws-deploy`）
3. 编辑 `SKILL.md` 文件

**方法二：手动创建**

在 `.cline/skills/`（项目）或 `~/.cline/skills/`（全局）创建目录：

### 命名约定

使用小写连字符（kebab-case），描述性命名：

✅ 好的名称：
- `aws-cdk-deploy`
- `pr-review-checklist`
- `database-migration`
- `api-client-generator`

❌ 避免：
- `aws`（太模糊）
- `my_skill`（下划线，不描述）
- `DeployToAWS`（使用 kebab-case，非 PascalCase）

### 编写有效的描述

好的描述具体且可操作：

```yaml
# ✅ 好的描述
description: 使用 CDK 部署应用到 AWS。在部署、更新基础设施或管理 AWS 资源时使用。

description: 从 git 提交生成发布说明。在准备发布、编写变更日志或总结最近更改时使用。

description: 分析 CSV 和 Excel 数据文件。在探索数据集、生成统计信息或从表格数据创建可视化时使用。
```

```yaml
# ❌ 弱的描述
description: 帮助处理 AWS 相关事务。
description: 数据分析助手。
description: 对发布有用。
```

### 捆绑支持文件

```
complex-skill/
├── SKILL.md
├── docs/
│   ├── setup.md
│   └── troubleshooting.md
├── templates/
│   └── config.yaml
└── scripts/
    └── validate.py
```

**docs/**：详细文档、故障排除指南、参考资料
**templates/**：配置文件模板、代码脚手架、文档模板
**scripts/**：验证脚本、数据处理、复杂计算

### 实际示例：数据分析技能

```markdown
---
name: data-analysis
description: 分析数据文件并生成洞察。在处理需要探索、清理或可视化的 CSV、Excel 或 JSON 数据文件时使用。
---

# 数据分析

分析数据文件时，遵循以下工作流程：

## 1. 理解数据
- 读取文件样本以了解其结构
- 识别列类型和数据质量问题
- 注意任何缺失值或异常

## 2. 询问澄清问题
深入之前，询问用户：
- 他们寻找什么具体洞察？
- 是否有已知的数据质量问题？
- 他们想要什么格式的输出？

## 3. 执行分析
使用 pandas 进行数据操作：

```python
import pandas as pd

# 加载和探索
df = pd.read_csv("data.csv")
print(df.head())
print(df.describe())
print(df.info())
```

对于可视化，根据复杂性选择 matplotlib 或 seaborn。
```

---

## Workflows（工作流）

Workflows 是 Markdown 文件，定义一系列步骤来指导 Cline 完成重复或复杂的任务。输入 `/` 后跟工作流文件名即可调用（如 `/deploy.md`）。

### 工作流结构

文件名成为命令：`demo-workflow.md` 通过 `/demo-workflow.md` 调用。

```markdown
# 演示工作流

此工作流完成的目标的简要描述。

## 步骤 1：检查先决条件
验证环境已准备就绪。查找所需工具和依赖项。

## 步骤 2：运行构建
执行构建命令：
```bash
npm run build
```

## 步骤 3：验证结果
检查构建是否成功完成并报告任何问题。
```

### 创建工作流

**方法一：通过 UI 创建**
1. 点击天平图标，切换到 Workflows 标签
2. 点击 "New workflow file..."，输入文件名
3. 用 markdown 格式添加标题和编号步骤

**方法二：从已完成任务创建**

告诉 Cline："为刚才完成的过程创建一个工作流。" Cline 会分析对话，识别步骤并生成工作流文件。

### 调用工作流

在聊天输入中输入 `/` 查看可用工作流。Cline 会显示自动完成建议。

### 工作流内容类型

**1. 自然语言**

```markdown
## 步骤 1：检查未提交的更改
查看 git 状态。如果有未提交的更改，询问是继续还是中止。

## 步骤 2：运行测试套件
执行所有测试。如果有失败的，显示失败并停止。
```

**2. Cline 工具（XML 语法）**

```xml
<execute_command>
  <command>npm run test</command>
  <requires_approval>false</requires_approval>
</execute_command>

<read_file>
  <path>src/config.json</path>
</read_file>

<ask_followup_question>
  <question>部署到生产环境还是预发布环境？</question>
  <options>["Production", "Staging", "Cancel"]</options>
</ask_followup_question>
```

**3. MCP 工具**

```xml
<use_mcp_tool>
  <server_name>github-server</server_name>
  <tool_name>create_release</tool_name>
  <arguments>{"tag": "v1.2.0", "name": "Release v1.2.0"}</arguments>
</use_mcp_tool>
```

### 实际示例：发布准备工作流

```markdown
# 发布准备

通过运行测试、构建和更新版本信息来准备新发布。

## 步骤 1：检查干净的工作目录
<execute_command>
<command>git status --porcelain</command>
</execute_command>

如果有未提交的更改，询问是继续还是先暂存它们。

## 步骤 2：运行测试套件
<execute_command>
<command>npm run test</command>
</execute_command>

如果有任何测试失败，停止工作流并报告失败。

## 步骤 3：构建项目
<execute_command>
<command>npm run build</command>
</execute_command>

验证构建是否无错误完成。

## 步骤 4：询问新版本
<ask_followup_question>
<question>新版本应该是什么？</question>
<options>["Patch (x.x.X)", "Minor (x.X.0)", "Major (X.0.0)", "Custom"]</options>
</ask_followup_question>

## 步骤 5：更新版本
将 `package.json` 中的版本更新为用户指定的新版本。

## 步骤 6：生成变更日志条目
<execute_command>
<command>git log --oneline $(git describe --tags --abbrev=0)..HEAD</command>
</execute_command>

使用这些提交为新版本编写变更日志条目。
```

---

## Hooks（钩子）

Hooks 是在 Cline 工作流程关键时刻运行的脚本。它们在已知的执行点以一致的输入输出注入自定义逻辑，用于验证操作、监控工具使用、塑造 Cline 的决策。

### 钩子类型

| 钩子类型 | 执行时机 |
|----------|----------|
| TaskStart | 开始新任务时 |
| TaskResume | 恢复中断的任务时 |
| TaskCancel | 取消运行中的任务时 |
| TaskComplete | 任务成功完成时 |
| PreToolUse | Cline 执行工具前 |
| PostToolUse | 工具执行完成后 |
| UserPromptSubmit | 提交消息给 Cline 时 |
| PreCompact | Cline 截断对话历史前 |

### 钩子生命周期

```
开始任务
  ↓
TaskStart / TaskResume
  ↓
对话循环：
  - UserPromptSubmit（提交消息）
  - PreToolUse（执行工具前）→ 工具执行 → PostToolUse（执行后）
  - PreCompact（上下文压缩前）
  ↓
TaskComplete / TaskCancel
  ↓
结束
```

### 创建钩子

1. 点击天平图标，切换到 Hooks 标签
2. 点击 "New hook..." 下拉菜单，选择钩子类型
3. 点击铅笔图标编辑钩子脚本
4. 切换开关激活钩子

**注意：始终查看钩子代码后再启用。钩子会在工作流程中自动执行。**

### 钩子工作原理

钩子是通过 stdin 接收 JSON 输入、通过 stdout 返回 JSON 输出的可执行脚本。

**输入结构：**

```json
{
  "taskId": "abc123",
  "hookName": "PreToolUse",
  "clineVersion": "3.17.0",
  "timestamp": "1736654400000",
  "workspaceRoots": ["/path/to/project"],
  "userId": "user_123",
  "model": {
    "provider": "openrouter",
    "slug": "anthropic/claude-sonnet-4.5"
  },
  "preToolUse": {
    "tool": "write_to_file",
    "parameters": {
      "path": "src/config.ts",
      "content": "..."
    }
  }
}
```

**输出结构：**

```json
{
  "cancel": false,
  "contextModification": "可选的添加到对话的文本",
  "errorMessage": ""
}
```

| 字段 | 类型 | 描述 |
|------|------|------|
| `cancel` | boolean | `true` 时停止操作 |
| `contextModification` | string | 注入到对话中的可选文本 |
| `errorMessage` | string | `cancel` 为 `true` 时显示给用户 |

### 平台差异

- **Windows**：仅支持 `HookName.ps1`（PowerShell 脚本）
- **macOS/Linux**：仅支持无扩展名的 `HookName`（可执行文件）

### 实际示例

**示例 1：文件操作日志（PreToolUse）**

```bash
#!/bin/bash
# 记录所有文件操作到 ~/cline-activity.log

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.preToolUse.tool')
FILE_PATH=$(echo "$INPUT" | jq -r '.preToolUse.parameters.path // "N/A"')

# 记录到文件
echo "$(date '+%H:%M:%S') - $TOOL: $FILE_PATH" >> ~/cline-activity.log

# 始终允许操作
echo '{"cancel":false}'
```

**示例 2：TypeScript 项目强制（PreToolUse）**

```bash
#!/bin/bash
# 阻止在 TypeScript 项目中创建 .js 文件

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.preToolUse.tool')
FILE_PATH=$(echo "$INPUT" | jq -r '.preToolUse.parameters.path // empty')

if [[ "$TOOL" == "write_to_file" && "$FILE_PATH" == *.js ]]; then
  echo '{"cancel":true,"errorMessage":"在此 TypeScript 项目中使用 .ts 文件而非 .js"}'
  exit 0
fi

echo '{"cancel":false}'
```

**示例 3：任务开始日志（TaskStart）**

```bash
#!/bin/bash
INPUT=$(cat)
TASK=$(echo "$INPUT" | jq -r '.taskStart.task')
echo "[TaskStart] 开始: $TASK" >&2
echo '{"cancel":false,"contextModification":"","errorMessage":""}'
```

**示例 4：PostToolUse 审计**

```bash
#!/bin/bash
# 审计工具使用

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.postToolUse.tool')
SUCCESS=$(echo "$INPUT" | jq -r '.postToolUse.success')
DURATION=$(echo "$INPUT" | jq -r '.postToolUse.durationMs')

echo "$(date) - $TOOL: success=$SUCCESS, duration=${DURATION}ms" >> ~/cline-audit.log

echo '{"cancel":false}'
```

---

## MCP（Model Context Protocol）

MCP 是一个开放协议，标准化应用程序如何向 LLM 提供上下文。它就像 AI 应用的 USB-C 端口，提供连接 AI 模型与不同数据源和工具的标准方式。

### 核心概念

- **MCP 主机**：发现连接服务器的能力并加载其工具、提示和资源
- **资源**：提供对只读数据的一致访问
- **安全**：服务器隔离凭证和敏感数据，交互需要用户明确批准

### MCP 服务器配置

配置存储在 `cline_mcp_settings.json` 中。

**STDIO 传输（本地服务器）：**

```json
{
  "mcpServers": {
    "local-server": {
      "command": "node",
      "args": ["/path/to/server.js"],
      "env": {
        "API_KEY": "your_api_key"
      },
      "alwaysAllow": ["tool1", "tool2"],
      "disabled": false
    }
  }
}
```

**SSE 传输（远程服务器）：**

```json
{
  "mcpServers": {
    "remote-server": {
      "url": "https://your-server-url.com/mcp",
      "headers": {
        "Authorization": "Bearer your-token"
      },
      "alwaysAllow": ["tool3"],
      "disabled": false
    }
  }
}
```

### 寻找 MCP 服务器

- **Cline MCP Marketplace**：直接在 Cline 中浏览和安装
- **官方 MCP 服务器**：https://github.com/modelcontextprotocol/servers
- **Awesome-MCP 服务器**：https://github.com/punkpeye/awesome-mcp-servers
- **在线目录**：mcpservers.org、mcp.so、glama.ai/mcp/servers

### 添加 MCP 服务器

最简单的方法是让 Cline 为你构建：

1. 向 Cline 提供 GitHub 仓库 URL
2. 可选：包含 README 内容以提供上下文
3. Cline 克隆仓库、构建并添加配置

**示例对话：**

```
用户："添加来自 https://github.com/modelcontextprotocol/servers/tree/main/src/brave-search 的 MCP 服务器"

Cline："正在克隆仓库。需要构建。我应该运行 'npm run build' 吗？"

用户："是的"

Cline："构建完成。此服务器需要 API 密钥。我应该从哪里获取？"
```

### 使用 MCP 工具

配置服务器后，Cline 会自动检测可用工具：

1. 在聊天中输入你的请求
2. Cline 识别何时可以使用 MCP 工具
3. 批准工具使用（或使用自动批准）

### 全局 MCP 模式

控制 MCP 服务器如何影响令牌使用：

1. 点击 MCP 服务器图标
2. 选择 "Configure" 标签
3. 点击 "Advanced MCP Settings"
4. 找到 `Cline>Mcp:Mode` 并选择首选项

---

## .clineignore 文件控制

`.clineignore` 文件告诉 Cline 在分析代码库时跳过哪些文件和目录。它像 `.gitignore` 一样工作。

### 为什么重要

没有 `.clineignore`，Cline 可能加载整个项目到上下文中，包括依赖项、构建产物和生成的文件。这会浪费令牌、增加成本，并可能将有用上下文推出窗口。

添加 `.clineignore` 可以将起始上下文从 200k+ 令牌减少到 50k 以下。

### 创建 .clineignore

在项目根目录创建 `.clineignore` 文件：

```
# 依赖项
node_modules/
**/node_modules/

# 构建输出
/build/
/dist/
/.next/
/out/

# 测试产物
/coverage/

# 环境变量
.env
.env.*

# 大数据文件
*.csv
*.xlsx
*.sqlite

# 生成/压缩代码
*.min.js
*.map
```

### 模式语法

| 模式 | 匹配 |
|------|------|
| `node_modules/` | `node_modules` 目录 |
| `**/node_modules/` | 任意深度的 `node_modules` |
| `*.csv` | 所有 CSV 文件 |
| `/build/` | 仅项目根目录下的 `build` 目录 |
| `*.env.*` | 如 `.env.local`、`.env.production` 等文件 |
| `!important.csv` | 例外：不忽略此文件 |

### 应该排除什么

**几乎总是排除：**
- 包管理器目录（`node_modules/`、`vendor/`、`.venv/`）
- 构建输出（`dist/`、`build/`、`.next/`、`out/`）
- 覆盖率报告（`coverage/`）
- 大的锁定文件（`package-lock.json`、`yarn.lock`）

**如果存在则排除：**
- 大数据文件（`.csv`、`.xlsx`、`.sqlite`、`.parquet`）
- 二进制资源（图片、字体、视频）
- 生成代码（API 客户端、protobuf 输出、压缩包）
- 包含密钥的环境文件（`.env`、`.env.local`）

**保持可访问：**
- 你积极处理的源代码
- Cline 需要理解的配置文件（`tsconfig.json`、`package.json`）
- 文档和 README
- 测试文件（Cline 通常需要这些上下文）

### 显式访问被忽略的文件

你可以使用 `@` 提及显式引用被忽略的文件。如果输入 `@/node_modules/some-package/index.js`，Cline 会读取该特定文件，即使 `node_modules/` 在 `.clineignore` 中。

---

## 综合示例

### 场景：完整的发布流程

看看所有五种系统如何协同工作：

**1. Rules 确保 Cline 遵循团队的提交消息格式和版本控制策略**

```markdown
# .clinerules/release.md
---
paths:
  - "CHANGELOG.md"
  - "package.json"
---

# 发布规范

- 遵循语义化版本控制（SemVer）
- 提交消息格式：`type(scope): description`
- 更新 CHANGELOG.md 时包含所有相关变更
```

**2. Skills 提供关于 CI/CD 系统的深度知识**

```markdown
---
name: github-actions
description: 管理 GitHub Actions 工作流。在创建、修改或排查 CI/CD 管道时使用。
---

# GitHub Actions 技能

## 工作流结构
- 所有工作流放在 `.github/workflows/`
- 使用语义化命名：`test.yml`、`deploy-production.yml`

## 安全实践
- 不在工作流中硬编码密钥
- 对敏感数据使用 GitHub Secrets
```

**3. Workflows 提供显式的 `/release.md` 序列**

```markdown
# 发布流程

## 步骤 1：验证当前分支
<execute_command>
<command>git branch --show-current</command>
</execute_command>

确保在 main 分支上。

## 步骤 2：运行完整测试
<execute_command>
<command>npm run test:ci</command>
</execute_command>

## 步骤 3：版本升级
<ask_followup_question>
<question>选择版本升级类型</question>
<options>["patch", "minor", "major"]</options>
</ask_followup_question>

## 步骤 4：创建 GitHub Release
使用 GitHub MCP 服务器创建带标签的发布。
```

**4. Hooks 验证测试在提交前通过**

```bash
#!/bin/bash
# PreToolUse 钩子 - 提交前验证

INPUT=$(cat)
TOOL=$(echo "$INPUT" | jq -r '.preToolUse.tool')
PARAMS=$(echo "$INPUT" | jq -r '.preToolUse.parameters.command // empty')

if [[ "$TOOL" == "execute_command" && "$PARAMS" == *"git commit"* ]]; then
  # 检查测试是否通过
  if ! npm run test:quick; then
    echo '{"cancel":true,"errorMessage":"提交前测试失败。请修复后再提交。"}'
    exit 0
  fi
fi

echo '{"cancel":false}'
```

**5. .clineignore 保持构建产物和依赖项不进入上下文**

```
node_modules/
dist/
build/
.coverage/
*.log
```

---

## 最佳实践

### Rules
- **具体而非模糊**：使用 "使用 camelCase 变量、PascalCase 类名" 而非 "使用描述性变量名"
- **包含原因**：当规则看起来随意时，解释原因
- **指向示例**：引用代码库中已存在的模式
- **保持更新**：过时的规则会混淆 Cline
- **每文件一个关注点**：按主题拆分规则

### Skills
- **描述要具体**：包含用户可能说的触发短语
- **保持聚焦**：SKILL.md 保持在 5k 令牌以下
- **使用示例**：展示具体命令和预期输出
- **测试描述**：尝试不同措辞的请求，确保技能可靠触发

### Workflows
- **从简单开始**：先写自然语言步骤
- **明确决策**：需要用户输入时明确说明
- **包含失败处理**：告诉 Cline 出错时做什么
- **保持聚焦**：一个 `deploy.md` 只做部署
- **版本控制**：将工作流提交到仓库

### Hooks
- **审查后再启用**：钩子自动执行，可能阻塞操作
- **使用最严格的触发器**：不需要时不要在每次保存都运行钩子
- **记录行为**：为调试记录钩子活动
- **优雅失败**：钩子失败时不应破坏工作流程

### MCP
- **安全存储密钥**：使用环境变量
- **限制 alwaysAllow**：只自动批准安全工具
- **监控令牌使用**：MCP 工具会增加上下文成本
- **定期更新**：保持 MCP 服务器为最新版本

### .clineignore
- **早期添加**：项目早期就添加 `.clineignore`
- **检查令牌使用**：添加后查看任务头部令牌差异
- **与 .gitignore 分开**：某些 Git 跟踪的文件可能仍需要被 Cline 忽略

---

## 资源链接

- **Cline 官方文档**：https://docs.cline.bot/
- **GitHub 仓库**：https://github.com/cline/cline
- **MCP 官方仓库**：https://github.com/modelcontextprotocol/
- **Awesome MCP 服务器**：https://github.com/punkpeye/awesome-mcp-servers
- **MCP 服务器目录**：
  - https://mcpservers.org/
  - https://mcp.so/
  - https://glama.ai/mcp/servers

---

*本教程基于 Cline 官方文档整理，最后更新：2026年3月*
