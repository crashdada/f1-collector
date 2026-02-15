import json
import os

data_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector\data"

# 1. 修复车手数据
drivers_file = os.path.join(data_dir, "drivers_2026.json")
if os.path.exists(drivers_file):
    with open(drivers_file, 'r', encoding='utf-8') as f:
        drivers = json.load(f)
    
    for d in drivers:
        # 使用 ID 作为文件名
        d['image'] = f"/photos/seasons/2026/drivers/{d['id']}.webp"
        
    with open(drivers_file, 'w', encoding='utf-8') as f:
        json.dump(drivers, f, ensure_ascii=False, indent=4)
    print(f"Fixed {drivers_file}")

# 2. 检查并修复车队数据 (防止遗漏)
teams_file = os.path.join(data_dir, "teams_2026.json")
if os.path.exists(teams_file):
    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    for t in teams:
        tid = t['id']
        if "https://" in str(t.get('logo', '')):
            t['logo'] = f"/photos/seasons/2026/teams/{tid}_logo.webp"
        if "https://" in str(t.get('carImage', '')):
            t['carImage'] = f"/photos/seasons/2026/teams/{tid}_car.webp"
            
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=4)
    print(f"Fixed {teams_file}")
