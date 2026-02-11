import json
import re
import os

def restore():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    reconstructed_file = os.path.join(collector_dir, "reconstructed_data.txt")
    tracks_file = os.path.join(collector_dir, "research", "all_tracks.txt")
    output_file = os.path.join(collector_dir, "schedule_2026.json")
    web_output_file = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"

    # 1. Load data
    with open(reconstructed_file, "r", encoding="utf-8") as f:
        full_text = f.read()
    
    with open(tracks_file, "r", encoding="utf-8") as f:
        track_links = [line.strip() for line in f if line.strip()]

    # 2. Extract secondaryNavigationSchedule
    start_tag = '"secondaryNavigationSchedule":['
    start_idx = full_text.find(start_tag)
    if start_idx == -1:
        print("Error: Could not find secondaryNavigationSchedule")
        return

    content = full_text[start_idx + len(start_tag) - 1:]
    brace_count = 0
    end_idx = 0
    for i, char in enumerate(content):
        if char == '[': brace_count += 1
        elif char == ']': brace_count -= 1
        if brace_count == 0:
            end_idx = i + 1
            break
    
    schedule_raw = content[:end_idx]
    raw_events = json.loads(schedule_raw)

    # 3. Track mapping (by location keyword)
    def find_track(location):
        loc_map = {
            "Bahrain": "sakhir",
            "Australia": "melbourne",
            "China": "shanghai",
            "Japan": "suzuka",
            "Saudi Arabia": "jeddah",
            "Miami": "miami",
            "Emilia Romagna": "imola", # 2026 may differ, check track list
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
        keyword = loc_map.get(location, location.lower().replace(" ", ""))
        for link in track_links:
            if keyword in link.lower():
                return link
        return None

    # 4. Flag mapping
    def get_flag(country):
        if not country: return None
        # F1 Flag URL pattern
        c_name = country.replace(" ", "_")
        return f"https://media.formula1.com/content/dam/fom-website/flags/{c_name}.png.transform/2col/image.png"

    # 5. Build final schedule
    final_schedule = []
    for item in raw_events:
        location = item.get("meetingName", "TBC")
        country = item.get("meetingCountryName", "").upper()
        
        event = {
            "round": item.get("roundText"),
            "country": country,
            "gpName": item.get("text"),
            "location": location,
            "dates": item.get("startAndEndDateForF1RD"),
            "image": find_track(location),
            "flag": get_flag(item.get("meetingCountryName")),
            "isTest": item.get("isTestEvent", False)
        }
        final_schedule.append(event)

    # Save to collector
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)
    
    # Sync to website
    with open(web_output_file, 'w', encoding='utf-8') as f:
        json.dump(final_schedule, f, indent=4, ensure_ascii=False)

    print(f"Successfully restored {len(final_schedule)} events with assets.")

if __name__ == "__main__":
    restore()
