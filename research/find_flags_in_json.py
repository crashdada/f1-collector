import json
import base64
import re
from bs4 import BeautifulSoup

file_path = r'c:\Users\jaymz\Desktop\oc\f1-collector\debug_2026.html'
soup = BeautifulSoup(open(file_path, encoding='utf-8'), 'html.parser')

def find_flags(obj, path=""):
    if isinstance(obj, dict):
        for k, v in obj.items():
            if 'flag' in k.lower() or 'country' in k.lower():
                print(f"Key match {k}: {v} at {path}.{k}")
            if isinstance(v, str) and 'media.formula1.com' in v and 'flag' in v.lower():
                print(f"Value match {k}: {v} at {path}.{k}")
            find_flags(v, f"{path}.{k}")
    elif isinstance(obj, list):
        for i, item in enumerate(obj):
            find_flags(item, f"{path}[{i}]")

# Check data-f1rd-a7s-context nodes
context_nodes = soup.find_all(attrs={"data-f1rd-a7s-context": True})
for node in context_nodes:
    try:
        decoded = json.loads(base64.b64decode(node["data-f1rd-a7s-context"]).decode('utf-8'))
        find_flags(decoded, "context")
    except:
        pass

# Check __NEXT_DATA__
next_script = soup.find("script", id="__NEXT_DATA__")
if next_script:
    try:
        data = json.loads(next_script.string)
        find_flags(data, "next")
    except:
        pass
