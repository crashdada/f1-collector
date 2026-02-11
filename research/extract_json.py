import re
import json
import sys

def extract_next_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if match:
        data = json.loads(match.group(1))
        with open('debug_full_data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully extracted debug_full_data.json")
    else:
        print("No __NEXT_DATA__ found")

if __name__ == "__main__":
    path = sys.argv[1] if len(sys.argv) > 1 else 'debug_2026_new.html'
    extract_next_data(path)
