import re
import os

def brute_force_meetings():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        data = f.read()

    # Find all occurrences of meetingName
    meetings = re.findall(r'\"meetingName\":\"(.*?)\"', data)
    unique_meetings = sorted(list(set(meetings)))
    
    print(f"Total meetingName tags: {len(meetings)}")
    print(f"Unique meetings: {len(unique_meetings)}")
    for m in unique_meetings:
        print(f" - {m}")

if __name__ == "__main__":
    brute_force_meetings()
