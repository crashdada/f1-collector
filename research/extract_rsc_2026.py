import re
import json
import base64
import os

def extract_schedule_from_rsc():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Extract Next.js RSC fragments
    # self.__next_f.push([1,"..."])
    fragments = re.findall(r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)', content)
    
    # 2. Concatenate and unescape
    full_rsc = "".join(fragments).replace('\\"', '"').replace('\\\\', '\\')
    
    # 3. Look for Base64 segments or direct JSON
    # Often RSC has JSON mixed with Base64.
    # Let's search for the "secondaryNavigationSchedule" key
    
    # Sometimes it's just raw text in the RSC stream
    # Let's search for the rounds directly in the reconstructed RSC
    rounds = []
    
    # Pattern for rounds: "roundText":"ROUND 1","meetingName":"Australia"
    # We might need to handle extra escaping
    pattern = r'\"roundText\":\"(ROUND \d+|TESTING)\".*?\"meetingName\":\"(.*?)\".*?\"startAndEndDateForF1RD\":\"(.*?)\"'
    
    matches = re.finditer(pattern, full_rsc)
    for match in matches:
        rounds.append({
            "round": match.group(1),
            "location": match.group(2),
            "dates": match.group(3)
        })

    # Deduplicate
    unique = {}
    for r in rounds:
        key = (r['round'], r['location'])
        if key not in unique:
            unique[key] = r
    
    results = list(unique.values())
    
    # Sort
    def sort_key(x):
        if x['round'] == 'TESTING': return 0
        num = re.search(r'\d+', x['round'])
        return int(num.group(0)) if num else 99
    
    results.sort(key=sort_key)
    
    if not results:
        print("No rounds found in reconstructed RSC stream. Trying alternative search...")
        # Try searching for the Base64 chunks that might contain the JSON
        # Example: "a7s-context":"..." contains Base64
        # We saw Base64 in the manual search too.
        
        # Searching for meetingName in the whole file
        all_meetings = re.findall(r'\"meetingName\":\"(.*?)\"', content)
        print(f"Found {len(all_meetings)} raw meetingName occurrences.")
        
    return results

if __name__ == "__main__":
    rounds = extract_schedule_from_rsc()
    if rounds:
        print(f"Successfully found {len(rounds)} rounds.")
        for r in rounds:
            print(f"{r['round']}: {r['location']} ({r['dates']})")
        
        # Mapping flags
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
        for r in rounds:
            loc = r['location']
            flag = svg_map.get(loc.upper())
            if not flag:
                for k, v in svg_map.items():
                    if k in loc.upper():
                        flag = v
                        break
            
            # Special case for Emilia Romagna (Italy)
            if "Emilia" in loc: flag = "/assets/flags/Italy.svg"
            
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
            
        with open("schedule_2026.json", 'w', encoding='utf-8') as f:
            json.dump(enriched, f, indent=4, ensure_ascii=False)
        
        # Also sync to website
        web_path = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
        with open(web_path, 'w', encoding='utf-8') as f:
            json.dump(enriched, f, indent=4, ensure_ascii=False)
        print(f"Saved to {web_path}")
    else:
        print("Extraction failed.")
