import base64
import json
import re
from bs4 import BeautifulSoup

def decode_f1_data():
    with open("debug_2026_new.html", "r", encoding="utf-8") as f:
        html = f.read()
    
    soup = BeautifulSoup(html, "html.parser")
    # 查找所有包含 data-f1rd-a7s-context 的标签
    elements = soup.find_all(attrs={"data-f1rd-a7s-context": True})
    print(f"Found {len(elements)} elements with context attribute")

    races = []
    seen_keys = set()

    for el in elements:
        try:
            b64_data = el["data-f1rd-a7s-context"]
            # 补齐 base64 填充
            missing_padding = len(b64_data) % 4
            if missing_padding:
                b64_data += '=' * (4 - missing_padding)
                
            decoded = base64.b64decode(b64_data).decode('utf-8')
            data = json.loads(decoded)
            
            # 我们只关心包含 raceName 或 roundNumber 的数据
            if "raceName" in data or "roundNumber" in data:
                # 提取有用的字段
                race_id = data.get("raceId") or f"{data.get('roundNumber')}-{data.get('raceName')}"
                if race_id not in seen_keys:
                    races.append(data)
                    seen_keys.add(race_id)
        except Exception as e:
            continue

    print(f"Decoded {len(races)} unique race data blocks")
    
    # 获取详细信息
    final_schedule = []
    for r in races:
        # 为了匹配用户截图，我们需要找到对应的日期和图片
        # 这些数据可能在同一个标签的周围，或者是 data 对象本身的一部分
        
        # 尝试从 data 对象中直接提取 (如果有)
        # 如果 data 没包含日期，我们需要从 HTML 中找到该标签周围的日期
        
        # 寻找该 element 在 HTML 中的上下文以获取日期
        # (这步在真正的 scraper 中会更精细)
        
        final_schedule.append({
            "round": f"ROUND {r.get('roundNumber', '?')}",
            "gpName": r.get("raceName", "TBC"),
            "country": r.get("countryName", "TBC"),
            "date": r.get("raceDate", "TBC"), # 这里的字段名需要确认
            "raw": r
        })

    # 打印前几个结果确认
    for fs in final_schedule[:5]:
        print(fs)

if __name__ == "__main__":
    decode_f1_data()
