import re
import json

def extract_next_data(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    match = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html)
    if match:
        data = json.loads(match.group(1))
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        print("Successfully extracted data.json")
    else:
        print("No __NEXT_DATA__ found")

if __name__ == "__main__":
    extract_next_data('raw.html')
