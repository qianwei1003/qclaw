"""
视频下载通知模块
通过 OpenClaw Gateway HTTP API 发送微信通知
"""
import urllib.request
import json
import time


GATEWAY_URL = "http://127.0.0.1:28789/tools/invoke"
GATEWAY_TOKEN = "fb0b44857f36393e9f2c4e1856a1620122d9afe7e4018e52"
GATEWAY_PORT = 28789


def format_duration(seconds: int) -> str:
    """格式化耗时为人类可读"""
    if seconds < 60:
        return f"{seconds}秒"
    elif seconds < 3600:
        return f"{seconds // 60}分钟"
    else:
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        return f"{hours}小时{minutes}分钟"


def _gateway_invoke(tool: str, action: str, args: dict) -> dict:
    """通过 Gateway HTTP API 调用工具"""
    payload = json.dumps({
        "tool": tool,
        "action": action,
        "args": args,
    }).encode("utf-8")

    req = urllib.request.Request(
        GATEWAY_URL,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {GATEWAY_TOKEN}",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=10) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        if not result.get("ok", False):
            raise Exception(f"Gateway error: {result}")
        return result.get("result", {})


def send_notification(results, elapsed_seconds: int, error_message: str = None) -> bool:
    """
    发送下载完成微信通知

    Args:
        results: run_all() 返回的结果列表
        elapsed_seconds: 总耗时（秒）
        error_message: 错误信息（可选）

    Returns:
        bool: 是否发送成功
    """
    total_downloaded = sum(r.get("downloaded", 0) for r in results)
    total_skipped = sum(r.get("skipped", 0) for r in results)

    # 没有新增下载，不发送通知
    if total_downloaded == 0:
        print("[通知] 没有新增下载，跳过通知")
        return False

    # 构建消息
    lines = ["[视频下载完成]"]

    for r in results:
        name = r.get("name", "未知")
        downloaded = r.get("downloaded", 0)
        skipped = r.get("skipped", 0)
        if downloaded > 0:
            lines.append(f"{name}: 新增 {downloaded}, 跳过 {skipped}")

    if error_message:
        lines.append(f"⚠️ 错误: {error_message}")

    duration_str = format_duration(elapsed_seconds)
    lines.append(f"总计: 新增 {total_downloaded}, 跳过 {total_skipped}, 耗时 {duration_str}")

    message = "\n".join(lines)

    # 通过 Gateway API 发送微信消息
    try:
        result = _gateway_invoke("message", "send", {
            "channel": "wechat-access",
            "target": "237004848",
            "message": message,
        })
        via = result.get("details", {}).get("via", "unknown")
        ok = result.get("details", {}).get("result", {}).get("ok", False)
        if ok or via == "direct":
            print(f"[通知] ✓ 微信发送成功 ({via})")
            return True
        else:
            print(f"[通知] ✗ 微信发送失败: {result}")
            return False
    except Exception as e:
        print(f"[通知] ✗ 微信发送失败: {e}")
        return False
