import re

countries = [
    "Australia", "China", "Japan", "Bahrain", "Saudi Arabia", "Miami", "Canada", 
    "Monaco", "Spain", "Austria", "Great Britain", "Belgium", "Hungary", 
    "Netherlands", "Italy", "Azerbaijan", "Singapore", "USA", "Mexico", 
    "Brazil", "Las Vegas", "Qatar", "Abu Dhabi"
]

file_path = r'c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html'
with open(file_path, encoding='utf-8') as f:
    content = f.read()

all_media = re.findall(r'https://media\.formula1\.com/[^"]+?\.(?:png|svg|jpg)', content)
unique_media = set(all_media)

for country in countries:
    name = country.replace(" ", "_")
    matches = [m for m in unique_media if name.lower() in m.lower() or country.lower().replace(" ", "") in m.lower().replace("_", "")]
    if matches:
        print(f"--- {country} ---")
        for m in sorted(matches):
            print(m)
