---
name: web-crawler-doc
description: |
  通用网页爬虫 + 内容提取 + 文档生成工具。用于抓取任意网站内容，整理成结构化文档（Markdown/Word），更新个人知识库。
  
  使用场景：
  - 抓取财税政策网站更新
  - 收集行业资讯整理成文档
  - 监控特定网页变化并归档
  - 将网页内容转为离线可读的 Markdown/Word
  
  触发词："爬取网站"、"抓取网页"、"生成文档"、"更新知识库"、"网页转文档"
---

# Web Crawler Doc - 网页爬虫文档生成器

抓取任意网页内容，提取核心信息，生成结构化的 Markdown 或 Word 文档，用于更新知识库。

## 快速开始

### 1. 单页爬取

```bash
# 爬取单个网页，生成 Markdown
python scripts/crawl.py --url "https://example.com/article" --output markdown

# 爬取并生成 Word
python scripts/crawl.py --url "https://example.com/article" --output word
```

### 2. 批量爬取

```bash
# 从 URL 列表批量爬取
python scripts/batch_crawl.py --urls-file urls.txt --output-dir ./docs/
```

### 3. 监控更新

```bash
# 监控网页变化，有更新时生成新文档
python scripts/monitor.py --url "https://example.com/updates" --interval 3600
```

## 工作流程

```
用户提供 URL → 爬取网页 → 提取正文 → 结构化处理 → 生成文档 → 保存到知识库
```

## 详细用法

### 爬取参数

| 参数 | 说明 | 示例 |
|------|------|------|
| `--url` | 目标网址 | `"https://xxx.com"` |
| `--output` | 输出格式: markdown/word/both | `markdown` |
| `--selector` | CSS 选择器，指定提取区域 | `".article-content"` |
| `--title` | 自定义文档标题 | `"增值税新规"` |
| `--save-to` | 保存路径 | `./knowledge-base/tax/` |

### 示例场景

**场景 1：抓取税务总局最新政策**
```bash
python scripts/crawl.py \
  --url "https://www.chinatax.gov.cn/xxx.html" \
  --output markdown \
  --selector ".content-detail" \
  --title "2024年增值税新政解读" \
  --save-to "./knowledge-base/tax-policy/2024/"
```

**场景 2：批量整理行业资讯**
```bash
# 先创建 URL 列表文件
echo "https://site1.com/news1" > urls.txt
echo "https://site2.com/news2" >> urls.txt

# 批量爬取
python scripts/batch_crawl.py \
  --urls-file urls.txt \
  --output-dir "./knowledge-base/industry-news/" \
  --format markdown
```

**场景 3：生成 Word 汇报文档**
```bash
python scripts/crawl.py \
  --url "https://example.com/report" \
  --output word \
  --title "月度行业动态汇总" \
  --template "assets/report-template.docx"
```

## 输出格式

### Markdown 格式
- 自动提取标题、正文、表格
- 保留链接（转为脚注）
- 图片保存到同级 `images/` 目录

### Word 格式
- 使用模板生成专业排版
- 自动目录
- 页眉页脚

## 知识库管理建议

推荐目录结构：

```
knowledge-base/
├── tax-policy/          # 税务政策
│   ├── 2024/
│   ├── 2025/
│   └── index.md         # 索引
├── industry-news/       # 行业资讯
├── regulations/         # 法规解读
└── templates/           # 文档模板
```

## 脚本说明

### scripts/crawl.py
单页爬取主脚本，支持动态渲染（JavaScript 页面）。

### scripts/batch_crawl.py
批量爬取，支持并发、去重、错误重试。

### scripts/monitor.py
监控模式，定时检查网页变化，变化时自动生成新文档。

### scripts/extract.py
内容提取工具，测试选择器、预览提取结果。

## 依赖安装

```bash
pip install requests beautifulsoup4 playwright python-docx markdown
playwright install
```

## 注意事项

1. **遵守 robots.txt** - 爬虫自动检查网站的 robots.txt
2. **控制频率** - 默认 1 秒间隔，避免对目标网站造成压力
3. **反爬处理** - 支持 User-Agent 轮换、代理设置
4. **动态页面** - 使用 Playwright 处理 JavaScript 渲染的页面

## 故障排查

**问题：提取内容为空**
- 检查 `--selector` 是否正确
- 尝试不加 selector，让程序自动检测正文区域
- 可能是动态页面，确认已安装 Playwright

**问题：中文乱码**
- 程序自动检测编码，如仍乱码可手动指定 `--encoding utf-8`

**问题：被网站封 IP**
- 增加 `--delay 3` 降低请求频率
- 使用 `--proxy` 设置代理

## 进阶配置

创建 `config.yaml` 自定义默认行为：

```yaml
# 默认输出格式
default_output: markdown

# 默认保存路径
default_save_path: "./knowledge-base/"

# 请求间隔（秒）
request_delay: 1

# User-Agent
user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"

# 代理设置
proxy: null

# 自动提取规则
auto_extract:
  title_selector: "h1, .title, .article-title"
  content_selector: "article, .content, .article-content, .post-content"
```
