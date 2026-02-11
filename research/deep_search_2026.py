import re

with open("reconstructed_2026.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Search for dates
dates_to_find = [
    "20 - 22 MAR", # China
    "03 - 05 APR", # Japan
    "10 - 12 APR", # Bahrain
    "17 - 19 APR", # Saudi
]

for d in dates_to_find:
    pos = text.find(d)
    print(f"Searching for '{d}': {'Found' if pos != -1 else 'Not Found'}")
    if pos != -1:
        print(f"Context: {text[pos-200 : pos+200]}\n")

# Search for meetingName "TBC" specifically since the screenshot showed it
tbc_matches = list(re.finditer(r'\"meetingName\":\"TBC\"', text))
print(f"Total 'meetingName':'TBC' found: {len(tbc_matches)}")
for m in tbc_matches[:3]:
    print(f"TBC at {m.start()}: {text[m.start()-100 : m.start()+200]}")
