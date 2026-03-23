"""
Windows Scheduled Task Manager - Video Downloader

Usage:
    python scheduler.py --install   # Create scheduled task
    python scheduler.py --remove   # Remove scheduled task
    python scheduler.py --status   # Check task status
"""
import os
import sys
import subprocess
import argparse
import yaml
from pathlib import Path
from datetime import datetime


# Constants
TASK_NAME = "VideoDownloader_AutoRun"
SCRIPT_DIR = Path(__file__).parent.resolve()
RUN_PY = SCRIPT_DIR / "run.py"
SOURCES_YAML = SCRIPT_DIR / "sources.yaml"
LOG_FILE = SCRIPT_DIR / "downloader.log"


def _run_cmd(cmd, **kwargs):
    """Run command with safe encoding fallback"""
    defaults = {"capture_output": True}
    defaults.update(kwargs)
    if "encoding" not in kwargs and "errors" not in kwargs:
        defaults["encoding"] = "cp936"
        defaults["errors"] = "replace"
    elif "text" not in kwargs:
        defaults["text"] = True
    return subprocess.run(cmd, **defaults)


def load_interval_hours():
    """Read check interval (hours) from sources.yaml"""
    try:
        with open(SOURCES_YAML, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)
        interval = config.get("settings", {}).get("check_interval_hours", 6)
        return max(1, min(24, int(interval)))
    except Exception as e:
        print(f"[WARN] Failed to read config, using default 6h: {e}")
        return 6


def install_task():
    """Create Windows scheduled task using schtasks command"""
    print(f"[INSTALL] Creating scheduled task: {TASK_NAME}")

    interval_hours = load_interval_hours()
    print(f"   Interval: every {interval_hours} hour(s)")

    # Check if task already exists
    result = _run_cmd(["schtasks", "/Query", "/TN", TASK_NAME])
    if result.returncode == 0:
        print(f"[WARN] Task exists, removing old one...")
        _run_cmd(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])

    # Build command: powershell -X utf8 python script
    # Use a wrapper that logs output
    run_py_str = str(RUN_PY)
    log_file_str = str(LOG_FILE)
    
    # PowerShell command to run python and tee output
    ps_command = f"python -X utf8 \"{run_py_str}\" 2>&1 | Tee-Object -FilePath \"{log_file_str}\" -Append"
    
    # For intervals < 24 hours, use /SC HOURLY
    if interval_hours < 24:
        # schtasks /SC HOULY /MO N - every N hours
        cmd = [
            "schtasks", "/Create",
            "/TN", TASK_NAME,
            "/SC", "HOURLY",
            "/MO", str(interval_hours),
            "/TR", f'powershell.exe -ExecutionPolicy Bypass -Command "{ps_command}"',
            "/F"  # Force create (overwrite if exists)
        ]
    else:
        # For 24+ hours, use /SC DAILY
        cmd = [
            "schtasks", "/Create",
            "/TN", TASK_NAME,
            "/SC", "DAILY",
            "/MO", "1",
            "/TR", f'powershell.exe -ExecutionPolicy Bypass -Command "{ps_command}"',
            "/F"
        ]

    print(f"   Command: {' '.join(cmd[:6])}...")
    print(f"   Log: {LOG_FILE}")

    result = _run_cmd(cmd)

    if result.returncode == 0:
        print(f"[OK] Task created successfully!")
        print(f"   Task name: {TASK_NAME}")
        print(f"   Interval: every {interval_hours} hour(s)")
        print(f"   Log file:  {LOG_FILE}")
        
        # Show next run time
        status_result = _run_cmd(["schtasks", "/Query", "/TN", TASK_NAME, "/FO", "LIST"])
        if status_result.returncode == 0:
            for line in status_result.stdout.split("\n"):
                if "Next Run Time" in line:
                    print(f"   {line.strip()}")
        return True
    else:
        print(f"[ERROR] Failed to create task: {result.stderr or result.stdout}")
        return False


def remove_task():
    """Delete Windows scheduled task"""
    print(f"[REMOVE] Deleting scheduled task: {TASK_NAME}")

    result = _run_cmd(["schtasks", "/Delete", "/TN", TASK_NAME, "/F"])

    if result.returncode == 0:
        print(f"[OK] Task deleted")
        return True
    else:
        err = result.stderr or result.stdout or ""
        if "cannot find" in err.lower() or "not found" in err.lower():
            print(f"[INFO] Task does not exist, nothing to remove")
            return True
        print(f"[ERROR] Failed to delete task: {err}")
        return False


def get_task_status():
    """Query and display task status"""
    print(f"[STATUS] Task: {TASK_NAME}")
    print("-" * 60)

    result = _run_cmd(["schtasks", "/Query", "/TN", TASK_NAME, "/V", "/FO", "LIST"])

    if result.returncode != 0:
        print(f"[ERROR] Task not found or query failed")
        print(f"   Hint: run 'python scheduler.py --install' to create it")
        return None

    lines = result.stdout.split("\n")
    status_info = {}
    for line in lines:
        if ":" in line:
            key, value = line.split(":", 1)
            status_info[key.strip()] = value.strip()

    # Display key fields
    print(f"  Task Name:        {TASK_NAME}")

    for label, candidates in [
        ("Status", ["Status", "状态"]),
        ("Last Run", ["Last Run Time", "上次运行时间"]),
        ("Last Result", ["Last Result", "上次运行结果"]),
        ("Next Run", ["Next Run Time", "下次运行时间"]),
    ]:
        for cand in candidates:
            for key in status_info:
                if cand.lower() in key.lower():
                    print(f"  {label}: {status_info[key]}")
                    break

    print("-" * 60)

    interval_hours = load_interval_hours()
    print(f"[CONFIG]")
    print(f"  Check interval: every {interval_hours} hour(s)")
    print(f"  Script:        {RUN_PY}")
    print(f"  Log file:      {LOG_FILE}")

    return status_info


def main():
    parser = argparse.ArgumentParser(
        description="Windows Scheduled Task Manager - Video Downloader",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Examples:\n"
            "  python scheduler.py --install   # Create scheduled task\n"
            "  python scheduler.py --remove    # Remove scheduled task\n"
            "  python scheduler.py --status    # Check task status\n"
        ),
    )

    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--install", action="store_true", help="Create scheduled task"
    )
    group.add_argument(
        "--remove", action="store_true", help="Remove scheduled task"
    )
    group.add_argument(
        "--status", action="store_true", help="Check task status"
    )

    args = parser.parse_args()

    if sys.platform != "win32":
        print("[ERROR] This script only supports Windows")
        sys.exit(1)

    if args.install:
        # Warn if not admin
        try:
            import ctypes
            if not ctypes.windll.shell32.IsUserAnAdmin():
                print("[WARN] Administrator privileges recommended for task creation")
        except Exception:
            pass

    if args.install:
        success = install_task()
    elif args.remove:
        success = remove_task()
    else:  # --status
        status = get_task_status()
        success = status is not None

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
