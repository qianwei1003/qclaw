"""
视频下载框架 - 配置模块
"""
import os
import yaml
import time
import subprocess
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional

CONFIG_PATH = Path(__file__).parent / "sources.yaml"
RECORD_FILE = Path(__file__).parent / "downloaded.json"
STATE_FILE  = Path(__file__).parent / "state.json"

logger = logging.getLogger(__name__)

# ── 画质预设映射 ──────────────────────────────────────────────────────────────
QUALITY_PRESETS: Dict[str, Dict[str, Any]] = {
    "ultra": {
        "desc": "4K/原画 (bestvideo[height<=2160]+bestaudio)",
        "yt_dlp":  "bestvideo[height<=2160]+bestaudio/best",
        "bilibili": "超清 4K",
    },
    "high": {
        "desc": "1080P (bestvideo[height<=1080]+bestaudio)",
        "yt_dlp":  "bestvideo[height<=1080]+bestaudio/best",
        "bilibili": "超清 108P",
    },
    "medium": {
        "desc": "720P (bestvideo[height<=720]+bestaudio)",
        "yt_dlp":  "bestvideo[height<=720]+bestaudio/best",
        "bilibili": "高清 720P",
    },
    "fast": {
        "desc": "720P 单文件 (best[height<=720])",
        "yt_dlp":  "best[height<=720]/best",
        "bilibili": "高清 720P",
    },
}

VALID_PRESETS = list(QUALITY_PRESETS.keys())


def _state() -> Dict[str, Any]:
    """加载/初始化状态文件"""
    if STATE_FILE.exists():
        import json
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def _save_state(state: Dict[str, Any]) -> None:
    import json
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


# ── 代理测速 ──────────────────────────────────────────────────────────────────
def _proxy_speed_kbs(proxy: str) -> float:
    """通过下载一个小文件测试代理带宽 (KB/s)，失败返回 0"""
    test_url = "http://httpbin.org/bytes/102400"  # 100KB 测试文件
    try:
        cmd = [
            "python", "-m", "yt_dlp",
            "--no-playlist",
            "--quiet",
            "--print", "progress",
            "-o", os.devnull,
        ]
        if proxy:
            cmd += ["--proxy", proxy]
        cmd.append(test_url)

        start = time.time()
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            encoding="utf-8",
            timeout=30,
        )
        elapsed = max(time.time() - start, 0.1)
        if result.returncode == 0:
            return 1024 / elapsed  # KB/s
    except Exception as e:
        logger.debug(f"测速失败: {e}")
    return 0.0


def auto_detect_quality(proxy: str = "") -> str:
    """首次运行检测带宽，返回推荐 preset。已确认过则缓存结果。"""
    state = _state()

    if state.get("bandwidth_check_done"):
        cached = state.get("auto_quality", "high")
        logger.info(f"代理带宽已确认: {cached} 模式 (缓存)")
        return cached

    logger.info("首次运行，检测代理带宽...")
    speed = _proxy_speed_kbs(proxy)
    logger.info(f"  测速结果: {speed:.1f} KB/s")

    if speed > 0 and speed < 500:
        recommended = "fast"
        logger.info(f"  带宽 <500 KB/s，自动切换到 'fast' 模式")
    else:
        recommended = "high"
        logger.info(f"  带宽正常，使用 'high' 模式")

    state["bandwidth_check_done"] = True
    state["auto_quality"] = recommended
    state["last_speed_kbs"] = round(speed, 1)
    _save_state(state)

    return recommended


# ── 画质解析 ──────────────────────────────────────────────────────────────────
def resolve_quality(quality_raw: Any, global_preset: str, platform: str) -> str:
    """
    统一画质字符串：
    - 如果 channel 显式写了 preset 名 ("ultra"/"high"…) → 对应 yt-dlp 格式
    - 如果写了 yt-dlp 原始格式字符串 → 直接透传
    - 如果为空 → fallback 到 global preset
    """
    if not quality_raw:
        quality_raw = global_preset

    q = str(quality_raw).strip().lower()

    # 1. 命中 preset 名
    if q in QUALITY_PRESETS:
        preset = QUALITY_PRESETS[q]
        if platform == "bilibili":
            return preset["bilibili"]
        return preset["yt_dlp"]

    # 2. yt-dlp 原始格式字符串（包含 bestvideo / best 等关键词）
    if any(k in q for k in ["bestvideo", "best", "bv", "bestaudio"]):
        return quality_raw  # 原样透传

    # 3. B站中文画质描述
    if "4k" in q or "超清" in q:
        return QUALITY_PRESETS["ultra"]["bilibili"]
    if "108" in q or "原画" in q or "超清" in q:
        return QUALITY_PRESETS["high"]["bilibili"]
    if "720" in q or "高清" in q:
        return QUALITY_PRESETS["medium"]["bilibili"]

    # 4. 兜底
    return QUALITY_PRESETS["high"]["yt_dlp"]


# ── YAML 配置读写 ─────────────────────────────────────────────────────────────
def load_config() -> Dict[str, Any]:
    if not CONFIG_PATH.exists():
        raise FileNotFoundError(f"配置文件不存在: {CONFIG_PATH}")
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_record() -> Dict[str, List[str]]:
    if not RECORD_FILE.exists():
        return {}
    import json
    with open(RECORD_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_record(record: Dict[str, List[str]]) -> None:
    import json
    with open(RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(record, f, ensure_ascii=False, indent=2)


def is_downloaded(platform: str, video_id: str) -> bool:
    record = load_record()
    return video_id in record.get(platform, [])


def mark_downloaded(platform: str, video_id: str) -> None:
    record = load_record()
    if platform not in record:
        record[platform] = []
    if video_id not in record[platform]:
        record[platform].append(video_id)
    save_record(record)


def get_enabled_subscriptions(global_preset: str = "high") -> List[Dict[str, Any]]:
    """获取所有已启用的订阅源，统一 resolution quality 字符串。"""
    config = load_config()
    enabled = []
    for platform, subs in config.get("subscriptions", {}).items():
        for sub in subs:
            if sub.get("enabled", False):
                resolved = resolve_quality(
                    sub.get("quality"), global_preset, platform
                )
                enabled.append({**sub, "platform": platform, "quality": resolved})
    return enabled
