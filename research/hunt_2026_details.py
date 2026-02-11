import re
import os

def hunt_data():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Find all track SVGs
    tracks = re.findall(r'https://media.formula1.com/image/upload/[^\"]*track[^\"]*outline\.svg', content)
    unique_tracks = sorted(list(set(tracks)))
    
    print(f"Found {len(unique_tracks)} unique track SVGs.")
    for t in unique_tracks:
        print(f" - {t}")

    # 2. Search for dates that aren't in the Base64 cards
    # Pattern: "13 - 15 MAR" etc.
    dates = re.findall(r'\d{2} - \d{2} [A-Z]{3}', content)
    unique_dates = sorted(list(set(dates)))
    print(f"\nFound {len(unique_dates)} unique date strings.")
    for d in unique_dates:
        print(f" - {d}")

if __name__ == "__main__":
    hunt_data()
