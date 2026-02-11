from bs4 import BeautifulSoup
import re
import json

with open("debug_2026_new.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")

# 寻找所有包含 ROUND 的文本
rounds = soup.find_all(string=re.compile(r'ROUND \d+'))
print(f"Total ROUND markers: {len(rounds)}")

all_found = []
for r in rounds:
    # 向上找容器，直到包含日期或到达一定深度
    p = r.parent
    found_date = None
    for _ in range(12):
        if not p: break
        t = p.get_text()
        date_m = re.search(r'\d+ - \d+ [A-Z]{3}', t)
        if date_m:
            found_date = date_m.group(0)
            break
        p = p.parent
    
    if p:
        all_found.append({
            "round": r.strip(),
            "date": found_date,
            "text": p.get_text(separator="|", strip=True)[:200]
        })

# 去重并展示
unique = []
seen = set()
for a in all_found:
    key = (a["round"], a["date"])
    if key not in seen:
        unique.append(a)
        seen.add(key)

print(f"Unique markers with dates: {len(unique)}")
for u in unique:
    print(f" - {u['round']} | {u['date']} | {u['text']}")
