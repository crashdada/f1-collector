import json
import re
import os

def extract():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    in_file = os.path.join(collector_dir, "reconstructed_data.txt")
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    web_out_file = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    tracks_file = os.path.join(collector_dir, "research", "all_tracks.txt")

    with open(in_file, "r", encoding="utf-8") as f:
        text = f.read()

    # Track map list
    with open(tracks_file, "r", encoding="utf-8") as f:
        track_links = [line.strip() for line in f if line.strip()]

    # Extract all meetings
    # Look for patterns like: {"roundText":"ROUND 1","meetingName":"Australia",...}
    # We'll use a regex to find all objects that look like meetings
    meetings = []
    
    # regex to find meeting groups
    # We search for "roundText" followed by "meetingName"
    pattern = r'\{[^{}]*?\"roundText\":\"(ROUND \d+|TESTING)\"[^{}]*?\"meetingName\":\"(.*?)\"[^{}]*?\"startAndEndDateForF1RD\":\"(.*?)\"[^{}]*?\}'
    matches = re.finditer(pattern, text)
    
    seen = set()
    for m in matches:
        round_txt = m.group(1)
        location = m.group(2)
        dates = m.group(3)
        
        # Get country (usually meetingCountryName)
        country_match = re.search(r'\"meetingCountryName\":\"(.*?)\"', m.group(0))
        country = country_match.group(1) if country_match else location
        
        # Get GP name (usually text or meetingOfficialName)
        name_match = re.search(r'\"text\":\"(.*?)\"', m.group(0))
        if not name_match:
            name_match = re.search(r'\"meetingOfficialName\":\"(.*?)\"', m.group(0))
        gp_name = name_match.group(1) if name_match else location
        
        key = (round_txt, location, dates)
        if key not in seen:
            meetings.append({
                "round": round_txt,
                "country": country.upper(),
                "gpName": gp_name,
                "location": location,
                "dates": dates,
                "isTest": "TESTING" in round_txt
            })
            seen.add(key)

    # Assets mapping
    loc_map = {
        "Australia": "melbourne", "China": "shanghai", "Japan": "suzuka", "Bahrain": "sakhir",
        "Saudi Arabia": "jeddah", "Miami": "miami", "Emilia Romagna": "imola", "Monaco": "montecarlo",
        "Spain": "catalunya", "Canada": "montreal", "Austria": "spielberg", "Great Britain": "silverstone",
        "Belgium": "spafrancorchamps", "Hungary": "hungaroring", "Netherlands": "zandvoort", "Italy": "monza",
        "Azerbaijan": "baku", "Singapore": "singapore", "USA": "austin", "Mexico": "mexicocity",
        "Brazil": "interlagos", "Las Vegas": "lasvegas", "Qatar": "lusail", "Abu Dhabi": "yasmarina",
        "Madrid": "madrid"
    }

    def find_track(loc):
        keyword = loc_map.get(loc, loc.lower().replace(" ", ""))
        for link in track_links:
            if keyword in link.lower(): return link
        return None

    def get_flag(c):
        c_name = c.title().replace(" ", "_")
        return f"https://media.formula1.com/content/dam/fom-website/flags/{c_name}.png.transform/2col/image.png"

    for m in meetings:
        m["image"] = find_track(m["location"])
        m["flag"] = get_flag(m["location"])

    # Sorting
    def sort_key(e):
        if "TESTING" in e["round"]: return (0, e["dates"])
        num = re.search(r"ROUND (\d+)", e["round"])
        return (1, int(num.group(1)) if num else 99)

    meetings.sort(key=sort_key)

    # Special fix for Testing rounds to avoid duplicates if any
    filtered = []
    seen_test_dates = set()
    for m in meetings:
        if m["isTest"]:
            if m["dates"] not in seen_test_dates:
                filtered.append(m)
                seen_test_dates.add(m["dates"])
        else:
            filtered.append(m)

    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=4, ensure_ascii=False)
    
    with open(web_out_file, "w", encoding="utf-8") as f:
        json.dump(filtered, f, indent=4, ensure_ascii=False)

    print(f"Extracted {len(filtered)} rounds.")
    for m in filtered:
        print(f"{m['round']}: {m['location']} ({m['dates']})")

if __name__ == "__main__":
    extract()
