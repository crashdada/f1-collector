import re

content = open('f1-collector/debug_2026.html', encoding='utf-8').read()
# Greedily find everything that looks like an F1 track SVG URL
matches = re.findall(r'https://media\.formula1\.com/[^\"]+?track/[^\"]+?\.svg', content)
unique_matches = sorted(list(set(matches)))

with open('f1-collector/all_tracks.txt', 'w', encoding='utf-8') as f:
    for m in unique_matches:
        f.write(m + '\n')
print(f"Total unique tracks found: {len(unique_matches)}")
