import json
import re
import os

def rescue_and_clean():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    # Use the website one as it definitely has the 24 round structure (even if messy)
    in_file = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    out_file = os.path.join(collector_dir, "schedule_2026.json")
    
    if not os.path.exists(in_file):
        print("Input file for rescue not found.")
        return

    with open(in_file, 'r', encoding='utf-8') as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"JSON load failed, attempting raw text fix: {e}")
            # If JSON is too broken to load, we'd need a raw text sweep
            return

    def clean_val(val):
        if not isinstance(val, str): return val
        # Strip everything after \",\"
        parts = val.split('\\",\\"')
        clean = parts[0]
        # Also remove trailing \",{\" or similar
        clean = re.split(r'\\",\{', clean)[0]
        # Remove any other weird Next.js escape sequences
        clean = clean.replace('\\"', '"').replace('\\\\', '\\')
        # Final trim of quotes if they leaked
        clean = clean.strip('"').strip("'")
        return clean

    cleaned_data = []
    
    # SVG Flag mapping
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

    for entry in data:
        country = clean_val(entry.get("country", ""))
        location = clean_val(entry.get("location", ""))
        round_text = clean_val(entry.get("round", ""))
        dates = clean_val(entry.get("dates", ""))
        gp_name = clean_val(entry.get("gpName", ""))
        
        # Determine flag
        flag_url = svg_map.get(country.upper())
        if not flag_url:
            # Try location
            flag_url = svg_map.get(location.upper())
        
        if not flag_url:
            # Partial matches
            for k, v in svg_map.items():
                if k in country.upper() or k in location.upper():
                    flag_url = v
                    break

        cleaned_data.append({
            "round": round_text,
            "country": country.upper(),
            "gpName": gp_name.upper(),
            "location": location,
            "dates": dates,
            "isTest": "TESTING" in round_text,
            "image": None,
            "flag": flag_url or entry.get("flag") # Keep old only if rescue fails
        })

    with open(out_file, 'w', encoding='utf-8') as f:
        json.dump(cleaned_data, f, ensure_ascii=False, indent=4)
    
    print(f"Rescue complete: {len(cleaned_data)} entries cleaned.")

if __name__ == "__main__":
    rescue_and_clean()
