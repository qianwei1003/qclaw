# Web Crawler Doc 配置参考

将以下内容保存为 `config.yaml` 放在 skills 目录或工作区根目录：

```yaml
# ==================== 基础配置 ====================

# 默认输出格式: markdown / word / both
default_output: markdown

# 默认保存路径（相对于工作区）
default_save_path: "./knowledge-base/"

# ==================== 请求配置 ====================

# 请求间隔（秒），避免被封
request_delay: 1.0

# 请求超时（秒）
request_timeout: 30

# 并发数（批量爬取时）
max_workers: 3

# ==================== 请求头 ====================

user_agent: "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# 轮换 User-Agent（可选）
user_agents:
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
  - "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 Safari/537.36"
  - "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0"

# ==================== 代理配置 ====================

# 代理设置（不需要则设为 null）
proxy: null
# proxy: "http://127.0.0.1:7890"

# ==================== 自动提取规则 ====================

auto_extract:
  # 标题选择器（按优先级排列）
  title_selector:
    - "h1"
    - ".title"
    - ".article-title"
    - ".post-title"
    - "title"
  
  # 正文选择器（按优先级排列）
  content_selector:
    - "article"
    - ".article-content"
    - ".content"
    - ".post-content"
    - ".entry-content"
    - "#content"
    - ".main-content"
    - "[role='main']"
    - "body"
  
  # 需要移除的元素
  remove_selectors:
    - "script"
    - "style"
    - "nav"
    - "footer"
    - "header"
    - ".ads"
    - ".advertisement"
    - ".sidebar"
    - ".comments"
    - ".share"
    - ".related-posts"

# ==================== 知识库配置 ====================

knowledge_base:
  # 知识库根目录
  root: "./knowledge-base/"
  
  # 分类目录
  categories:
    tax_policy: "./knowledge-base/tax-policy/"
    industry_news: "./knowledge-base/industry-news/"
    regulations: "./knowledge-base/regulations/"
    company_info: "./knowledge-base/company-info/"
  
  # 是否自动创建日期子目录
  date_subdirs: true
  
  # 索引文件
  index_file: "index.md"

# ==================== 文档模板 ====================

# Word 模板路径
word_template: null
# word_template: "./templates/report-template.docx"

# Markdown 模板（暂不支持）
# markdown_template: null

# ==================== 监控配置 ====================

monitor:
  # 默认检查间隔（秒）
  default_interval: 3600  # 1小时
  
  # 状态文件位置
  state_file: "./.monitor_state.json"
  
  # 是否开启变化检测
  detect_changes: true
  
  # 变化检测方式: hash / text_length
  change_detection: hash

# ==================== 日志配置 ====================

# 日志级别: DEBUG / INFO / WARNING / ERROR
log_level: INFO

# 日志文件（不需要则设为 null）
log_file: null
# log_file: "./logs/crawler.log"
