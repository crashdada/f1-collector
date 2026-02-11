import json
import requests
from bs4 import BeautifulSoup
import re
import os
import time

def auto_collect():
    # Paths
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    schedule_path = os.path.join(collector_dir, "schedule_2026.json")
    
    if not os.path.exists(schedule_path):
        print(f"Schedule file not found: {schedule_path}")
        return

    with open(schedule_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }

    updated_schedule = []
    month_map = {
        'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04', 'May': '05', 'Jun': '06',
        'Jul': '07', 'Aug': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
    }

    for race in schedule:
        slug = race.get('slug')
        if not slug or race.get('isTest'):
            updated_schedule.append(race)
            continue

        print(f"Processing {race['country']} ({slug})...")
        url = f"https://www.formula1.com/en/racing/2026/{slug}"
        
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            if resp.status_code != 200:
                print(f"  Failed to fetch {url}: {resp.status_code}")
                updated_schedule.append(race)
                continue

            soup = BeautifulSoup(resp.text, 'html.parser')
            
            # 0. Extract GMT Offset / Timezone
            # Search for gmtOffset in RSC with more flexibility
            offset_match = re.search(r'\"gmtOffset\":\"(.*?)\"', resp.text)
            if not offset_match:
                # Try finding it in another format or nearby context
                offset_match = re.search(r'offset\":\"(.*?)\"', resp.text)
            
            if offset_match:
                race['gmtOffset'] = offset_match.group(1).replace('\\', '')
            
            # 1. Extract Technical Specs
            specs = race.get('circuitSpecs', {})
            dt_elements = soup.find_all('dt')
            for dt in dt_elements:
                label = dt.get_text(strip=True).lower()
                dd = dt.find_next_sibling('dd')
                if not dd: continue
                value = dd.get_text(strip=True)
                
                if 'race distance' in label: specs['distance'] = value
                elif 'number of laps' in label: 
                    laps_match = re.search(r'\d+', value)
                    specs['laps'] = int(laps_match.group(0)) if laps_match else 0
                elif 'circuit length' in label: specs['length'] = value
                elif any(x in label for x in ['lap record', 'fastest lap time']): 
                    # Record info is often in the dd or a descendant
                    record_time = value
                    # Look for driver/year in span after dd or within dd's parent
                    driver_info = ""
                    # Check next sibling
                    next_el = dd.find_next_sibling()
                    if next_el and next_el.name in ['span', 'div', 'p']:
                        driver_info = f" ({next_el.get_text(strip=True)})"
                    
                    if not driver_info:
                        # Check inside dd's parent for any small text
                        parent = dd.parent
                        extra = parent.find(re.compile(r'span|div|p'), class_=re.compile(r'body-xs|semibold|text-3|technical'))
                        if extra and extra != dd:
                            driver_info = f" ({extra.get_text(strip=True)})"
                    
                    # Last ditch: if '(' is already in record_time, don't double up
                    # Clean up driver_info (remove existing parentheses before wrapping)
                    driver_info = driver_info.strip()
                    if driver_info.startswith('(') and driver_info.endswith(')'):
                        driver_info = driver_info[1:-1].strip()
                    
                    if driver_info:
                        specs['record'] = f"{record_time} ({driver_info})"
                    else:
                        specs['record'] = record_time
                    
                    # Final validation: if record is just '--' or empty, mark as None to show placeholder
                    if specs['record'].strip() in ['--', '-- ()', '()']:
                        specs['record'] = None

                elif 'first grand prix' in label: 
                    fgp_match = re.search(r'\d+', value)
                    specs['first_gp'] = int(fgp_match.group(0)) if fgp_match else 0

            race['circuitSpecs'] = specs

            # 2. Extract Sessions (with UTC timestamps)
            sessions = []
            session_items = soup.find_all('li', attrs={"data-f1rd-a7s-context": True})
            for item in session_items:
                name_span = item.find('span', class_=re.compile(r'typography-module_display-m-bold'))
                if not name_span: continue
                name = name_span.get_text(strip=True)
                
                day_span = item.find('span', class_=re.compile(r'typography-module_technical-l-bold'))
                month_span = item.find('span', class_=re.compile(r'typography-module_technical-s-regular'))
                
                time_tags = item.find_all('time')
                if time_tags:
                    start_time_text = time_tags[0].get_text(strip=True)
                    
                    found_utc = False
                    # Search specifically for the session in RSC
                    pattern = rf'\"sessionName\":\"{name.upper()}\".*?\"startTime\":\"(2026-.*?Z)\"'
                    utc_match = re.search(pattern, resp.text)
                    if not utc_match:
                        pattern = rf'\"sessionName\":\"{name}\".*?\"startTime\":\"(2026-.*?Z)\"'
                        utc_match = re.search(pattern, resp.text)

                    if utc_match:
                        sessions.append({"name": name, "time": utc_match.group(1)})
                        found_utc = True
                    
                    if not found_utc:
                        day = day_span.get_text(strip=True).zfill(2)
                        month = month_map.get(month_span.get_text(strip=True), '01')
                        sessions.append({"name": name, "time": f"2026-{month}-{day}T{start_time_text}:00Z"})

            if sessions:
                race['sessions'] = sessions

            # 3. Extract Detailed Image
            img_tag = soup.find('img', alt=re.compile(r'detailed', re.I))
            if img_tag and img_tag.get('src'):
                race['detailedImage'] = img_tag['src']
            else:
                # Fallback to standard 2026 pattern
                track_slug = race.get('image', '').split('2026track')[-1].split('blackoutline')[0] if race.get('image') else ''
                if track_slug:
                     race['detailedImage'] = f"https://media.formula1.com/image/upload/c_fit,h_704/q_auto/v1740000000/common/f1/2026/track/2026track{track_slug}detailed.webp"

        except Exception as e:
            print(f"  Error processing {slug}: {e}")
        
        updated_schedule.append(race)
        time.sleep(1)

    # Save and Sync
    with open(schedule_path, 'w', encoding='utf-8') as f:
        json.dump(updated_schedule, f, indent=4, ensure_ascii=False)
    web_dest = r"c:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
    with open(web_dest, 'w', encoding='utf-8') as f:
        json.dump(updated_schedule, f, indent=4, ensure_ascii=False)

    print(f"\nAuto-collection complete. Updated {len(updated_schedule)} races.")

if __name__ == "__main__":
    auto_collect()
