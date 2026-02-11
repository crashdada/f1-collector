import json
import re
import os

def extract_full_and_map():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    in_file = os.path.join(collector_dir, "debug_2026.html")
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    
    with open(in_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # Pattern for Next.js fragments
    pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
    matches = re.findall(pattern, html)
    reconstructed = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')
    
    # Search for all rounds. We look for the patterns of "roundText" and "meetingName"
    # Note: These might be in a large array or spread out.
    # We'll extract everything that looks like a race entry.
    
    # Regex to find meeting data blocks: {"roundText":"...", "meetingName":"...", ...}
    # Using a non-greedy catch for the meeting block
    items = re.findall(r'\{"roundText":"(ROUND \d+|TESTING)","meetingName":"(.*?)"(?:,"meetingSponsor":".*?")?,"startAndEndDateForF1RD":"(.*?)"\}', reconstructed)
    
    # Deduplicate by (Round, MeetingName)
    seen = {}
    for r_text, m_name, d_range in items:
        key = (r_text, m_name)
        if key not in seen:
            seen[key] = d_range
            
    # Convert to list and sort
    final_list = []
    for (r_text, m_name), d_range in seen.items():
        # Map to local SVG filename
        # Mapping logic consistent with generate_flag_assets.py
        country_norm = m_name.upper()
        filename_map = {
            "CHINA": "China",
            "MIAMI": "USA",
            "AUSTIN": "USA",
            "LAS VEGAS": "USA",
            "UNITED STATES": "USA",
            "ABU DHABI": "UAE",
            "EMILIA ROMAGNA": "Italy",
            "SAUDI ARABIA": "Saudi_Arabia",
            "GREAT BRITAIN": "Great_Britain"
        }
        
        flag_filename = filename_map.get(country_norm)
        if not flag_filename:
            # Fallback for complex names
            if "CHINA" in country_norm: flag_filename = "China"
            elif "STATES" in country_norm: flag_filename = "USA"
            elif "ABU DHABI" in country_norm: flag_filename = "UAE"
            else:
                flag_filename = m_name.replace(" ", "_")
        
        flag_url = f"/assets/flags/{flag_filename}.svg"
        
        final_list.append({
            "round": r_text,
            "country": m_name.upper(),
            "gpName": f"FORMULA 1 {m_name.upper()} GRAND PRIX 2026",
            "location": m_name,
            "dates": d_range,
            "isTest": "TESTING" in r_text,
            "image": None,
            "flag": flag_url # Using a consistent field name for the website
        })

    def sort_key(x):
        if x['isTest']: return 0
        m = re.search(r'ROUND (\d+)', x['round'])
        return int(m.group(1)) if m else 99

    final_list.sort(key=sort_key)

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(final_list, f, ensure_ascii=False, indent=4)
    
    print(f"Extracted {len(final_list)} rounds.")
    if len(final_list) < 24:
        print("Still missing some rounds. Searching broader...")
        # Check if we can find more meetingNames
        all_meetings = re.findall(r'"meetingName":"(.*?)"', reconstructed)
        print(f"Total meetingNames found: {len(set(all_meetings))}")

if __name__ == "__main__":
    extract_full_and_map()
