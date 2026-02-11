import json
import os

source = r'c:\Users\jaymz\Desktop\oc\schedule_2026_detailed.json'
target = r'c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json'

if os.path.exists(source):
    with open(source, 'r', encoding='utf-8') as f:
        data = json.load(f)
    print(f"Total entries in source: {len(data)}")
    for i, item in enumerate(data):
        print(f"{i+1}. {item.get('round')}: {item.get('gpName')} - {item.get('dates')}")
    
    # Sync to frontend
    with open(target, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Synced to {target}")
else:
    print(f"Source file not found: {source}")
