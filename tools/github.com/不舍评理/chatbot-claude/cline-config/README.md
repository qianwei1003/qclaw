# Cline 快速部署指南

## 📦 前置要求

- Node.js 18+
- VS Code 或 Cursor
- Git（可选，用于版本控制）

## 🚀 部署步骤

### 方式一：手动配置

1. **打开 Cline 设置**
   - VS Code: `Cmd/Ctrl + Shift + P` → "Cline: Open Settings"
   - Cursor: 类似操作

2. **复制配置文件**
   ```bash
   cp cline-config/settings.json ~/.cline/settings.json
   cp cline-config/mcp-servers.json ~/.cline/mcp-servers.json
   ```

3. **配置 API Key**
   - 设置环境变量：`CLINE_API_KEY=your-key`
   - 或在 settings.json 中直接配置

4. **安装 MCP Servers**
   - 按照 mcp-servers.json 中的配置逐一安装

### 方式二：自动部署脚本

```bash
python deploy-cline.py --config-dir ./cline-config
```

## ✅ 验证配置

```bash
# 检查配置文件
cline --verify-config

# 测试 API 连接
cline --test-api

# 列出已安装的 MCP Servers
cline --list-mcp
```

## 🔄 同步配置

### 保存当前配置
```bash
cline --export-config > cline-config/backup-$(date +%Y%m%d).json
```

### 恢复配置
```bash
cline --import-config cline-config/settings.json
```

## 📝 配置版本管理

建议使用 Git 管理配置文件：

```bash
cd cline-config
git init
git add .
git commit -m "Initial Cline configuration"
git remote add origin <your-repo>
git push -u origin main
```

## 🆘 故障排除

| 问题 | 解决方案 |
|------|--------|
| API Key 无效 | 检查环境变量或 settings.json |
| MCP Server 连接失败 | 验证 command 和 args 路径 |
| 配置未生效 | 重启 VS Code/Cursor |

---

**最后更新**：2026-03-23
