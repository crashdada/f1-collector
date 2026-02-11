import re

with open("reconstructed_2026.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Find Round 1 info
r1_pos = text.find('"roundText":"ROUND 1"')
if r1_pos != -1:
    chunk = text[r1_pos-500 : r1_pos+1000]
    print("Found ROUND 1. Chunk:")
    print(chunk)
    
    # Extract fields
    fields = ["meetingName", "meetingCountryName", "meetingStartDate", "meetingEndDate", "startAndEndDateForF1RD", "meetingGraphic"]
    for field in fields:
        match = re.search(f'\"{field}\":\"(.*?)\"', chunk)
        if match:
            print(f" - {field}: {match.group(1)}")
        else:
            # Try non-string values or nested
            match_obj = re.search(f'\"{field}\":({{.*?}})', chunk)
            if match_obj:
                print(f" - {field} (obj): {match_obj.group(1)}")
            else:
                print(f" - {field}: NOT FOUND")
