import base64
import json
import re
from bs4 import BeautifulSoup

def inspect_australia():
    with open("debug_2026_new.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    # 查找包含 Australia 且有 data-f1rd-a7s-context 的标签
    elements = soup.find_all(attrs={"data-f1rd-a7s-context": True})
    
    for el in elements:
        b64 = el["data-f1rd-a7s-context"] + "==="
        try:
            decoded = base64.b64decode(b64).decode('utf-8')
            if "Australia" in decoded:
                data = json.loads(decoded)
                print(json.dumps(data, indent=2))
                break
        except:
            continue

if __name__ == "__main__":
    inspect_australia()
