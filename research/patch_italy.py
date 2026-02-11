import json
import os

def patch_italy():
    filepath = r'c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json'
    if os.path.exists(filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for race in data:
            if race.get('slug') == 'italy':
                race['gmtOffset'] = '+02:00'
                if 'circuitSpecs' not in race:
                    race['circuitSpecs'] = {}
                race['circuitSpecs']['record'] = '1:20.901 (Lando Norris, 2025)'
                print("Patched Italy in website data.")
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
            
    # Also patch collector
    collector_path = r'c:\Users\jaymz\Desktop\oc\f1-collector\schedule_2026.json'
    if os.path.exists(collector_path):
        with open(collector_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for race in data:
            if race.get('slug') == 'italy':
                race['gmtOffset'] = '+02:00'
                if 'circuitSpecs' not in race:
                    race['circuitSpecs'] = {}
                race['circuitSpecs']['record'] = '1:20.901 (Lando Norris, 2025)'
                print("Patched Italy in collector data.")
        
        with open(collector_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

if __name__ == "__main__":
    patch_italy()
