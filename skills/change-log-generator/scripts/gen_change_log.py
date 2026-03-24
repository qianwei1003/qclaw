#!/usr/bin/env python3
# language: python
"""
gen_change_log.py
生成改动档案（Markdown）到 docs/change-logs/

用法示例：
  python gen_change_log.py
  python gen_change_log.py --base origin/main --task ZD#1234
  python gen_change_log.py --base origin/main --task ZD#1234 --output docs/change-logs

说明：
- 默认基线为 origin/main（如果不存在，将使用 HEAD^）
- 不会自动 git add/commit，生成后在控制台打印路径与摘要
"""
import argparse
import os
import subprocess
import sys
from datetime import datetime
import shutil
import re

def run(cmd):
    return subprocess.check_output(cmd, shell=True, universal_newlines=True).strip()

def safe_run(cmd):
    try:
        return run(cmd)
    except subprocess.CalledProcessError:
        return ""

def ensure_output_dir(path):
    os.makedirs(path, exist_ok=True)

def get_current_branch():
    branch = safe_run("git rev-parse --abbrev-ref HEAD")
    if branch == "HEAD":
        # detached, use short commit
        branch = safe_run("git rev-parse --short HEAD")
    return branch

def commits_summary(base, head='HEAD', max_count=20):
    out = safe_run(f"git log --pretty=format:%h\\ %s {base}..{head} --max-count={max_count}")
    if not out:
        out = safe_run(f"git log --pretty=format:%h\\ %s {head} --max-count={max_count}")
    return out.splitlines()

def name_status_list(base, head='HEAD'):
    out = safe_run(f"git diff --name-status {base}..{head}")
    lines = []
    if out:
        for l in out.splitlines():
            parts = l.split("\t")
            if len(parts) >= 2:
                status = parts[0]
                path = parts[-1]
                lines.append((status, path))
    return lines

def parse_unified_diff_hunks(base, head='HEAD'):
    # returns dict: file -> list of (start_line,end_line, change_type)
    diff = safe_run(f"git diff --unified=0 {base}..{head}")
    files = {}
    cur_file = None
    for line in diff.splitlines():
        if line.startswith("diff --git"):
            m = re.search(r"a/(.+?)\s+b/(.+)$", line)
            if m:
                # use b/ path as target path
                cur_file = m.group(2)
                files[cur_file] = []
        elif line.startswith("@@") and cur_file:
            # @@ -l,s +l,s @@
            m = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,(\d+))? @@", line)
            if m:
                start = int(m.group(1))
                count = int(m.group(2)) if m.group(2) else 1
                if count == 0:
                    # deletion in new file
                    end = start
                else:
                    end = start + count - 1
                files[cur_file].append((start, end))
    return files

def generate_markdown(task, branch, timestamp, commits, name_status, hunks, base, head):
    time_str = timestamp.strftime("%Y-%m-%d %H:%M:%S")
    filename_title = task if task else branch
    header = f"# {filename_title} 改动档案\n\n"
    header += f"- 生成时间：{time_str}\n"
    header += f"- 分支/范围：{branch} ({base}..{head})\n\n"
    header += "## 改动摘要\n\n"
    if commits:
        header += "最近提交：\n\n"
        for c in commits:
            header += f"- {c}\n"
    else:
        header += "_无 commit 摘要_\n"
    header += "\n## 改动文件\n\n"
    if name_status:
        header += "| 类型 | 文件 | 行号范围 |\n"
        header += "|---|---|---|\n"
        for status, path in name_status:
            ranges = hunks.get(path, [])
            if ranges:
                ranges_str = ", ".join([f"{s}-{e}" for s,e in ranges])
            else:
                ranges_str = "-"
            header += f"| {status} | {path} | {ranges_str} |\n"
    else:
        header += "_无文件变更_\n"
    header += "\n## 改动原因\n\n- （请填写改动原因，关联禅道/任务/描述）\n\n"
    header += "## 关联任务 / Issue\n\n- （示例：ZD#1234）\n\n"
    header += "## 测试要点\n\n- （请列出验证步骤）\n\n"
    header += "## 被检测但跳过的建议（占位）\n\n- （例如：UserList.vue:23 建议 v-show（已记录，未改动））\n\n"
    header += "## 备注\n\n- 本文档由 gen_change_log.py 自动生成。如需补充，请编辑并提交到仓库 docs/change-logs/。\n"
    return header

def safe_filename(text):
    return re.sub(r"[^0-9A-Za-z._-]", "-", text)

def main():
    parser = argparse.ArgumentParser(description="生成改动档案 Markdown 到 docs/change-logs/")
    parser.add_argument("--base", "-b", default="origin/main", help="比较基线（默认 origin/main）")
    parser.add_argument("--head", default="HEAD", help="比较目标（默认 HEAD）")
    parser.add_argument("--task", "-t", default="", help="任务号（可选，例如 ZD#1234），将写入文件名与文档头")
    parser.add_argument("--output", "-o", default="docs/change-logs", help="输出目录（默认 docs/change-logs）")
    args = parser.parse_args()

    # verify git repository
    if not os.path.isdir(".git"):
        print("当前目录不是 git 仓库（未找到 .git），请在仓库根目录运行脚本。")
        sys.exit(1)

    branch = get_current_branch()
    timestamp = datetime.now()

    # if base doesn't exist, fallback
    if not safe_run(f"git rev-parse --verify {args.base}"):
        # try HEAD^
        args.base = safe_run("git rev-parse --verify HEAD^") or args.base

    commits = commits_summary(args.base, args.head)
    name_status = name_status_list(args.base, args.head)
    hunks = parse_unified_diff_hunks(args.base, args.head)

    ensure_output_dir(args.output)

    safe_task = args.task if args.task else branch
    file_ts = timestamp.strftime("%Y%m%dT%H%M%S")
    safe_branch = safe_filename(safe_task)
    filename = f"{safe_branch}-{file_ts}.md"
    out_path = os.path.join(args.output, filename)

    md = generate_markdown(args.task, branch, timestamp, commits, name_status, hunks, args.base, args.head)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)

    print(f"已生成改动档案：{out_path}")
    print("摘要：")
    print(f"- 分支: {branch}")
    print(f"- 基线: {args.base}")
    print(f"- 改动文件数: {len(name_status)}")
    print(f"- 输出文件: {out_path}")
    print("请手动补充『改动原因』『测试要点』等信息并提交该文档。")

if __name__ == "__main__":
    main()