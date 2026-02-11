import re

with open(r"c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html", "r", encoding="utf-8") as f:
    html = f.read()

pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
matches = re.findall(pattern, html)
full_text = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')

rounds = re.findall(r'\"roundText\":\"(.*?)\"', full_text)
unique_rounds = []
for r in rounds:
    if r not in unique_rounds:
        unique_rounds.append(r)

print(f"Total round markers found in JSON: {len(rounds)}")
print("Unique rounds found:")
for ur in unique_rounds:
    print(f" - {ur}")

# Check for other meeting markers
meetings = re.findall(r'\"meetingName\":\"(.*?)\"', full_text)
unique_meetings = []
for m in meetings:
    if m not in unique_meetings:
        unique_meetings.append(m)
print(f"Total meeting markers: {len(meetings)}")
print("Unique meetings:")
for um in unique_meetings:
    print(f" - {um}")
