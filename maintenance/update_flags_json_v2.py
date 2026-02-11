import json
import urllib.parse

# 定义赛程数据路径
schedule_path = r'c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json'

# 加载数据
with open(schedule_path, 'r', encoding='utf-8') as f:
    schedule = json.load(f)

# 国家与国旗图片的映射规律
# 经过排查，URL 中应该使用空格（或 %20），下划线会导致 404
country_to_flag_name = {
    "AUSTRALIA": "Australia",
    "CHINA": "China",
    "JAPAN": "Japan",
    "BAHRAIN": "Bahrain",
    "SAUDI ARABIA": "Saudi Arabia",
    "MIAMI": "United States",
    "CANADA": "Canada",
    "MONACO": "Monaco",
    "SPAIN": "Spain",
    "AUSTRIA": "Austria",
    "GREAT BRITAIN": "United Kingdom", # 重点修正
    "BELGIUM": "Belgium",
    "HUNGARY": "Hungary",
    "NETHERLANDS": "Netherlands",
    "ITALY": "Italy",
    "AZERBAIJAN": "Azerbaijan",
    "SINGAPORE": "Singapore",
    "UNITED STATES": "United States",
    "MEXICO": "Mexico",
    "BRAZIL": "Brazil",
    "LAS VEGAS": "United States",
    "QATAR": "Qatar",
    "ABU DHABI": "United Arab Emirates" # 重点修正
}

# 更新赛程数据
for event in schedule:
    country_key = event['country'].upper()
    flag_name = country_to_flag_name.get(country_key, country_key.title())
    
    # URL 编码空格为 %20
    encoded_name = urllib.parse.quote(flag_name)
    event['flag'] = f"https://media.formula1.com/content/dam/fom-website/flags/{encoded_name}.png"

# 写回文件
with open(schedule_path, 'w', encoding='utf-8') as f:
    json.dump(schedule, f, indent=4, ensure_ascii=False)

print(f"Successfully updated {len(schedule)} events with CORRECT flag URLs.")
