#!/usr/bin/env python3
"""生成测试视频：包含声音段和静音段"""

import subprocess
import os

# 方案：用 ffmpeg 生成一个测试视频
# 结构：5秒有声音 + 3秒静音 + 5秒有声音 + 3秒静音 + 5秒有声音 = 21秒

output = __import__('os').path.join(os.path.dirname(os.path.abspath(__file__)), "test_silence_video.mp4")

# 使用 amovie 和 aconcatenate 来创建静音段
# 更简单的方法：先生成有声音的，再合成

# 第一步：生成有声音的片段
cmd1 = r'''ffmpeg -f lavfi -i "sine=frequency=440:duration=5" -f lavfi -i "color=blue:s=320x240:d=5" -shortest -y ''' + output.replace('.mp4', '_temp1.mp4')

# 第二步：生成静音片段（纯音频，无声音）
cmd2 = r'''ffmpeg -f lavfi -i "anullsrc=r=44100:cl=mono" -f lavfi -i "color=black:s=320x240:d=3" -shortest -y ''' + output.replace('.mp4', '_temp2.mp4')

# 第三步：生成有声音的片段
cmd3 = r'''ffmpeg -f lavfi -i "sine=frequency=880:duration=5" -f lavfi -i "color=red:s=320x240:d=5" -shortest -y ''' + output.replace('.mp4', '_temp3.mp4')

# 第四步：生成静音片段
cmd4 = r'''ffmpeg -f lavfi -i "anullsrc=r=44100:cl=mono" -f lavfi -i "color=green:s=320x240:d=3" -shortest -y ''' + output.replace('.mp4', '_temp4.mp4')

# 第五步：生成有声音的片段
cmd5 = r'''ffmpeg -f lavfi -i "sine=frequency=660:duration=5" -f lavfi -i "color=yellow:s=320x240:d=5" -shortest -y ''' + output.replace('.mp4', '_temp5.mp4')

# 打印命令
print("生成测试视频...")
print("结构：5秒有声音 + 3秒静音 + 5秒有声音 + 3秒静音 + 5秒有声音 = 21秒")
print()

for i, cmd in enumerate([cmd1, cmd2, cmd3, cmd4, cmd5], 1):
    print(f"生成片段 {i}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"错误: {result.stderr[-200:]}")
    else:
        print(f"  OK")

# 合并所有片段
concat_list = output.replace('.mp4', '_list.txt')
with open(concat_list, 'w') as f:
    for i in range(1, 6):
        temp_file = output.replace('.mp4', f'_temp{i}.mp4')
        f.write(f"file '{temp_file.replace(chr(92), '/')}'\n")

print("\n合并片段...")
cmd_merge = f'ffmpeg -f concat -safe 0 -i "{concat_list}" -c copy -y "{output}"'
result = subprocess.run(cmd_merge, shell=True, capture_output=True, text=True)

if result.returncode == 0:
    # 清理临时文件
    for i in range(1, 6):
        temp_file = output.replace('.mp4', f'_temp{i}.mp4')
        if os.path.exists(temp_file):
            os.remove(temp_file)
    if os.path.exists(concat_list):
        os.remove(concat_list)
    print("完成！")
else:
    print(f"错误: {result.stderr[-300:]}")

# 验证
print("\n验证输出...")
result = subprocess.run(
    f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{output}"',
    shell=True, capture_output=True, text=True
)
if result.returncode == 0:
    print(f"输出视频时长: {result.stdout.strip()} 秒")
