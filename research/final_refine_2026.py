import re
import json
import base64
from bs4 import BeautifulSoup
import os

def final_refine():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "research", "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')

    cards = soup.find_all('a', attrs={"data-f1rd-a7s-context": True})
    
    rounds = []
    seen_rounds = set()

    for card in cards:
        b64_data = card['data-f1rd-a7s-context']
        try:
            decoded = json.loads(base64.b64decode(b64_data).decode('utf-8'))
            if 'raceName' not in decoded:
                continue
            
            # Find round text
            round_span = card.find(string=re.compile(r'ROUND \d+|TESTING'))
            round_text = round_span.strip() if round_span else "Unknown"
            
            # Find dates - look more broadly in the card
            # The dates are usually in a sibling or descendant of the round span
            dates = "TBC"
            # Find dates - look more broadly in the card
            # Using get_text() to search the entire text content of the card
            card_text = card.get_text(separator=" ", strip=True)
            dates = "TBC"
            # Prioritize mixed-case dates like "13 - 15 Mar"
            # We search for any date pattern and then pick the best one
            all_date_matches = re.findall(r'\d{2} - \d{2} [a-zA-Z]{3}', card_text)
            if all_date_matches:
                # Prioritize those with lowercase letters (e.g., Mar instead of MAR)
                mixed_case = [d for d in all_date_matches if any(c.islower() for c in d)]
                if mixed_case:
                    dates = mixed_case[0]
                else:
                    dates = all_date_matches[0]
            
            country = decoded.get('trackCountry', 'Unknown')
            gp_name = decoded.get('raceName', 'Unknown')
            
            # Track SVG
            track_svg = None
            span_with_bg = card.find('span', style=re.compile(r'mask-image:url'))
            if span_with_bg:
                match = re.search(r'url\((.*?)\)', span_with_bg['style'])
                if match:
                    track_svg = match.group(1)

            # Deduplication logic
            if round_text in seen_rounds and round_text != "TESTING":
                continue
            
            # For TESTING, only keep if it has unique dates or GP name
            if round_text == "TESTING":
                key = (round_text, gp_name, dates)
                if key in seen_rounds:
                    continue
                seen_rounds.add(key)
            else:
                seen_rounds.add(round_text)
            
            rounds.append({
                "round": round_text,
                "country": country,
                "gpName": gp_name,
                "location": decoded.get('trackName', country),
                "dates": dates,
                "image": track_svg
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

    # Deduplicate and clean
    final_rounds = []
    seen_rounds = set()
    
    # Track pattern lookup
    track_lookup = {
        "AUSTRALIA": "melbourne",
        "CHINA": "shanghai",
        "JAPAN": "suzuka",
        "BAHRAIN": "sakhir",
        "SAUDI ARABIA": "jeddah",
        "MIAMI": "miami",
        "CANADA": "montreal",
        "MONACO": "montecarlo",
        "BARCELONA": "catalunya",
        "AUSTRIA": "spielberg",
        "GREAT BRITAIN": "silverstone",
        "BELGIUM": "spafrancorchamps",
        "HUNGARY": "hungaroring",
        "NETHERLANDS": "zandvoort",
        "ITALY": "monza",
        "SPAIN": "madrid",
        "AZERBAIJAN": "baku",
        "SINGAPORE": "singapore",
        "UNITED STATES": "austin",
        "MEXICO": "mexicocity",
        "BRAZIL": "interlagos",
        "LAS VEGAS": "lasvegas",
        "QATAR": "lusail",
        "ABU DHABI": "yasmarinacircuit",
        "SPAIN": "madring"
    }

    def get_track_url(country, gp_name, existing):
        # 1. 优先使用我们验证过的 Slug 映射表
        key = country.upper()
        if key in track_lookup:
            slug = track_lookup[key]
            if slug is None:
                return None
        else:
            slug = None
            for k, v in track_lookup.items():
                if k and (k in gp_name.upper() or k in country.upper()):
                    slug = v
                    break
        
        if "BARCELONA" in gp_name.upper(): slug = "catalunya"
        if "EMILIA" in gp_name.upper(): slug = "imola"

        if slug:
            return f"https://media.formula1.com/image/upload/c_lfill,w_3392/v1740000000/common/f1/2026/track/2026track{slug}blackoutline.svg"
        
        return existing if existing and (".svg" in existing or ".webp" in existing) else None

    def get_detailed_track_url(country, gp_name):
        key = country.upper()
        slug = track_lookup.get(key)
        if not slug:
            for k, v in track_lookup.items():
                if k and (k in gp_name.upper() or k in country.upper()):
                    slug = v
                    break
        
        if "BARCELONA" in gp_name.upper(): slug = "catalunya"
        if "EMILIA" in gp_name.upper(): slug = "imola"

        if slug:
            # 使用用户提供的彩色大图模式
            return f"https://media.formula1.com/image/upload/c_fit,h_704/q_auto/v1740000000/common/f1/2026/track/2026track{slug}detailed.webp"
        return None

    # Regex for extracting hidden session data from RSC
    session_data = re.findall(r'\"sessionName\":\"(.*?)\".*?\"startTime\":\"(.*?)\"', soup.get_text())
    slug_data = re.findall(r'\"meetingSlug\":\"(.*?)\"', soup.get_text())
    # Group sessions by round (heuristic: 5 sessions per round)
    all_sessions_raw = []
    for name, start in session_data:
        all_sessions_raw.append({"name": name, "time": start})
    
    # Meeting slugs mapping
    unique_slugs = []
    seen_slugs = set()
    for s in slug_data:
        if s not in seen_slugs:
            unique_slugs.append(s)
            seen_slugs.add(s)

    circuit_specs = {
        "melbourne": {"length": "5.278km", "laps": 58, "record": "1:20.235 (Leclerc)", "first_gp": 1996, "distance": "306.124km"},
        "shanghai": {"length": "5.451km", "laps": 56, "record": "1:32.238 (Schumacher)", "first_gp": 2004, "distance": "305.066km"},
        "suzuka": {"length": "5.807km", "laps": 53, "record": "1:30.983 (Hamilton)", "first_gp": 1987, "distance": "307.471km"},
        "sakhir": {"length": "5.412km", "laps": 57, "record": "1:31.447 (De la Rosa)", "first_gp": 2004, "distance": "308.238km"},
        "jeddah": {"length": "6.174km", "laps": 50, "record": "1:30.734 (Hamilton)", "first_gp": 2021, "distance": "308.450km"},
        "miami": {"length": "5.412km", "laps": 57, "record": "1:29.708 (Verstappen)", "first_gp": 2022, "distance": "308.326km"},
        "montreal": {"length": "4.361km", "laps": 70, "record": "1:13.078 (Bottas)", "first_gp": 1978, "distance": "305.270km"},
        "montecarlo": {"length": "3.337km", "laps": 78, "record": "1:12.909 (Hamilton)", "first_gp": 1950, "distance": "260.286km"},
        "catalunya": {"length": "4.657km", "laps": 66, "record": "1:16.330 (Verstappen)", "first_gp": 1991, "distance": "307.236km"},
        "spielberg": {"length": "4.318km", "laps": 71, "record": "1:05.619 (Sainz)", "first_gp": 1964, "distance": "306.452km"},
        "silverstone": {"length": "5.891km", "laps": 52, "record": "1:27.097 (Verstappen)", "first_gp": 1950, "distance": "306.198km"},
        "spafrancorchamps": {"length": "7.004km", "laps": 44, "record": "1:46.286 (Bottas)", "first_gp": 1950, "distance": "308.052km"},
        "hungaroring": {"length": "4.381km", "laps": 70, "record": "1:16.627 (Hamilton)", "first_gp": 1986, "distance": "306.630km"},
        "zandvoort": {"length": "4.259km", "laps": 72, "record": "1:11.097 (Hamilton)", "first_gp": 1952, "distance": "306.587km"},
        "monza": {"length": "5.793km", "laps": 53, "record": "1:21.046 (Barrichello)", "first_gp": 1950, "distance": "306.720km"},
        "baku": {"length": "6.003km", "laps": 51, "record": "1:43.009 (Leclerc)", "first_gp": 2016, "distance": "306.049km"},
        "singapore": {"length": "4.940km", "laps": 62, "record": "1:35.867 (Hamilton)", "first_gp": 2008, "distance": "306.143km"},
        "austin": {"length": "5.513km", "laps": 56, "record": "1:36.169 (Leclerc)", "first_gp": 2012, "distance": "308.405km"},
        "mexicocity": {"length": "4.304km", "laps": 71, "record": "1:17.774 (Bottas)", "first_gp": 1963, "distance": "305.354km"},
        "interlagos": {"length": "4.309km", "laps": 71, "record": "1:10.540 (Bottas)", "first_gp": 1973, "distance": "305.879km"},
        "lasvegas": {"length": "6.201km", "laps": 50, "record": "1:34.876 (Piastri)", "first_gp": 2023, "distance": "309.958km"},
        "lusail": {"length": "5.419km", "laps": 57, "record": "1:24.319 (Verstappen)", "first_gp": 2021, "distance": "308.611km"},
        "yasmarinacircuit": {"length": "5.281km", "laps": 58, "record": "1:26.103 (Verstappen)", "first_gp": 2009, "distance": "306.183km"},
        "madring": {"length": "5.47km", "laps": 0, "record": "N/A", "first_gp": 2026, "distance": "306.32km"}
    }

    gmt_offsets = {
        "AUSTRALIA": "+11:00",
        "CHINA": "+08:00",
        "JAPAN": "+09:00",
        "BAHRAIN": "+03:00",
        "SAUDI ARABIA": "+03:00",
        "MIAMI": "-04:00",
        "CANADA": "-04:00",
        "MONACO": "+02:00",
        "BARCELONA": "+02:00",
        "AUSTRIA": "+02:00",
        "GREAT BRITAIN": "+01:00",
        "BELGIUM": "+02:00",
        "HUNGARY": "+02:00",
        "NETHERLANDS": "+02:00",
        "ITALY": "+02:00",
        "SPAIN": "+02:00",
        "AZERBAIJAN": "+04:00",
        "SINGAPORE": "+08:00",
        "UNITED STATES": "-05:00",
        "MEXICO": "-06:00",
        "BRAZIL": "-03:00",
        "LAS VEGAS": "-07:00",
        "QATAR": "+03:00",
        "ABU DHABI": "+04:00"
    }

    final_rounds = []
    seen_rounds = set()
    
    # Heuristic: Match sessions to rounds by name/order
    session_idx = 0
    slug_idx = 0

    for i, r in enumerate(rounds):
        rt = r['round']
        country_upper = r['country'].upper()
        # 显式移除季前测试
        if rt == "TESTING":
            continue

        if rt != "TESTING":
            if rt in seen_rounds: continue
            seen_rounds.add(rt)

        round_num = 0
        if "ROUND" in rt:
            round_num = int(re.search(r'\d+', rt).group(0))

        # Assign Slug
        slug = r['country'].lower().replace(" ", "-")
        if slug_idx < len(unique_slugs):
            slug = unique_slugs[slug_idx]
            slug_idx += 1
        
        # Override for testing
        if rt == "TESTING": slug = "pre-season-testing-1" if "1" in r['gpName'] else "pre-season-testing-2"

        # Assign Sessions (typically 5 per GP)
        my_sessions = []
        if rt != "TESTING" and session_idx + 5 <= len(all_sessions_raw):
            my_sessions = all_sessions_raw[session_idx:session_idx+5]
            session_idx += 5
        elif rt == "TESTING" and session_idx + 1 <= len(all_sessions_raw):
            my_sessions = [all_sessions_raw[session_idx]]
            session_idx += 1

        # Track Spec
        track_key = track_lookup.get(country_upper, "")
        specs = circuit_specs.get(track_key, {})

        final_rounds.append({
            "round": rt,
            "roundNumber": round_num,
            "country": country_upper,
            "gpName": r['gpName'],
            "location": r['location'],
            "dates": r['dates'],
            "slug": slug,
            "isTest": rt == 'TESTING',
            "image": get_track_url(r['country'], r['gpName'], r['image']),
            "detailedImage": get_detailed_track_url(r['country'], r['gpName']),
            "flag": svg_map.get(r['country']) or next((v for k,v in svg_map.items() if k in r['country']), None),
            "sessions": my_sessions,
            "circuitSpecs": specs,
            "gmtOffset": gmt_offsets.get(country_upper, "Z")
        })

    # Final Sort
    def final_sort(x):
        if x['round'] == 'TESTING': return 0 if "1" in x['gpName'] else 1
        return int(re.search(r'\d+', x['round']).group(0)) + 2

    final_rounds.sort(key=final_sort)

    # Save
    with open("schedule_2026.json", 'w', encoding='utf-8') as f:
        json.dump(final_rounds, f, indent=4, ensure_ascii=False)
    
    web_dest = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    with open(web_dest, 'w', encoding='utf-8') as f:
        json.dump(final_rounds, f, indent=4, ensure_ascii=False)
        
    return len(final_rounds)

if __name__ == "__main__":
    count = final_refine()
    print(f"Final refinement complete. Processed {count} rounds.")
