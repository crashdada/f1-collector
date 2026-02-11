import json
import os

# 定义赛程数据路径
schedule_path = r'c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json'

# 加载数据
with open(schedule_path, 'r', encoding='utf-8') as f:
    schedule = json.load(f)

# 国家与国旗图片的映射规律
# 注意：有些国家名称在 URL 中可能需要特殊处理，比如空格转下划线或连字符
# 根据官网规律，通常是 Country.png
country_to_flag = {
    "AUSTRALIA": "Australia",
    "CHINA": "China",
    "JAPAN": "Japan",
    "BAHRAIN": "Bahrain",
    "SAUDI ARABIA": "Saudi_Arabia",
    "MIAMI": "United_States", # 迈阿密站使用美国国旗
    "CANADA": "Canada",
    "MONACO": "Monaco",
    "SPAIN": "Spain",
    "AUSTRIA": "Austria",
    "GREAT BRITAIN": "Great_Britain",
    "BELGIUM": "Belgium",
    "HUNGARY": "Hungary",
    "NETHERLANDS": "Netherlands",
    "ITALY": "Italy",
    "AZERBAIJAN": "Azerbaijan",
    "SINGAPORE": "Singapore",
    "UNITED STATES": "United_States",
    "MEXICO": "Mexico",
    "BRAZIL": "Brazil",
    "LAS VEGAS": "United_States", # 拉斯维加斯使用美国国旗
    "QATAR": "Qatar",
    "ABU DHABI": "United_Arab_Emirates"
}

# 更新赛程数据
for event in schedule:
    country_key = event['country'].upper()
    flag_name = country_to_flag.get(country_key, country_key.title().replace(' ', '_'))
    event['flag'] = f"https://media.formula1.com/content/dam/fom-website/flags/{flag_name}.png"

# 写回文件
with open(schedule_path, 'w', encoding='utf-8') as f:
    json.dump(schedule, f, indent=4, ensure_ascii=False)

print(f"Successfully updated {len(schedule)} events with flag URLs.")
