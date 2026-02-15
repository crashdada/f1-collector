import json
import os

collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
drivers_json = os.path.join(collector_dir, "data", "drivers_2026.json")
assets_dir = os.path.join(collector_dir, "assets", "seasons", "2026", "drivers")

with open(drivers_json, 'r', encoding='utf-8') as f:
    drivers = json.load(f)

for d in drivers:
    code = d['code']
    first = d['firstName'].lower().replace(' ', '_')
    last = d['lastName'].lower().replace(' ', '_')
    full_name_id = f"{first}_{last}"
    
    old_file = os.path.join(assets_dir, f"{code}.webp")
    new_file = os.path.join(assets_dir, f"{full_name_id}.webp")
    
    if os.path.exists(old_file):
        print(f"Renaming {code}.webp -> {full_name_id}.webp")
        if os.path.exists(new_file):
            os.remove(new_file)
        os.rename(old_file, new_file)
    else:
        print(f"File not found for {code}: {old_file}")
