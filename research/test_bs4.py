from bs4 import BeautifulSoup
import re
import json

with open("debug_2026_new.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

events = []

# 查找所有包含 ROUND 的文本
round_texts = soup.find_all(string=re.compile(r'ROUND \d+'))
print(f"Found {len(round_texts)} potential rounds")

for rt in round_texts:
    # 查找父级容器，直到找到一个包含日期和大奖赛名字的块
    # 官网卡片通常有一个特定的类或结构
    parent = rt.parent
    # 向上查找 5 层尝试找到卡片容器
    card = None
    for _ in range(10):
        if parent is None: break
        # 如果包含 "MAR" 或 "APR" 等月份缩写，可能是找到了日期
        if re.search(r'(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)', parent.get_text()):
            card = parent
        parent = parent.parent
    
    if card:
        text = card.get_text(separator="|", strip=True)
        # 提取信息
        # 格式示例: ROUND 1|TBC|AUSTRALIA|13 - 15 MAR
        parts = text.split("|")
        
        # 尝试正则提取图像
        img = card.find("img")
        img_url = img["src"] if img and img.has_attr("src") else None
        
        # 简化处理：存入 events，后续排重
        events.append({
            "round": rt.strip(),
            "full_text": text,
            "image": img_url
        })

# 分析 events
print(f"Extracted {len(events)} events initially")

# 打印一些样本
for e in events[:5]:
    print(f" - {e['round']} | {e['full_text']}")
