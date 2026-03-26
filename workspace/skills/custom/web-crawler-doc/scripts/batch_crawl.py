#!/usr/bin/env python3
"""
批量爬虫脚本
支持从文件读取 URL 列表，并发爬取
"""

import argparse
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

try:
    import requests
    from bs4 import BeautifulSoup
    from markdownify import markdownify as md
except ImportError:
    print("请先安装依赖: pip install requests beautifulsoup4 markdownify")
    sys.exit(1)


def fetch_page(url, headers=None, timeout=30):
    """获取网页内容"""
    default_headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    if headers:
        default_headers.update(headers)
    
    try:
        response = requests.get(url, headers=default_headers, timeout=timeout)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        return response.text
    except Exception as e:
        return None, str(e)


def extract_content(html, selector=None):
    """提取正文内容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    if selector:
        content = soup.select_one(selector)
        if content:
            return content, soup.title.string if soup.title else "无标题"
    
    content_selectors = [
        'article', '.article-content', '.content', '.post-content',
        '.entry-content', '#content', '.main-content', '[role="main"]'
    ]
    
    for sel in content_selectors:
        content = soup.select_one(sel)
        if content:
            return content, soup.title.string if soup.title else "无标题"
    
    return soup.body or soup, soup.title.string if soup.title else "无标题"


def save_markdown(content_html, title, url, save_path):
    """保存为 Markdown"""
    markdown_content = md(str(content_html), heading_style="ATX")
    
    header = f"""# {title}

> 来源: {url}
> 抓取时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

"""
    
    full_content = header + markdown_content
    
    os.makedirs(save_path, exist_ok=True)
    
    # 清理文件名
    import re
    clean = re.sub(r'[\\/*?:"<>|]', '', title)[:100].strip() or "untitled"
    filename = f"{clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(save_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filepath


def crawl_single(args_tuple):
    """爬取单个 URL"""
    url, output_dir, delay = args_tuple
    
    print(f"🌐 正在爬取: {url}")
    
    html = fetch_page(url)
    if isinstance(html, tuple):  # 错误返回
        print(f"❌ 失败: {url} - {html[1]}")
        return None
    
    content, title = extract_content(html)
    
    try:
        filepath = save_markdown(content, title, url, output_dir)
        print(f"✓ 已保存: {filepath}")
        time.sleep(delay)
        return filepath
    except Exception as e:
        print(f"❌ 保存失败: {url} - {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='批量网页爬虫')
    parser.add_argument('--urls-file', required=True, help='URL 列表文件（每行一个）')
    parser.add_argument('--output-dir', default='./docs/', help='输出目录')
    parser.add_argument('--format', choices=['markdown'], default='markdown',
                       help='输出格式（目前仅支持 markdown）')
    parser.add_argument('--workers', type=int, default=3, help='并发数（默认: 3）')
    parser.add_argument('--delay', type=float, default=1.0, help='请求间隔（秒，默认: 1）')
    
    args = parser.parse_args()
    
    # 读取 URL 列表
    if not os.path.exists(args.urls_file):
        print(f"❌ 文件不存在: {args.urls_file}")
        return 1
    
    with open(args.urls_file, 'r', encoding='utf-8') as f:
        urls = [line.strip() for line in f if line.strip() and not line.startswith('#')]
    
    if not urls:
        print("❌ URL 列表为空")
        return 1
    
    print(f"📋 共 {len(urls)} 个 URL 待爬取")
    print(f"⚙️  并发: {args.workers}, 间隔: {args.delay}s")
    print()
    
    # 批量爬取
    crawl_args = [(url, args.output_dir, args.delay) for url in urls]
    
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {executor.submit(crawl_single, arg): arg[0] for arg in crawl_args}
        
        for future in as_completed(futures):
            result = future.result()
            if result:
                results.append(result)
    
    print()
    print(f"✅ 完成！成功: {len(results)}/{len(urls)}")
    print(f"📁 输出目录: {os.path.abspath(args.output_dir)}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
