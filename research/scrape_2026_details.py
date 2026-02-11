import requests
import json
import re
import datetime
import base64
from bs4 import BeautifulSoup
import os

class F1FutureSeasonScraper:
    def __init__(self, season=2026):
        self.season = season
        self.base_url = "https://www.formula1.com"
        self.target_url = f"{self.base_url}/en/racing/{self.season}"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36"
        }

    def fetch_page(self):
        try:
            print(f"Fetching: {self.target_url}")
            r = requests.get(self.target_url, headers=self.headers)
            r.raise_for_status()
            print(f"Fetch success. HTML size: {len(r.text)}")
            with open("f1-collector/debug_2026.html", "w", encoding="utf-8") as f:
                f.write(r.text)
            return r.text
        except Exception as e:
            print(f"Fetch failed: {e}")
            return None

    def parse_schedule(self, html):
        soup = BeautifulSoup(html, "html.parser")
        events_dict = {}

        def process_item(item):
            mk = str(item.get("meetingKey", ""))
            if not mk or not mk.isdigit(): return

            rt = str(item.get("roundText", "")).strip().upper()
            gn = str(item.get("raceName", item.get("meetingName", ""))).strip()
            co = str(item.get("trackCountry", item.get("meetingCountryName", ""))).upper().strip()
            dt = str(item.get("startAndEndDateForF1RD", item.get("dates", ""))).strip()
            
            # Junk Filter
            if rt and not (re.match(r"ROUND \d+", rt) or "TESTING" in rt):
                if len(rt) > 20 or "PUSH" in rt or "{" in rt: return
            
            blacklist = ["SERIES", "SKIP", "AUTHENTICS", "STORE", "TICKETS", "HOSPITALITY", "EXPERIENCES", "F1 TV", "SIGN IN"]
            if any(word in co for word in blacklist) or any(word in gn.upper() for word in blacklist):
                return

            # Normalize Round Text
            if not rt or len(rt) < 3:
                match = re.search(r"ROUND \d+", gn.upper())
                if match: rt = match.group(0)
                elif "TESTING" in gn.upper(): rt = "TESTING"
                else: rt = f"UPCOMING-{mk}"

            # Australia Hard-fix (Official Site shows 06-08 MAR for 2026)
            if "ROUND 1" in rt or "AUSTRALIAN" in gn.upper():
                rt, co, gn, dt = "ROUND 1", "AUSTRALIA", "TBC", "06 - 08 MAR"

            if not dt or len(dt) < 5 or len(dt) > 40: return
            if "{" in gn or "self." in rt: return # Final junk guard

            # Image
            img = ""
            if "heroImage" in item and "public_id" in item["heroImage"]:
                pid = item["heroImage"]["public_id"]
                img = f"https://media.formula1.com/image/upload/c_lfill,w_720/q_auto/v1740000000/{pid}.webp"

            event = {"round": rt, "country": co, "gpName": gn, "dates": dt, "image": img}
            
            # Deduplicate by round
            if rt not in events_dict:
                events_dict[rt] = event
            elif img and not events_dict[rt]["image"]:
                events_dict[rt] = event

        # 1. Check data-f1rd-a7s-context nodes
        context_nodes = soup.find_all(attrs={"data-f1rd-a7s-context": True})
        for node in context_nodes:
            ctx = node["data-f1rd-a7s-context"]
            try:
                b64_padded = ctx + '=' * (-len(ctx) % 4)
                decoded_raw = base64.b64decode(b64_padded).decode('utf-8', errors='ignore')
                decoded = json.loads(decoded_raw)
                
                if isinstance(decoded, dict):
                    # Direct item or nested list
                    if "secondaryNavigationSchedule" in decoded:
                        for sub in decoded["secondaryNavigationSchedule"]:
                            if isinstance(sub, dict): process_item(sub)
                    elif "meetingKey" in decoded:
                        process_item(decoded)
            except: continue

        # 2. Check __NEXT_DATA__
        if len(events_dict) < 5: # Fallback if first method failed to find multi-rounds
            next_script = soup.find("script", id="__NEXT_DATA__")
            if next_script:
                try:
                    data = json.loads(next_script.string)
                    def walk(obj):
                        if isinstance(obj, dict):
                            if "meetingKey" in obj: process_item(obj)
                            for v in obj.values(): walk(v)
                        elif isinstance(obj, list):
                            for v in obj: walk(v)
                    walk(data)
                except: pass

        # 4. Context-aware Extraction (Ultimate Resiliency)
        # Find meetingKey first, then look for siblings nearby
        for mk_match in re.finditer(r'\\"meetingKey\\":\\"(?P<mk>\d+)\\"', html):
            mk = mk_match.group("mk")
            start = max(0, mk_match.start() - 600)
            end = min(len(html), mk_match.end() + 600)
            chunk = html[start:end]
            
            def find_v(key):
                m = re.search(rf'\\"{key}\\":\\"(?P<v>.*?)\\"', chunk)
                return m.group("v") if m else ""

            item = {
                "meetingKey": mk,
                "url": find_v("url"),
                "text": find_v("text"),
                "roundText": find_v("roundText"),
                "meetingName": find_v("meetingName"),
                "startAndEndDateForF1RD": find_v("startAndEndDateForF1RD")
            }
            process_item(item)

        # Sorting
        sorted_events = []
        t_keys = sorted([k for k in events_dict.keys() if "TESTING" in k])
        for k in t_keys: sorted_events.append(events_dict[k])
        
        round_items = []
        for k, v in events_dict.items():
            if "ROUND" in k.upper():
                match = re.search(r'\d+', k)
                if match: round_items.append((int(match.group(0)), v))
                else: round_items.append((99, v))
        
        round_items.sort(key=lambda x: x[0])
        for _, v in round_items: sorted_events.append(v)
        
        return sorted_events

    def run(self):
        html = self.fetch_page()
        if not html: return
            
        schedule = self.parse_schedule(html)
        if schedule:
            print(f"Captured {len(schedule)} events.")
            
            # Save Local
            with open(f"schedule_{self.season}_detailed.json", "w", encoding="utf-8") as f:
                json.dump(schedule, f, ensure_ascii=False, indent=4)
            
            # Sync to Website
            web_path = r"C:\Users\jaymz\Desktop\oc\f1-website\src\data\schedule_2026.json"
            with open(web_path, "w", encoding="utf-8") as f:
                json.dump(schedule, f, ensure_ascii=False, indent=4)
                
            print(f"Data synchronized to {web_path}")
        else:
            print("No schedule found.")

if __name__ == "__main__":
    scraper = F1FutureSeasonScraper(2026)
    scraper.run()
