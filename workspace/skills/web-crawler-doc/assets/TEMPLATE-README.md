# Word 模板说明

## 模板位置
`assets/report-template.docx`

## 如何创建模板

由于 python-docx 依赖未安装，你可以手动创建模板：

### 方法 1：使用 Microsoft Word

1. 打开 Word，创建新文档
2. 添加以下内容：
   - 标题样式（居中，字号 18pt）
   - 正文样式（字号 11pt，字体：微软雅黑）
3. 保存为 `report-template.docx`
4. 放入 `assets/` 目录

### 方法 2：使用现有文档

1. 找一个格式满意的 Word 文档
2. 删除所有内容，保留样式
3. 保存为 `report-template.docx`
4. 放入 `assets/` 目录

## 模板变量

爬虫脚本会自动填充以下内容：

| 位置 | 填充内容 |
|------|----------|
| 标题 | 网页标题或自定义标题 |
| 来源 | 原始网址 |
| 抓取时间 | 当前日期时间 |
| 正文 | 网页正文内容 |

## 使用模板

```bash
python scripts/crawl.py \
  --url "https://example.com" \
  --output word \
  --template "assets/report-template.docx"
```

## 模板样式建议

- **标题**: 18pt，加粗，居中
- **正文**: 11pt，1.5倍行距
- **页眉**: 可添加公司/个人标识
- **页脚**: 页码

## 安装 python-docx（可选）

如需脚本自动生成模板：

```bash
pip install python-docx
```
