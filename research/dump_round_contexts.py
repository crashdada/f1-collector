import re
import os

def dump_round_contexts():
    collector_dir = r"c:\Users\jaymz\Desktop\oc\f1-collector"
    html_file = os.path.join(collector_dir, "debug_2026.html")
    
    with open(html_file, 'r', encoding='utf-8') as f:
        data = f.read()

    # Search for ROUND 1, ROUND 2, ..., ROUND 24
    for i in range(1, 25):
        pattern = f"ROUND {i}"
        idx = data.find(pattern)
        if idx != -1:
            print(f"--- {pattern} Context ---")
            print(data[idx-200:idx+500])
            print("\n")
        else:
            print(f"--- {pattern} Not Found ---")

if __name__ == "__main__":
    dump_round_contexts()
