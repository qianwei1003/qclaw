"""
视频下载框架 - 入口脚本
用法:
    python run.py                    # 运行所有订阅源
    python run.py --test             # 测试模式（只显示，不下载）
    python run.py --source youtube   # 只运行指定平台
    python run.py --add "URL"       # 快速添加订阅源
    python run.py --list             # 查看订阅源状态
"""
import sys
import os
import subprocess
import argparse

# 确保当前目录正确
os.chdir(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from downloader import run_all, run_subscription, SOURCES, logger
from config import load_config, get_enabled_subscriptions


def cmd_list():
    """查看订阅源列表"""
    config = load_config()
    subs = config.get("subscriptions", {})
    
    print("\n📺 订阅源列表\n" + "─" * 60)
    
    total = 0
    enabled = 0
    
    for platform, sources in subs.items():
        source_info = SOURCES.get(platform, None)
        platform_label = f"{platform} ({source_info.platform_name})" if source_info else platform
        
        print(f"\n【{platform.upper()}】")
        
        for sub in sources:
            status = "✅ 启用" if sub.get("enabled") else "❌ 禁用"
            quality = sub.get("quality", "默认")
            name = sub.get("name", "未命名")
            
            print(f"  • {name}")
            print(f"    状态: {status} | 画质: {quality}")
            print(f"    URL: {sub.get('url', 'N/A')[:60]}...")
            
            total += 1
            if sub.get("enabled"):
                enabled += 1
    
    print("\n" + "─" * 60)
    print(f"总计: {total} 个订阅源，{enabled} 个已启用\n")


def cmd_test():
    """测试模式：解析但不下载"""
    from config import get_enabled_subscriptions
    
    enabled = get_enabled_subscriptions()
    
    if not enabled:
        print("❌ 没有启用的订阅源")
        return
    
    print(f"\n🧪 测试模式，共 {len(enabled)} 个订阅源\n")
    
    for sub in enabled:
        platform = sub["platform"]
        name = sub.get("name", platform)
        
        if platform not in SOURCES:
            print(f"❌ {name}: 平台 {platform} 暂不支持")
            continue
        
        source = SOURCES[platform]
        videos = source.get_video_list(sub["url"])
        
        if videos:
            print(f"✅ {name}: 获取到 {len(videos)} 个视频")
            for v in videos[:3]:
                print(f"   - {v['title'][:50]}")
            if len(videos) > 3:
                print(f"   ... 还有 {len(videos) - 3} 个")
        else:
            print(f"❌ {name}: 获取失败")


def cmd_add(url: str):
    """快速添加订阅源（交互式）"""
    print(f"\n🔍 正在识别: {url}\n")
    
    # 用 yt-dlp 识别平台
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", "--playlist-end", "1", url],
            capture_output=True, text=True, encoding="utf-8", timeout=30
        )
        
        if result.returncode != 0:
            print(f"❌ 无法识别该URL: {result.stderr[:200]}")
            return
        
        import json
        data = json.loads(result.stdout)
        
        # 判断平台
        webpage_url = data.get("webpage_url", "")
        
        if "youtube.com" in webpage_url or "youtu.be" in webpage_url:
            platform = "youtube"
        elif "bilibili.com" in webpage_url:
            platform = "bilibili"
        elif "tiktok.com" in webpage_url:
            platform = "tiktok"
        else:
            platform = "unknown"
        
        print(f"✅ 识别为: {platform}")
        print(f"   标题: {data.get('title', 'N/A')}")
        print(f"   频道: {data.get('channel', 'N/A')}")
        
        print(f"\n请手动将以下内容添加到 sources.yaml 的 subscriptions.{platform} 中:\n")
        
        new_entry = f"""  - name: "{data.get('channel', '新订阅源')}"
      url: "{url}"
      quality: "best"
      enabled: true"""
        
        print(new_entry)
        
    except Exception as e:
        print(f"❌ 识别失败: {e}")


def main():
    parser = argparse.ArgumentParser(description="视频下载框架")
    parser.add_argument("--test", action="store_true", help="测试模式")
    parser.add_argument("--list", action="store_true", help="查看订阅源")
    parser.add_argument("--add", metavar="URL", help="添加订阅源")
    parser.add_argument("--source", metavar="PLATFORM", help="只运行指定平台")
    parser.add_argument("--config", metavar="PATH", help="指定配置文件")
    
    args = parser.parse_args()
    
    if args.list:
        cmd_list()
    elif args.test:
        cmd_test()
    elif args.add:
        cmd_add(args.add)
    elif args.source:
        # 运行指定平台
        from config import get_enabled_subscriptions
        subs = get_enabled_subscriptions()
        filtered = [s for s in subs if s["platform"] == args.source]
        
        if not filtered:
            print(f"❌ 没有找到启用的 {args.source} 订阅源")
            return
        
        for sub in filtered:
            run_subscription(sub)
    else:
        # 运行全部
        run_all()


if __name__ == "__main__":
    main()
