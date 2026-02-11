import json
import re
import os

def reconstruct_and_extract():
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
    
    # Save the reconstructed text for debugging if needed
    # with open("reconstructed_debug_2026.txt", "w", encoding="utf-8") as debug_f:
    #     debug_f.write(reconstructed)

    # Search for secondaryNavigationSchedule
    start_tag = '"secondaryNavigationSchedule":['
    start_idx = reconstructed.find(start_tag)
    if start_idx == -1:
        print("Required JSON blob not found in reconstructed text.")
        # Try a broader search for any schedule-like array
        return

    content = reconstructed[start_idx + len(start_tag) - 1:]
    brace_count = 0
    end_idx = 0
    for i, char in enumerate(content):
        if char == '[': brace_count += 1
        elif char == ']': brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            break
    
    try:
        raw_schedule = json.loads(content[:end_idx])
    except Exception as e:
        print(f"JSON Parse Error: {e}")
        return
    
    # Load flags
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_flags = json.load(f)

    clean_schedule = []
    for item in raw_schedule:
        country_raw = item.get("meetingName", "")
        
        # Mapping logic
        svg_content = None
        # Try to find exactly or similar
        search_key = country_raw.lower()
        
        # Specific overrides for naming mismatches
        overrides = {
            "china": "People’s Republic of China",
            "miami": "United States of America",
            "austin": "United States of America",
            "las vegas": "United States of America",
            "united states": "United States of America",
            "abu dhabi": "United Arab Emirates",
            "great britain": "Great Britain"
        }
        
        mapped_key = overrides.get(search_key)
        if mapped_key:
            svg_content = svg_flags.get(mapped_key)
        
        if not svg_content:
            for svg_country, svg_code in svg_flags.items():
                if svg_country.lower() in search_key or search_key in svg_country.lower():
                    svg_content = svg_code
                    break
        
        clean_schedule.append({
            "round": item.get("roundText"),
            "country": country_raw.upper(),
            "gpName": item.get("meetingName").upper() + " GRAND PRIX 2026",
            "location": item.get("meetingName"),
            "dates": item.get("startAndEndDateForF1RD"),
            "isTest": item.get("isTestEvent", False),
            "flag_svg": svg_content
        })

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(clean_schedule, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully generated clean schedule with {len(clean_schedule)} rounds.")

if __name__ == "__main__":
    reconstruct_and_extract()
