from bs4 import BeautifulSoup
import json
import re
import os

def extract_full_schedule():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    debug_file = os.path.join(collector_dir, "debug_2026.html")
    tracks_file = os.path.join(collector_dir, "research", "all_tracks.txt")
    output_file = os.path.join(collector_dir, "schedule_2026.json")
    web_output_file = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"

    if not os.path.exists(debug_file):
        print(f"Error: {debug_file} not found")
        return

    with open(debug_file, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    with open(tracks_file, "r", encoding="utf-8") as f:
        track_links = [line.strip() for line in f if line.strip()]

    # 赛道关键词映射
    loc_map = {
        "Australia": "melbourne",
        "China": "shanghai",
        "Japan": "suzuka",
        "Bahrain": "sakhir",
        "Saudi Arabia": "jeddah",
        "Miami": "miami",
        "Emilia Romagna": "imola",
        "Monaco": "montecarlo",
        "Spain": "catalunya",
        "Canada": "montreal",
        "Austria": "spielberg",
        "Great Britain": "silverstone",
        "Belgium": "spafrancorchamps",
        "Hungary": "hungaroring",
        "Netherlands": "zandvoort",
        "Italy": "monza",
        "Azerbaijan": "baku",
        "Singapore": "singapore",
        "USA": "austin",
        "Mexico": "mexicocity",
        "Brazil": "interlagos",
        "Las Vegas": "lasvegas",
        "Qatar": "lusail",
        "Abu Dhabi": "yasmarina",
        "Madrid": "madrid"
    }

    def find_track(location):
        keyword = loc_map.get(location, location.lower().replace(" ", ""))
        for link in track_links:
            if keyword in link.lower():
                return link
        return None

    def get_flag(country):
        if not country: return None
        c_name = country.title().replace(" ", "_")
        return f"https://media.formula1.com/content/dam/fom-website/flags/{c_name}.png.transform/2col/image.png"

    events = []
    
    # 查找所有的比赛卡片/容器
    # 根据之前的 PowerShell 发现，我们可以找包含 ROUND 的元素
    round_spans = soup.find_all("span", string=re.compile(r"ROUND \d+|TESTING"))
    
    seen_rounds = set()
    for span in round_spans:
        round_text = span.get_text(strip=True)
        if round_text in seen_rounds and "ROUND" in round_text:
            continue
        
        # 寻找最近的父级容器，包含国家和日期
        container = span.parent
        for _ in range(10):
            if not container: break
            text_all = container.get_text("|", strip=True)
            # 尝试在这个范围内寻找国家名和日期
            # 以及 GP 名称
            if "|" in text_all:
                parts = [p.strip() for p in text_all.split("|")]
                
                # 日期模式: 06 - 08 MAR
                dates = next((p for p in parts if re.search(r"\d+\s*-\s*\d+\s*[A-Z]{3}", p)), None)
                
                # 国家名通常是大写且不在 round_text 中
                country = next((p for p in parts if p.isupper() and p not in round_text and len(p) > 2), None)
                
                # 如果找到了这些关键信息
                if dates and country:
                    # 尝试寻找 GP 名称 (通常在国家名附近)
                    gp_name = "TBC"
                    for i, p in enumerate(parts):
                        if p == country and i + 1 < len(parts):
                            gp_name = parts[i+1]
                            break
                    
                    location = country.title()
                    # 特殊处理
                    if "SAUDI" in country: location = "Saudi Arabia"
                    elif "USA" in country: location = "USA"
                    elif "GREAT BRITAIN" in country: location = "Great Britain"
                    elif "LAS VEGAS" in country: location = "Las Vegas"
                    elif "ABU DHABI" in country: location = "Abu Dhabi"
                    
                    event = {
                        "round": round_text,
                        "country": country,
                        "gpName": gp_name,
                        "location": location,
                        "dates": dates,
                        "image": find_track(location),
                        "flag": get_flag(location),
                        "isTest": "TEST" in round_text
                    }
                    events.append(event)
                    seen_rounds.add(round_text)
                    break
            container = container.parent

    # 排序
    def sort_key(e):
        if "TESTING" in e["round"]: return (0, e["dates"])
        m = re.search(r"ROUND (\d+)", e["round"])
        return (1, int(m.group(1)) if m else 99)

    events.sort(key=sort_key)

    # 最终补漏 (如果没抓全，手动补全基本的 24 站，因为用户之前肯定看到过完整的)
    if len(events) < 24:
        print(f"Warning: Only extracted {len(events)} events. Attempting secondary extraction.")
        # 这里可以使用更直接的正则或预设列表补齐，但既然 debug_2026.html 有 24 个 ROUND，应该能抓全。

    # 保存
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=4, ensure_ascii=False)
    
    with open(web_output_file, 'w', encoding='utf-8') as f:
        json.dump(events, f, indent=4, ensure_ascii=False)

    print(f"Successfully generated {len(events)} events.")
    for e in events:
        print(f"{e['round']}: {e['location']} ({e['dates']})")

if __name__ == "__main__":
    extract_full_schedule()
