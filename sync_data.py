import json
import os

COLLECTOR_DIR = r'c:\Users\jaymz\Desktop\oc\f1-collector'
WEBSITE_DIR = r'c:\Users\jaymz\Desktop\oc\f1-website'

def sync_file(filename):
    source = os.path.join(COLLECTOR_DIR, filename)
    target = os.path.join(WEBSITE_DIR, 'src', 'data', filename)
    
    if os.path.exists(source):
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        with open(target, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Successfully synced {filename} ({len(data)} entries) to {target}")
    else:
        print(f"Source not found: {source}")

if __name__ == "__main__":
    print("Starting 2026 Data Sync...")
    sync_file('schedule_2026.json')
    sync_file('drivers_2026.json')
    print("Sync process complete.")
