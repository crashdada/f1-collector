import re
import json
import base64
from bs4 import BeautifulSoup
import os

def extract_from_base64():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    # Find all race cards
    # They are <a> tags with data-f1rd-a7s-context
    cards = soup.find_all('a', attrs={"data-f1rd-a7s-context": True})
    
    rounds = []
    seen_rounds = set()

    for card in cards:
        b64_data = card['data-f1rd-a7s-context']
        try:
            # Decode Base64
            decoded = json.loads(base64.b64decode(b64_data).decode('utf-8'))
            
            # We only want race cards (they have raceName)
            if 'raceName' not in decoded:
                continue
            
            # Find round text: nearest span with ROUND or TESTING
            round_span = card.find(string=re.compile(r'ROUND \d+|TESTING'))
            round_text = round_span.strip() if round_span else "Unknown"
            
            # Find dates: nearest span with date pattern
            date_span = card.find(string=re.compile(r'\d+ - \d+ [A-Z]{3}'))
            dates = date_span.strip() if date_span else "TBC"
            
            country = decoded.get('trackCountry', 'Unknown')
            gp_name = decoded.get('raceName', 'Unknown')
            
            # Deduplicate by round
            if round_text in seen_rounds and round_text != "TESTING":
                continue
            
            # Special handling for TESTING: only keep if dates are not TBC if possible
            if round_text == "TESTING" and dates == "TBC" and any(r['round'] == 'TESTING' and r['dates'] != "TBC" for r in rounds):
                continue
                
            seen_rounds.add(round_text)
            
            rounds.append({
                "round": round_text,
                "country": country,
                "gpName": gp_name,
                "location": decoded.get('trackName', country),
                "dates": dates
            })
        except Exception as e:
            # print(f"Error decoding card: {e}")
            continue

    # Deduplicate by round, GP name, and dates
    unique = {}
    for r in rounds:
        key = (r['round'], r['gpName'], r['dates'])
        if key not in unique:
            unique[key] = r
    
    results = list(unique.values())
    
    # Sort
    def sort_key(x):
        if x['round'] == 'TESTING': return 0
        num = re.search(r'\d+', x['round'])
        return int(num.group(0)) if num else 99
    
    results.sort(key=sort_key)
    
    # SVG Flag mapping
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
    for r in results: # Changed from 'rounds' to 'results'
        country = r['country']
        flag = svg_map.get(country)
        if not flag:
            # Try matching parts
            for k, v in svg_map.items():
                if k in country:
                    flag = v
                    break
        
        final_schedule.append({
            "round": r['round'],
            "country": country.upper(),
            "gpName": r['gpName'].upper(),
            "location": r['location'],
            "dates": r['dates'],
            "isTest": r['round'] == 'TESTING',
            "image": None,
            "flag": flag
        })

    # Save
    out_path = os.path.join(collector_dir, "schedule_2026.json")
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)
        
    # Sync to website
    web_path = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    with open(web_path, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)
        
    return len(final_schedule)

if __name__ == "__main__":
    count = extract_from_base64()
    print(f"Successfully extracted {count} rounds.")
