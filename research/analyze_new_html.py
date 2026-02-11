import re

with open("debug_2026_new.html", "r", encoding="utf-8") as f:
    html = f.read()

# 提取 Next.js 数据
pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
matches = re.findall(pattern, html)
full_text = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')

# 搜索用户提到的 "13 - 15 MAR"
print(f"Searching for '13 - 15 MAR' in reconstructed text: {full_text.find('13 - 15 MAR')}")

# 搜索所有的 Round
rounds = re.findall(r'\"roundText\":\"(.*?)\"', full_text)
print(f"Rounds found: {list(set(rounds))}")

# 导出部分数据进行人工查验
with open("reconstructed_2026.txt", "w", encoding="utf-8") as f:
    f.write(full_text)
