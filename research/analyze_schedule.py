import re

with open("debug_2026_schedule.html", "r", encoding="utf-8") as f:
    html = f.read()

# 提取 Next.js 数据
pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
matches = re.findall(pattern, html)
full_text = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')

# 搜索所有的 Round
rounds = re.findall(r'\"roundText\":\"(ROUND \d+)\"', full_text)
unique_rounds = sorted(list(set(rounds)), key=lambda x: int(re.search(r'\d+', x).group(0)))
print(f"Unique Rounds found: {unique_rounds}")

# 如果找到了更多的 round，打印部分信息
if unique_rounds:
    for r in unique_rounds[:5]:
        r_pos = full_text.find(f'\"roundText\":\"{r}\"')
        chunk = full_text[r_pos-100 : r_pos+500]
        name = re.search(r'\"meetingName\":\"(.*?)\"', chunk)
        country = re.search(r'\"meetingCountryName\":\"(.*?)\"', chunk)
        date = re.search(r'\"startAndEndDateForF1RD\":\"(.*?)\"', chunk)
        print(f" - {r}: {name.group(1) if name else 'N/A'}, {country.group(1) if country else 'N/A'}, {date.group(1) if date else 'N/A'}")
