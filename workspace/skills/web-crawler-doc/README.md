# Web Crawler Doc 使用指南

## 快速开始

### 1. 安装依赖

```bash
pip install requests beautifulsoup4 markdownify python-docx playwright
playwright install
```

### 2. 基本用法

**爬取单个网页：**
```bash
python scripts/crawl.py --url "https://example.com/article"
```

**生成 Word 文档：**
```bash
python scripts/crawl.py --url "https://example.com/article" --output word
```

**批量爬取：**
```bash
# 创建 URL 列表文件
cat > urls.txt << EOF
https://site1.com/page1
https://site2.com/page2
EOF

# 批量爬取
python scripts/batch_crawl.py --urls-file urls.txt --output-dir ./docs/
```

**监控网页变化：**
```bash
python scripts/monitor.py --url "https://example.com/updates" --interval 3600
```

## 文件结构

```
web-crawler-doc/
├── SKILL.md                    # 技能说明（主入口）
├── scripts/
│   ├── crawl.py               # 单页爬取
│   ├── batch_crawl.py         # 批量爬取
│   ├── monitor.py             # 监控模式
│   └── extract.py             # 内容提取工具
├── references/
│   └── config-reference.md    # 配置参考
└── assets/
    └── report-template.docx   # Word 模板（可选）
```

## 典型使用场景

### 场景 1：收集财税政策

```bash
python scripts/crawl.py \
  --url "https://www.chinatax.gov.cn/chinatax/n810341/n810755/c5188463/content.html" \
  --output markdown \
  --selector ".content-detail" \
  --title "增值税小规模纳税人减免政策" \
  --save-to "./knowledge-base/tax-policy/2024/"
```

### 场景 2：批量整理行业资讯

```bash
# 创建 URL 列表
echo "https://news.site1.com/finance/001" > urls.txt
echo "https://news.site2.com/economy/002" >> urls.txt
echo "https://news.site3.com/tax/003" >> urls.txt

# 批量爬取
python scripts/batch_crawl.py \
  --urls-file urls.txt \
  --output-dir "./knowledge-base/industry-news/2024-03/" \
  --workers 2 \
  --delay 2
```

### 场景 3：监控政策更新

```bash
python scripts/monitor.py \
  --url "https://www.chinatax.gov.cn/chinatax/n810341/n810755/index.html" \
  --selector ".news-list" \
  --interval 7200 \
  --output-dir "./knowledge-base/tax-policy/updates/"
```

## 知识库管理建议

推荐目录结构：

```
knowledge-base/
├── tax-policy/              # 税务政策
│   ├── 2024/
│   ├── 2025/
│   └── index.md            # 索引
├── industry-news/          # 行业资讯
│   ├── 2024-01/
│   ├── 2024-02/
│   └── index.md
├── regulations/            # 法规解读
├── company-info/           # 企业信息
└── templates/              # 文档模板
```

## 常见问题

**Q: 提取的内容不对？**  
A: 使用 `--selector` 指定 CSS 选择器，或先用浏览器开发者工具检查目标元素。

**Q: 动态加载的页面抓不到？**  
A: 需要 Playwright 支持，确保已运行 `playwright install`。

**Q: 被网站封了？**  
A: 增加 `--delay` 参数降低频率，或使用代理。

**Q: 中文乱码？**  
A: 程序自动检测编码，如遇问题可手动指定 `--encoding utf-8`。

## 高级配置

创建 `config.yaml` 自定义默认行为，详见 `references/config-reference.md`。

## 更新日志

- v1.0.0 - 初始版本
  - 支持单页/批量爬取
  - 支持 Markdown/Word 输出
  - 支持网页变化监控
