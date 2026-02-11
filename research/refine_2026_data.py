import re
import json
import base64
from bs4 import BeautifulSoup
import os

def refine_extraction():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # 1. Find all race cards
    cards = soup.find_all('a', attrs={"data-f1rd-a7s-context": True})
    
    # Also find track SVGs
    # Pattern: https://media.formula1.com/image/upload/c_lfill,w_3392/v1740000000/common/f1/2026/track/2026tracksuzukablackoutline.svg
    # These are usually in style="mask-image:url(...)" in a span inside the card
    
    rounds = []
    seen_rounds = set()

    for card in cards:
        b64_data = card['data-f1rd-a7s-context']
        try:
            decoded = json.loads(base64.b64decode(b64_data).decode('utf-8'))
            if 'raceName' not in decoded:
                continue
            
            round_span = card.find(string=re.compile(r'ROUND \d+|TESTING'))
            round_text = round_span.strip() if round_span else "Unknown"
            
            date_span = card.find(string=re.compile(r'\d+ - \d+ [A-Z]{3}'))
            dates = date_span.strip() if date_span else "TBC"
            
            country = decoded.get('trackCountry', 'Unknown')
            gp_name = decoded.get('raceName', 'Unknown')
            
            # Find track SVG in this card
            track_svg = None
            span_with_bg = card.find('span', style=re.compile(r'mask-image:url'))
            if span_with_bg:
                match = re.search(r'url\((.*?)\)', span_with_bg['style'])
                if match:
                    track_svg = match.group(1)

            # Deduplicate
            if round_text in seen_rounds and round_text != "TESTING":
                continue
            
            if round_text == "TESTING" and dates == "TBC" and any(r['round'] == 'TESTING' and r['dates'] != "TBC" for r in rounds):
                continue
            
            seen_rounds.add(round_text)
            
            rounds.append({
                "round": round_text,
                "country": country,
                "gpName": gp_name,
                "location": decoded.get('trackName', country),
                "dates": dates,
                "trackImage": track_svg
            })
        except:
            continue

    # Sort
    def sort_key(x):
        if x['round'] == 'TESTING': return 0
        num = re.search(r'\d+', x['round'])
        return int(num.group(0)) if num else 99
    
    rounds.sort(key=sort_key)
    
    # Flag mapping
    svg_map = {
        "Bahrain": "/assets/flags/Bahrain.svg",
        "Saudi Arabia": "/assets/flags/Saudi_Arabia.svg",
        "Australia": "/assets/flags/Australia.svg",
        "China": "/assets/flags/China.svg",
        "Japan": "/assets/flags/Japan.svg",
        "United States": "/assets/flags/USA.svg",
        "USA": "/assets/flags/USA.svg",
        "Miami": "/assets/flags/USA.svg",
        "Las Vegas": "/assets/flags/USA.svg",
        "Italy": "/assets/flags/Italy.svg",
        "Emilia Romagna": "/assets/flags/Italy.svg",
        "Monaco": "/assets/flags/Monaco.svg",
        "Spain": "/assets/flags/Spain.svg",
        "Barcelona": "/assets/flags/Spain.svg",
        "Canada": "/assets/flags/Canada.svg",
        "Austria": "/assets/flags/Austria.svg",
        "Great Britain": "/assets/flags/Great_Britain.svg",
        "Belgium": "/assets/flags/Belgium.svg",
        "Hungary": "/assets/flags/Hungary.svg",
        "Netherlands": "/assets/flags/Netherlands.svg",
        "Azerbaijan": "/assets/flags/Azerbaijan.svg",
        "Singapore": "/assets/flags/Singapore.svg",
        "Mexico": "/assets/flags/Mexico.svg",
        "Brazil": "/assets/flags/Brazil.svg",
        "Qatar": "/assets/flags/Qatar.svg",
        "Lusail": "/assets/flags/Qatar.svg",
        "Abu Dhabi": "/assets/flags/UAE.svg",
        "United Arab Emirates": "/assets/flags/UAE.svg"
    }

    final_schedule = []
    for r in rounds:
        country = r['country']
        flag = svg_map.get(country)
        if not flag:
            for k, v in svg_map.items():
                if k in country:
                    flag = v
                    break
        
        final_schedule.append({
            "round": r['round'],
            "country": country.upper(),
            "gpName": r['gpName'], # Keep original for translation lookup
            "location": r['location'],
            "dates": r['dates'],
            "isTest": r['round'] == 'TESTING',
            "image": r['trackImage'],
            "flag": flag
        })

    # Save
    with open("schedule_2026.json", 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)
    
    # Output GP names for translation updating
    all_gps = sorted(list(set(r['gpName'] for r in final_schedule)))
    print("GP Names found:")
    for gp in all_gps:
        print(f'"{gp}": "",')

    # Sync to website
    web_path = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    with open(web_path, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)
        
    return len(final_schedule)

if __name__ == "__main__":
    count = refine_extraction()
    print(f"Refined extraction complete. Saved {count} rounds.")
