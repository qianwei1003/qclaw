import urllib.request
import ssl

# 忽略 SSL 验证
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

url = "https://tdesign.tencent.com/chat/getting-started"
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

req = urllib.request.Request(url, headers=headers)

print("正在请求...")
try:
    with urllib.request.urlopen(req, context=ctx, timeout=30) as response:
        html = response.read().decode('utf-8')
        print(f"状态码: {response.status}")
        print(f"内容长度: {len(html)}")
        print("\n--- 前 2000 字符 ---")
        print(html[:2000])
        
        # 保存到文件
        with open('tdesign_page.html', 'w', encoding='utf-8') as f:
            f.write(html)
        print("\n已保存到 tdesign_page.html")
except Exception as e:
    print(f"错误: {e}")
