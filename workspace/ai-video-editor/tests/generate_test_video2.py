#!/usr/bin/env python3
"""生成测试视频：包含真正的静音段"""

import subprocess
import os

output = r"C:\Users\admin\.qclaw\workspace\ai-video-editor\tests\test_silence_video2.mp4"

# 生成方案：5秒有声音 + 3秒静音 + 5秒有声音 + 3秒静音 + 5秒有声音
# 使用 anullsrc 生成真正的静音

# 先创建5秒有声音的片段（不同颜色方便识别）
fragments = []

# 1. 蓝色 + 声音 (0-5秒)
f1 = output.replace('.mp4', '_1.mp4')
fragments.append(f1)

# 2. 黑色 + 静音 (5-8秒) - 用 anullsrc 生成真正静音
f2 = output.replace('.mp4', '_2.mp4')
fragments.append(f2)

# 3. 红色 + 声音 (8-13秒)
f3 = output.replace('.mp4', '_3.mp4')
fragments.append(f3)

# 4. 绿色 + 静音 (13-16秒)
f4 = output.replace('.mp4', '_4.mp4')
fragments.append(f4)

# 5. 黄色 + 声音 (16-21秒)
f5 = output.replace('.mp4', '_5.mp4')
fragments.append(f5)

# 创建片段1: 蓝色画面 + 440Hz声音
cmd1 = f'ffmpeg -f lavfi -i "color=blue:s=320x240:d=5" -f lavfi -i "sine=frequency=440:duration=5" -shortest -y "{f1}"'

# 创建片段2: 黑色画面 + 静音（真正无声，用 anullsrc）
cmd2 = f'ffmpeg -f lavfi -i "color=black:s=320x240:d=3" -f lavfi -i "anullsrc=channel_layout=mono:sample_rate=44100" -shortest -y "{f2}"'

# 创建片段3: 红色画面 + 880Hz声音
cmd3 = f'ffmpeg -f lavfi -i "color=red:s=320x240:d=5" -f lavfi -i "sine=frequency=880:duration=5" -shortest -y "{f3}"'

# 创建片段4: 绿色画面 + 静音
cmd4 = f'ffmpeg -f lavfi -i "color=green:s=320x240:d=3" -f lavfi -i "anullsrc=channel_layout=mono:sample_rate=44100" -shortest -y "{f4}"'

# 创建片段5: 黄色画面 + 660Hz声音
cmd5 = f'ffmpeg -f lavfi -i "color=yellow:s=320x240:d=5" -f lavfi -i "sine=frequency=660:duration=5" -shortest -y "{f5}"'

print("生成测试视频...")
print("结构：5秒有声(蓝) + 3秒静音(黑) + 5秒有声(红) + 3秒静音(绿) + 5秒有声(黄) = 21秒")
print()

for i, (name, cmd) in enumerate([("1-蓝+声音", cmd1), ("2-黑+静音", cmd2), ("3-红+声音", cmd3), ("4-绿+静音", cmd4), ("5-黄+声音", cmd5)], 1):
    print(f"生成片段 {name}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')
    if result.returncode != 0:
        print(f"  错误: {result.stderr[-150:]}")
    else:
        print(f"  OK")

# 合并
print("\n合并片段...")
concat_file = output.replace('.mp4', '_list.txt')
with open(concat_file, 'w', encoding='utf-8') as f:
    for frag in fragments:
        f.write(f"file '{frag.replace(chr(92), '/')}'\n")

merge_cmd = f'ffmpeg -f concat -safe 0 -i "{concat_file}" -c copy -y "{output}"'
result = subprocess.run(merge_cmd, shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace')

if result.returncode == 0:
    # 清理
    for f in fragments + [concat_file]:
        if os.path.exists(f):
            os.remove(f)
    print("完成！")
    
    # 验证
    result = subprocess.run(
        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{output}"',
        shell=True, capture_output=True, text=True, encoding='utf-8', errors='replace'
    )
    if result.returncode == 0:
        print(f"\n输出视频时长: {result.stdout.strip()} 秒")
else:
    print(f"合并错误: {result.stderr[-200:]}")
