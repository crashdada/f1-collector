import re

file_path = r'c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

# Search for flag pattern or country icons
# Usually they look like: https://media.formula1.com/content/dam/fom-website/flags/Australia.png
# Or circular versions: Australia.png.transform/2col/image.png

# Let's find all media URLs
all_media = re.findall(r'https://media\.formula1\.com/[^"]+?\.(?:png|svg|jpg)', content)
unique_media = sorted(list(set(all_media)))

# Filter for flags
flags = [m for m in unique_media if 'flag' in m.lower() or 'country' in m.lower()]

for f in flags:
    print(f)

# Also check for Australia specific images
australia_images = [m for m in unique_media if 'australia' in m.lower()]
print("\nAustralia related images:")
for ai in australia_images:
    print(ai)
