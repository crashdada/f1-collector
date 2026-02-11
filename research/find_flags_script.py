import re

content = open(r'c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html', encoding='utf-8').read()
# Common patterns for F1 flags
patterns = [
    r'https://media\.formula1\.com/[^"]+?flag[^"]+?\.svg',
    r'https://media\.formula1\.com/[^"]+?flag[^"]+?\.png',
    r'https://media\.formula1\.com/[^"]+?flags[^"]+?\.svg',
    r'https://media\.formula1\.com/[^"]+?flags[^"]+?\.png'
]

results = set()
for p in patterns:
    matches = re.findall(p, content)
    results.update(matches)

# Sort and print
for r in sorted(list(results)):
    print(r)
