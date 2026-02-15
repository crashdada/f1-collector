import json
import os

data_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector\data"

# 1. 修复车手数据 (使用 code 而不是 id 作为图片文件名)
drivers_file = os.path.join(data_dir, "drivers_2026.json")
if os.path.exists(drivers_file):
    with open(drivers_file, 'r', encoding='utf-8') as f:
        drivers = json.load(f)
    
    for d in drivers:
        # 使用 code (如 LEC, HAM) 作为文件名，这与 assets 目录下的文件一致
        d['image'] = f"/photos/seasons/2026/drivers/{d['code']}.webp"
        
    with open(drivers_file, 'w', encoding='utf-8') as f:
        json.dump(drivers, f, ensure_ascii=False, indent=4)
    print(f"Fixed {drivers_file} to use CODE-based filenames (e.g. LEC.webp)")

# 2. 确保车队数据也指向正确的本地路径
teams_file = os.path.join(data_dir, "teams_2026.json")
if os.path.exists(teams_file):
    with open(teams_file, 'r', encoding='utf-8') as f:
        teams = json.load(f)
    
    for t in teams:
        tid = t['id']
        t['logo'] = f"/photos/seasons/2026/teams/{tid}_logo.webp"
        t['carImage'] = f"/photos/seasons/2026/teams/{tid}_car.webp"
            
    with open(teams_file, 'w', encoding='utf-8') as f:
        json.dump(teams, f, ensure_ascii=False, indent=4)
    print(f"Verified {teams_file}")
