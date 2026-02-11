import json
import base64
from bs4 import BeautifulSoup
import os

def explore():
    html_file = 'research/debug_2026.html'
    if not os.path.exists(html_file):
        print(f'File not found: {html_file}')
        return

    content = open(html_file, encoding='utf-8').read()
    
    # 1. Basic keyword check
    keywords = ['UTC', 'sessionTime', 'offset', 'gmtOffset', 'sessions', 'circuit', 'spectators']
    for kw in keywords:
        print(f"Keyword '{kw}': {kw.lower() in content.lower()}")

    import re
    # 2. Try to find session names and start times
    # Typical pattern in RSC: "sessionName":"PRACTICE 1","startTime":"2026-03-06T01:30:00Z"
    sessions = re.findall(r'\"sessionName\":\"(.*?)\".*?\"startTime\":\"(.*?)\"', content)
    print(f"\nFound {len(sessions)} session entries.")
    for s in sessions[:15]:
        print(f"  Session: {s[0]}, Start: {s[1]}")

    # 3. Try to find circuit specs
    # Patterns: "circuitId":"melbourne", "circuitName":"Albert Park Circuit"
    circuits = re.findall(r'\"circuitId\":\"(.*?)\".*?\"circuitName\":\"(.*?)\"', content)
    print(f"\nFound {len(circuits)} circuit entries.")
    for c in circuits[:5]:
        print(f"  ID: {c[0]}, Name: {c[1]}")

    # 4. Try to find meeting slugs for URLs
    # Pattern: "meetingSlug":"australia"
    slugs = re.findall(r'\"meetingSlug\":\"(.*?)\"', content)
    print(f"\nFound {len(set(slugs))} unique meeting slugs.")
    print(sorted(list(set(slugs))))

if __name__ == "__main__":
    explore()
