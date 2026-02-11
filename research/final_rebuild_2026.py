import json
import re
import os

def final_rebuild():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    in_file = os.path.join(collector_dir, "debug_2026.html")
    svg_file = os.path.join(collector_dir, "maintenance", "flag_svgs_2026.json")
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    
    with open(in_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Reconstruct Next.js data
    pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
    matches = re.findall(pattern, html)
    reconstructed = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')
    
    # Extract all meeting names and round texts
    # Pattern: "roundText":"ROUND 1" ... "meetingName":"Australia" ... "startAndEndDateForF1RD":"13 - 15 MAR"
    # We'll use a regex to find all matches because they might be in different fragments
    
    rounds = []
    # Use a more flexible regex for individual round data
    round_matches = re.findall(r'\"roundText\":\"(ROUND \d+|TESTING)\".*?\"meetingName\":\"(.*?)\".*?\"startAndEndDateForF1RD\":\"(.*?)\"', reconstructed)
    
    # deduplicate
    seen = set()
    cleaned_rounds = []
    for r_text, m_name, d_range in round_matches:
        key = (r_text, m_name)
        if key not in seen:
            cleaned_rounds.append((r_text, m_name, d_range))
            seen.add(key)
    
    # Load flags
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_flags = json.load(f)

    # Manual mapping for countries to SVG keys
    country_to_svg_key = {
        "BAHRAIN": "Bahrain",
        "SAUDI ARABIA": "Saudi Arabia",
        "AUSTRALIA": "Australia",
        "CHINA": "People’s Republic of China",
        "JAPAN": "Japan",
        "MIAMI": "United States of America",
        "EMILIA ROMAGNA": "Italy",
        "MONACO": "Monaco",
        "SPAIN": "Spain",
        "CANADA": "Canada",
        "AUSTRIA": "Austria",
        "GREAT BRITAIN": "Great Britain",
        "BELGIUM": "Belgium",
        "HUNGARY": "Hungary",
        "NETHERLANDS": "Netherlands",
        "ITALY": "Italy",
        "AZERBAIJAN": "Azerbaijan",
        "SINGAPORE": "Singapore",
        "UNITED STATES": "United States of America",
        "MEXICO": "Mexico",
        "BRAZIL": "Brazil",
        "LAS VEGAS": "United States of America",
        "QATAR": "Qatar",
        "ABU DHABI": "United Arab Emirates"
    }

    final_schedule = []
    for r_text, m_name, d_range in cleaned_rounds:
        svg_key = country_to_svg_key.get(m_name.upper())
        if not svg_key:
            # Try partial match
            for k in country_to_svg_key:
                if k in m_name.upper():
                    svg_key = country_to_svg_key[k]
                    break
        
        svg_content = svg_flags.get(svg_key) if svg_key else None
        
        final_schedule.append({
            "round": r_text,
            "country": m_name.upper(),
            "gpName": f"FORMULA 1 {m_name.upper()} GRAND PRIX 2026",
            "location": m_name,
            "dates": d_range,
            "isTest": "TESTING" in r_text,
            "image": None,
            "flag_svg": svg_content
        })

    # Sort if possible (TESTING first, then ROUND 1..24)
    def sort_key(x):
        if x['isTest']: return 0
        m = re.search(r'ROUND (\d+)', x['round'])
        return int(m.group(1)) if m else 99

    final_schedule.sort(key=sort_key)

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, ensure_ascii=False, indent=4)
    
    print(f"Generated clean schedule with {len(final_schedule)} entries.")
    if len(final_schedule) < 24:
        print("Warning: Still missing some rounds.")

if __name__ == "__main__":
    final_rebuild()
