import re
import json

with open("reconstructed_2026.txt", "r", encoding="utf-8") as f:
    text = f.read()

# 提取所有的 meeting 对象片段
# 通常 meeting 对象以 {"meetingCode":...} 开始
# 或者包含 "meetingName" 和 "meetingCountryName"
# 我们寻找包含 meetingName 的 JSON 片段

meetings = []
# 寻找所有的 "meetingName" : "..."
matches = re.finditer(r'\"meetingName\":\"(.*?)\"', text)

for m in matches:
    name = m.group(1)
    start = m.start()
    # 取前后 1000 字符
    chunk = text[start-500 : start+1500]
    
    # 尝试找到对应的 Round 和 Date
    round_val = re.search(r'\"roundText\":\"(.*?)\"', chunk)
    country = re.search(r'\"meetingCountryName\":\"(.*?)\"', chunk)
    date = re.search(r'\"startAndEndDateForF1RD\":\"(.*?)\"', chunk)
    
    meetings.append({
        "name": name,
        "round": round_val.group(1) if round_val else "N/A",
        "country": country.group(1) if country else "N/A",
        "date": date.group(1) if date else "N/A",
        "pos": start
    })

# 去重
unique_meetings = []
seen = set()
for m in meetings:
    key = (m["name"], m["date"])
    if key not in seen:
        unique_meetings.append(m)
        seen.add(key)

print(f"Total unique meetings found: {len(unique_meetings)}")
for i, m in enumerate(unique_meetings):
    print(f"{i+1}. {m['round']} | {m['name']} | {m['country']} | {m['date']}")
