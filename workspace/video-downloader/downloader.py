"""
视频下载框架 - 核心下载模块
"""
import os
import re
import time
import subprocess
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any
from abc import ABC, abstractmethod
from config import (
    load_config,
    is_downloaded,
    mark_downloaded,
    load_record,
    save_record,
    auto_detect_quality,
    get_enabled_subscriptions,
    QUALITY_PRESETS,
)

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)


class BaseSource(ABC):
    """订阅源抽象基类"""

    platform_name: str = "unknown"

    @abstractmethod
    def get_video_list(self, url: str) -> List[Dict[str, str]]:
        """获取视频列表，返回 [{id, title, url}]"""
        pass

    @abstractmethod
    def extract_id(self, url: str) -> str:
        """从URL提取视频ID"""
        pass


class YouTubeSource(BaseSource):
    """YouTube 订阅源"""

    platform_name = "youtube"

    def get_video_list(self, url: str) -> List[Dict[str, str]]:
        """获取频道最新视频"""
        try:
            config = load_config()

            # 第一步：获取频道信息，提取 channel URL
            cmd = _ytdlp_args(["python", "-m", "yt_dlp", "--flat-playlist", "-J", url], config)
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result.returncode != 0:
                logger.error(f"YouTube 获取失败: {result.stderr}")
                return []

            import json

            data = json.loads(result.stdout)

            # 提取 channel URL（用于拼接 /videos）
            channel_url = data.get("channel_url") or data.get("original_url") or url
            # 如果是 @handle 或 user URL，转为 /videos 路由
            if "/videos" not in channel_url:
                channel_url = channel_url.rstrip("/") + "/videos"

            # 第二步：用 /videos 路由获取真实视频列表
            cmd2 = _ytdlp_args(
                ["python", "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "10", channel_url],
                config,
            )
            result2 = subprocess.run(
                cmd2, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result2.returncode != 0:
                logger.error(f"YouTube 视频列表获取失败: {result2.stderr}")
                return []

            videos = []
            data2 = json.loads(result2.stdout)
            for entry in data2.get("entries", []) or []:
                if entry:
                    vid = entry.get("id") or ""
                    videos.append(
                        {
                            "id": vid,
                            "title": entry.get("title", "无标题"),
                            "url": entry.get("webpage_url")
                            or (f"https://youtu.be/{vid}" if vid else ""),
                        }
                    )
            return videos
        except Exception as e:
            logger.error(f"YouTube 解析异常: {e}")
            return []

    def extract_id(self, url: str) -> str:
        match = re.search(r"(?:v=|youtu\.be/)([a-zA-Z0-9_-]{11})", url)
        return match.group(1) if match else ""


class BilibiliSource(BaseSource):
    """B站订阅源"""

    platform_name = "bilibili"

    def get_video_list(self, url: str) -> List[Dict[str, str]]:
        """获取UP主最新视频"""
        try:
            config = load_config()
            cmd = _ytdlp_args(
                ["python", "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "10", url], config
            )
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result.returncode != 0:
                logger.error(f"B站 获取失败: {result.stderr}")
                return []

            import json

            data = json.loads(result.stdout)
            videos = []
            for entry in data.get("entries", []):
                if entry:
                    bvid = entry.get("id") or entry.get("display_id") or ""
                    videos.append(
                        {
                            "id": bvid,
                            "title": entry.get("title", "无标题"),
                            "url": entry.get(
                                "webpage_url", f"https://www.bilibili.com/video/{bvid}"
                            ),
                        }
                    )
            return videos
        except Exception as e:
            logger.error(f"B站 解析异常: {e}")
            return []

    def extract_id(self, url: str) -> str:
        match = re.search(r"BV[a-zA-Z0-9]{10}", url)
        return match.group(0) if match else ""


class TikTokSource(BaseSource):
    """抖音/TikTok 订阅源"""

    platform_name = "tiktok"

    def get_video_list(self, url: str) -> List[Dict[str, str]]:
        """获取用户最新视频"""
        try:
            config = load_config()
            cmd = _ytdlp_args(
                ["python", "-m", "yt_dlp", "--flat-playlist", "-J", "--playlist-end", "10", url], config
            )
            result = subprocess.run(
                cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=60
            )
            if result.returncode != 0:
                logger.error(f"TikTok 获取失败: {result.stderr}")
                return []

            import json

            data = json.loads(result.stdout)
            videos = []
            for entry in data.get("entries", []):
                if entry:
                    videos.append(
                        {
                            "id": entry.get("id", ""),
                            "title": entry.get("title", "无标题"),
                            "url": entry.get("webpage_url", ""),
                        }
                    )
            return videos
        except Exception as e:
            logger.error(f"TikTok 解析异常: {e}")
            return []

    def extract_id(self, url: str) -> str:
        match = re.search(r"/video/(\d+)", url)
        return match.group(1) if match else ""


# 注册所有平台
SOURCES: Dict[str, BaseSource] = {
    "youtube": YouTubeSource(),
    "bilibili": BilibiliSource(),
    "tiktok": TikTokSource(),
}


def sanitize_filename(title: str) -> str:
    """清理文件名非法字符"""
    return re.sub(r'[<>"/\\|?*]', "_", title)[:100]


def build_filename(platform: str, title: str, ext: str, template: str) -> str:
    """按模板生成文件名"""
    now = datetime.now()
    replacements = {
        "{platform}": platform,
        "{title}": sanitize_filename(title),
        "{year}": str(now.year),
        "{month}": str(now.month).zfill(2),
        "{day}": str(now.day).zfill(2),
        "{ext}": ext,
    }
    filename = template
    for k, v in replacements.items():
        filename = filename.replace(k, v)
    return filename


def _ytdlp_args(extra: list, config) -> list:
    """构建 yt-dlp 通用参数"""
    proxy = config.get("settings", {}).get("proxy", "")
    args = list(extra)
    if proxy:
        args.extend(["--proxy", proxy])
    return args


def download_video(url: str, platform: str, quality: str = "best") -> Optional[str]:
    """下载单个视频，返回输出路径"""
    config = load_config()
    output_dir = config.get("output_dir", "./downloads")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(
        output_dir, f"{platform}_%(title).100s_[%(upload_date)s].%(ext)s"
    )

    cmd = _ytdlp_args(
        [
            "python", "-m", "yt_dlp",
            "-f",
            quality,
            "--merge-output-format",
            "mp4",
            "-o",
            output_path,
            "--no-playlist",
            "--socket-timeout",
            "30",
            url,
        ],
        config,
    )

    logger.info(f"▶ 开始下载 [{platform}]: {url}")

    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=1800
        )
        if result.returncode == 0:
            logger.info(f"  ✓ 下载成功")
            return output_path
        else:
            stderr = result.stderr.lower()
            # 视频不可用/已删除/地区限制 → 跳过，不算失败
            if any(kw in stderr for kw in [
                "video unavailable", "is not available", "private video",
                "members only", "this video has been removed",
                "sign in to confirm your age", "geo restriction",
            ]):
                logger.warning(f"  ✗ 视频不可用，跳过: {url}")
            else:
                logger.warning(f"  ✗ 下载失败: {result.stderr[:200]}")
            return None
    except subprocess.TimeoutExpired:
        logger.error(f"  ✗ 下载超时（5分钟）")
        return None
    except Exception as e:
        logger.error(f"  ✗ 下载异常: {e}")
        return None


def run_subscription(sub: Dict[str, Any]) -> Dict[str, Any]:
    """运行单个订阅源，返回统计"""
    platform = sub["platform"]
    url = sub["url"]
    name = sub.get("name", platform)
    quality = sub.get("quality", "best")

    logger.info(f"\n{'='*50}")
    logger.info(f"📺 订阅源: {name} ({platform})")
    logger.info(f"  画质: {quality}")
    logger.info(f"{'='*50}")

    if platform not in SOURCES:
        logger.warning(f"  平台 {platform} 暂不支持")
        return {"name": name, "platform": platform, "downloaded": 0, "skipped": 0}

    source = SOURCES[platform]
    videos = source.get_video_list(url)

    if not videos:
        logger.warning(f"  获取视频列表失败")
        return {"name": name, "platform": platform, "downloaded": 0, "skipped": 0}

    logger.info(f"  发现 {len(videos)} 个视频")

    downloaded = 0
    skipped = 0

    for video in videos:
        video_id = video["id"]
        video_url = video["url"]
        video_title = video["title"]

        # 检查是否已下载
        record = load_record()
        platform_videos = record.get(platform, [])

        if video_id in platform_videos:
            logger.info(f"  → 已存在，跳过: {video_title[:40]}")
            skipped += 1
            continue

        # 下载
        result = download_video(video_url, platform, quality)

        if result:
            mark_downloaded(platform, video_id)
            downloaded += 1

    logger.info(f"  ✅ 完成: 新增 {downloaded}，跳过 {skipped}")

    return {
        "name": name,
        "platform": platform,
        "downloaded": downloaded,
        "skipped": skipped,
    }


def run_all() -> List[Dict[str, Any]]:
    """运行所有启用的订阅源"""
    import notifier

    config = load_config()
    settings = config.get("settings", {})
    proxy = settings.get("proxy", "")

    # ── 首次运行带宽检测 ─────────────────────────────────────────────────────────
    auto_preset = auto_detect_quality(proxy)

    # ── 获取全局画质设置 ─────────────────────────────────────────────────────────
    global_preset = config.get("global", {}).get("quality_preset", auto_preset)
    if global_preset not in QUALITY_PRESETS:
        logger.warning(f"无效画质预设 '{global_preset}'，回退到 'high'")
        global_preset = "high"

    logger.info(f"\n🎬 全局画质预设: {global_preset} ({QUALITY_PRESETS[global_preset]['desc']})")

    enabled = get_enabled_subscriptions(global_preset)

    if not enabled:
        logger.warning("没有启用的订阅源，请修改 sources.yaml 开启")
        return []

    logger.info(f"\n🚀 开始运行，共 {len(enabled)} 个订阅源\n")

    start_time = time.time()
    error_msg = None

    results = []
    try:
        for sub in enabled:
            result = run_subscription(sub)
            results.append(result)
    except Exception as e:
        error_msg = str(e)
        logger.error(f"下载过程出错: {e}")

    elapsed = int(time.time() - start_time)

    # 汇总
    total_dl = sum(r["downloaded"] for r in results)
    total_skip = sum(r["skipped"] for r in results)

    logger.info(f"\n{'='*50}")
    logger.info(f"📊 总计: 新增下载 {total_dl}，跳过 {total_skip}")
    logger.info(f"{'='*50}")

    # 发送微信通知（有新增下载时）
    notifier.send_notification(results, elapsed, error_msg)

    return results
