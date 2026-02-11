import re

with open("reconstructed_2026.txt", "r", encoding="utf-8") as f:
    text = f.read()

matches = list(re.finditer(r'\"roundText\":\"ROUND 1\"', text))
print(f"Total ROUND 1 matches: {len(matches)}")

for i, m in enumerate(matches):
    print(f"\n--- Match {i} at {m.start()} ---")
    chunk = text[m.start()-500 : m.start()+1000]
    print(chunk)
