import re
import json
import os

def rebuild_full_24():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Search for all "roundText" occurrences
    # Example: "roundText":"ROUND 24","meetingName":"Abu Dhabi"
    # We'll use a very greedy search to find as many properties as possible for each round
    
    # Let's find all pairs of roundText and meetingName
    rounds_found = []
    # Pattern to match the core data of a race card in RSC stream
    # "roundText":"ROUND 1",...,"meetingName":"Australia",...,"startAndEndDateForF1RD":"06 - 08 MAR"
    
    # We'll regex for individual pieces and then try to associate them by proximity
    # Or find the blocks:
    blocks = re.findall(r'\{"roundText":".*?","meetingName":".*?","startAndEndDateForF1RD":".*?"\}', html)
    # The above might be too strict if there are extra keys.
    # Try finding roundText and searching forward for meetingName
    
    all_round_texts = re.finditer(r'\"roundText\":\"(ROUND \d+|TESTING)\"', html)
    
    for match in all_round_texts:
        start_pos = match.start()
        # Look ahead 1000 characters for meetingName and dates
        context = html[start_pos:start_pos+2000]
        
        m_name = re.search(r'\"meetingName\":\"(.*?)\"', context)
        d_range = re.search(r'\"startAndEndDateForF1RD\":\"(.*?)\"', context)
        
        if m_name and d_range:
            rounds_found.append({
                "round": match.group(1),
                "location": m_name.group(1),
                "dates": d_range.group(1)
            })

    # Deduplicate
    unique_rounds = {}
    for r in rounds_found:
        key = (r['round'], r['location'])
        if key not in unique_rounds:
            unique_rounds[key] = r
            
    final_list = list(unique_rounds.values())
    
    # Sorting
    def sort_key(x):
        if x['round'] == 'TESTING': return 0
        num = re.search(r'\d+', x['round'])
        return int(num.group(0)) if num else 99
    
    final_list.sort(key=sort_key)
    
    # Map flags
    svg_map = {
        "BAHRAIN": "/assets/flags/Bahrain.svg",
        "SAUDI ARABIA": "/assets/flags/Saudi_Arabia.svg",
        "AUSTRALIA": "/assets/flags/Australia.svg",
        "CHINA": "/assets/flags/China.svg",
        "JAPAN": "/assets/flags/Japan.svg",
        "MIAMI": "/assets/flags/USA.svg",
        "EMILIA ROMAGNA": "/assets/flags/Italy.svg",
        "MONACO": "/assets/flags/Monaco.svg",
        "SPAIN": "/assets/flags/Spain.svg",
        "CANADA": "/assets/flags/Canada.svg",
        "AUSTRIA": "/assets/flags/Austria.svg",
        "GREAT BRITAIN": "/assets/flags/Great_Britain.svg",
        "BELGIUM": "/assets/flags/Belgium.svg",
        "HUNGARY": "/assets/flags/Hungary.svg",
        "NETHERLANDS": "/assets/flags/Netherlands.svg",
        "ITALY": "/assets/flags/Italy.svg",
        "AZERBAIJAN": "/assets/flags/Azerbaijan.svg",
        "SINGAPORE": "/assets/flags/Singapore.svg",
        "USA": "/assets/flags/USA.svg",
        "UNITED STATES": "/assets/flags/USA.svg",
        "MEXICO": "/assets/flags/Mexico.svg",
        "BRAZIL": "/assets/flags/Brazil.svg",
        "LAS VEGAS": "/assets/flags/USA.svg",
        "QATAR": "/assets/flags/Qatar.svg",
        "ABU DHABI": "/assets/flags/UAE.svg"
    }
    
    enriched = []
    for r in final_list:
        loc = r['location']
        flag = svg_map.get(loc.upper())
        if not flag:
            for k, v in svg_map.items():
                if k in loc.upper():
                    flag = v
                    break
        
        enriched.append({
            "round": r['round'],
            "country": loc.upper(),
            "gpName": f"FORMULA 1 {loc.upper()} GRAND PRIX 2026",
            "location": loc,
            "dates": r['dates'],
            "isTest": r['round'] == 'TESTING',
            "image": None,
            "flag": flag
        })

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(enriched, f, ensure_ascii=False, indent=4)
        
    print(f"Extraction complete: Found {len(enriched)} unique rounds.")

if __name__ == "__main__":
    rebuild_full_24()
