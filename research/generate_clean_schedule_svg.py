import json
import re
import os

def clean_extract_2026():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    in_file = os.path.join(collector_dir, "debug_2026.html")
    svg_file = os.path.join(collector_dir, "maintenance", "flag_svgs_2026.json")
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    
    # 1. Read the debug HTML
    with open(in_file, 'r', encoding='utf-8') as f:
        html = f.read()

    # 2. Find the secondaryNavigationSchedule JSON blob
    # It's hidden in the next_f fragment or script tags
    # Let's search for the pattern
    start_tag = '"secondaryNavigationSchedule":['
    start_idx = html.find(start_tag)
    if start_idx == -1:
        print("Required JSON blob not found.")
        return

    content = html[start_idx + len(start_tag) - 1:]
    brace_count = 0
    end_idx = 0
    for i, char in enumerate(content):
        if char == '[': brace_count += 1
        elif char == ']': brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            break
    
    raw_schedule = json.loads(content[:end_idx])
    
    # 3. Load the captured SVG flags
    with open(svg_file, 'r', encoding='utf-8') as f:
        svg_flags = json.load(f)

    # 4. Map and Clean
    clean_schedule = []
    # Country name mapping for specific cases in the SVG titles
    name_map = {
        "People’s Republic of China": "China",
        "United States of America": "United States",
        "United Arab Emirates": "Abu Dhabi", # Or wherever the race is
        "Great Britain": "Great Britain"
    }
    
    for item in raw_schedule:
        # Standardize country for mapping
        country_raw = item.get("meetingName", "")
        # The SVG titles are things like "Flag of Bahrain"
        # The schedule has meetingName like "Bahrain", "China", etc.
        
        # Find the matching SVG
        svg_content = None
        for svg_country, svg_code in svg_flags.items():
            if svg_country.lower() in country_raw.lower() or country_raw.lower() in svg_country.lower():
                svg_content = svg_code
                break
        
        # Fallback for China and USA
        if not svg_content:
             if "China" in country_raw: svg_content = svg_flags.get("People’s Republic of China")
             elif "Miami" in country_raw or "Austin" in country_raw or "Las Vegas" in country_raw or "States" in country_raw:
                  svg_content = svg_flags.get("United States of America")
             elif "Abu Dhabi" in country_raw: svg_content = svg_flags.get("United Arab Emirates")

        clean_schedule.append({
            "round": item.get("roundText"),
            "country": country_raw.upper(),
            "gpName": item.get("meetingName").upper() + " GRAND PRIX 2026",
            "location": item.get("meetingName"),
            "dates": item.get("startAndEndDateForF1RD"),
            "isTest": item.get("isTestEvent", False),
            "flag_svg": svg_content
        })

    # 5. Save the clean result
    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(clean_schedule, f, ensure_ascii=False, indent=4)
    
    print(f"Successfully generated clean schedule with {len(clean_schedule)} rounds and SVG flags.")

if __name__ == "__main__":
    clean_extract_2026()
