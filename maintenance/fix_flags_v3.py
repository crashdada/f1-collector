import json
import urllib.parse

# 定义赛程数据路径
schedule_path = r'c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json'

# 加载数据
with open(schedule_path, 'r', encoding='utf-8') as f:
    schedule = json.load(f)

# 经过进一步排查和常见规律，修正 404 的国家映射
# 有些国家在 F1 官网使用 .jpg 且路径不同，或者使用缩写
country_to_flag_url = {
    "AUSTRALIA": "https://media.formula1.com/content/dam/fom-website/flags/Australia.png",
    "CHINA": "https://media.formula1.com/content/dam/fom-website/flags/China.png",
    "JAPAN": "https://media.formula1.com/content/dam/fom-website/flags/Japan.png",
    "BAHRAIN": "https://media.formula1.com/content/dam/fom-website/flags/Bahrain.png",
    "SAUDI ARABIA": "https://media.formula1.com/content/dam/fom-website/flags/Saudi%20Arabia.jpg", # 改为 .jpg
    "MIAMI": "https://media.formula1.com/content/dam/fom-website/flags/United%20States.png",
    "CANADA": "https://media.formula1.com/content/dam/fom-website/flags/Canada.png",
    "MONACO": "https://media.formula1.com/content/dam/fom-website/flags/Monaco.png",
    "SPAIN": "https://media.formula1.com/content/dam/fom-website/flags/Spain.png",
    "AUSTRIA": "https://media.formula1.com/content/dam/fom-website/flags/Austria.png",
    "GREAT BRITAIN": "https://media.formula1.com/content/dam/fom-website/flags/United%20Kingdom.png",
    "BELGIUM": "https://media.formula1.com/content/dam/fom-website/flags/Belgium.png",
    "HUNGARY": "https://media.formula1.com/content/dam/fom-website/flags/Hungary.png",
    "NETHERLANDS": "https://media.formula1.com/content/dam/fom-website/flags/Netherlands.png",
    "ITALY": "https://media.formula1.com/content/dam/fom-website/flags/Italy.png",
    "AZERBAIJAN": "https://media.formula1.com/content/dam/fom-website/flags/Azerbaijan.jpg", # 改为 .jpg
    "SINGAPORE": "https://media.formula1.com/content/dam/fom-website/flags/Singapore.png",
    "UNITED STATES": "https://media.formula1.com/content/dam/fom-website/flags/United%20States.png",
    "MEXICO": "https://media.formula1.com/content/dam/fom-website/flags/Mexico.png",
    "BRAZIL": "https://media.formula1.com/content/dam/fom-website/flags/Brazil.png",
    "LAS VEGAS": "https://media.formula1.com/content/dam/fom-website/flags/United%20States.png",
    "QATAR": "https://media.formula1.com/content/dam/fom-website/flags/Qatar.png",
    "ABU DHABI": "https://media.formula1.com/content/dam/fom-website/flags/United%20Arab%20Emirates.jpg" # 改为 .jpg
}

# 更新赛程数据
for event in schedule:
    country_key = event['country'].upper()
    if country_key in country_to_flag_url:
        event['flag'] = country_to_flag_url[country_key]
    else:
        # 默认兜底逻辑
        flag_name = country_key.title()
        encoded_name = urllib.parse.quote(flag_name)
        event['flag'] = f"https://media.formula1.com/content/dam/fom-website/flags/{encoded_name}.png"

# 写回文件
with open(schedule_path, 'w', encoding='utf-8') as f:
    json.dump(schedule, f, indent=4, ensure_ascii=False)

print(f"Successfully applied FINAL flag URL corrections.")
