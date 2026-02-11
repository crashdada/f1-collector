import re
import os

def find_full_schedule():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    in_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(in_file, 'r', encoding='utf-8') as f:
        html = f.read()

    pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
    matches = re.findall(pattern, html)
    reconstructed = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')
    
    pos = reconstructed.find('ROUND 24')
    if pos != -1:
        print(f"Found 'ROUND 24' at position {pos}")
        print("Context:")
        print(reconstructed[max(0, pos-1000):pos+1000])
    else:
        print("'ROUND 24' not found in reconstructed text.")
        # Search for any large array that looks like a schedule
        arrays = re.findall(r'\[\{.*?\}\]', reconstructed)
        for arr in arrays:
            if '"meetingName"' in arr and len(arr) > 5000:
                 print(f"Found large meeting array of length {len(arr)}")
                 # print(arr[:500])

if __name__ == "__main__":
    find_full_schedule()
