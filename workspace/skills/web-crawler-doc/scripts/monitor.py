#!/usr/bin/env python3
"""
网页监控脚本
定时检查网页变化，变化时自动生成新文档
"""

import argparse
import hashlib
import json
import os
import sys
import time
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
        return None


def get_content_hash(content):
    """计算内容哈希"""
    return hashlib.md5(content.encode('utf-8')).hexdigest()


def load_state(state_file):
    """加载监控状态"""
    if os.path.exists(state_file):
        with open(state_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}


def save_state(state, state_file):
    """保存监控状态"""
    os.makedirs(os.path.dirname(state_file) or '.', exist_ok=True)
    with open(state_file, 'w', encoding='utf-8') as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def extract_content(html, selector=None):
    """提取正文内容"""
    soup = BeautifulSoup(html, 'html.parser')
    
    for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
        tag.decompose()
    
    if selector:
        content = soup.select_one(selector)
        if content:
            return content.get_text(), soup.title.string if soup.title else "无标题"
    
    # 获取纯文本用于比较
    text = soup.get_text(separator='\n', strip=True)
    return text, soup.title.string if soup.title else "无标题"


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
    
    import re
    clean = re.sub(r'[\\/*?:"<>|]', '', title)[:100].strip() or "untitled"
    filename = f"{clean}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
    filepath = os.path.join(save_path, filename)
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(full_content)
    
    return filepath


def check_and_save(url, selector, output_dir, state):
    """检查变化并保存"""
    print(f"[{datetime.now().strftime('%H:%M:%S')}] 检查: {url}")
    
    html = fetch_page(url)
    if not html:
        print(f"  ❌ 获取失败")
        return False
    
    # 提取内容
    soup = BeautifulSoup(html, 'html.parser')
    
    if selector:
        content_elem = soup.select_one(selector)
    else:
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()
        content_elem = soup.body or soup
    
    if not content_elem:
        print(f"  ❌ 未找到内容")
        return False
    
    # 计算哈希
    content_text = content_elem.get_text(separator=' ', strip=True)
    current_hash = get_content_hash(content_text)
    
    # 检查是否变化
    url_key = url.replace('/', '_').replace(':', '_')
    last_hash = state.get(url_key, {}).get('hash')
    
    if last_hash == current_hash:
        print(f"  ✓ 无变化")
        return False
    
    # 有变化，保存
    print(f"  🔄 检测到变化！")
    
    title = soup.title.string if soup.title else "无标题"
    filepath = save_markdown(content_elem, title, url, output_dir)
    
    # 更新状态
    state[url_key] = {
        'hash': current_hash,
        'last_check': datetime.now().isoformat(),
        'last_file': filepath
    }
    
    print(f"  ✓ 已保存: {filepath}")
    return True


def main():
    parser = argparse.ArgumentParser(description='网页监控工具')
    parser.add_argument('--url', required=True, help='要监控的网址')
    parser.add_argument('--selector', help='CSS 选择器，监控特定区域')
    parser.add_argument('--interval', type=int, default=3600, help='检查间隔（秒，默认: 3600=1小时）')
    parser.add_argument('--output-dir', default='./monitored/', help='输出目录')
    parser.add_argument('--state-file', default='./.monitor_state.json', help='状态文件')
    parser.add_argument('--once', action='store_true', help='只检查一次，不循环')
    
    args = parser.parse_args()
    
    print(f"🔍 网页监控启动")
    print(f"   URL: {args.url}")
    print(f"   间隔: {args.interval}秒 ({args.interval/60:.1f}分钟)")
    print(f"   输出: {args.output_dir}")
    print()
    
    # 加载状态
    state = load_state(args.state_file)
    
    if args.once:
        # 只检查一次
        changed = check_and_save(args.url, args.selector, args.output_dir, state)
        save_state(state, args.state_file)
        return 0 if changed else 0
    
    # 循环监控
    try:
        while True:
            check_and_save(args.url, args.selector, args.output_dir, state)
            save_state(state, args.state_file)
            
            print(f"  ⏳ 下次检查: {args.interval}秒后")
            print()
            time.sleep(args.interval)
    
    except KeyboardInterrupt:
        print("\n👋 监控已停止")
        save_state(state, args.state_file)
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
