import whisper

# Load medium model
print('Loading medium model...')
model = whisper.load_model('medium')

# Transcribe
print('Transcribing...')
result = model.transcribe(r'C:\Users\60597\.qclaw\workspace\ai-video-editor\test_video2.mp4', language='zh')

# Format segments
segments = []
for seg in result['segments']:
    segments.append({
        'start': round(seg['start'], 3),
        'end': round(seg['end'], 3),
        'text': seg['text'].strip(),
    })

# Generate SRT
srt_path = r'C:\Users\60597\.qclaw\workspace\ai-video-editor\test_video2_medium.srt'
def format_time(seconds):
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f'{h:02d}:{m:02d}:{s:02d},{ms:03d}'

with open(srt_path, 'w', encoding='utf-8') as f:
    for i, seg in enumerate(segments, 1):
        f.write(f'{i}\n')
        f.write(f"{format_time(seg['start'])} --> {format_time(seg['end'])}\n")
        f.write(f"{seg['text']}\n\n")

print(f'SRT saved: {srt_path}')
print(f'Total segments: {len(segments)}')
