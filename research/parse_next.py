import re
import json

def parse_next_f(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    # 提取所有数据碎片
    pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
    matches = re.findall(pattern, html)
    # 处理转义字符
    full_text = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')
    
    # 查找 secondaryNavigationSchedule
    print("Searching for secondaryNavigationSchedule...")
    
    # 使用正则定位 secondaryNavigationSchedule 数组
    # 模式: "secondaryNavigationSchedule": [...]
    # 这里的数据结构比较复杂，我们先找这个关键词
    start_tag = '"secondaryNavigationSchedule":['
    start_idx = full_text.find(start_tag)
    
    if start_idx != -1:
        # 寻找匹配的闭合括号
        content = full_text[start_idx + len(start_tag) - 1:]
        brace_count = 0
        end_idx = 0
        for i, char in enumerate(content):
            if char == '[': brace_count += 1
            elif char == ']': brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
        
        schedule_raw = content[:end_idx]
        try:
            data = json.loads(schedule_raw)
            refined_schedule = []
            for item in data:
                # 提取关键字段
                race = {
                    "round": item.get("roundText"), # e.g. "ROUND 1" 或 "TESTING"
                    "name": item.get("text"), # e.g. "FORMULA 1 QATAR AIRWAYS AUSTRALIAN GRAND PRIX 2026"
                    "location": item.get("meetingName"), # e.g. "Australia"
                    "dates": item.get("startAndEndDateForF1RD"), # e.g. "06 - 08 MAR"
                    "key": item.get("meetingKey"), # e.g. "1279"
                    "url": item.get("url"), # e.g. "/en/racing/2026/australia"
                    "isTest": item.get("isTestEvent", False)
                }
                refined_schedule.append(race)
            
            with open('schedule_2026.json', 'w', encoding='utf-8') as f:
                json.dump(refined_schedule, f, indent=2, ensure_ascii=False)
            
            print(f"成功导出 {len(refined_schedule)} 条赛程记录至 schedule_2026.json")
            for r in refined_schedule:
                print(f"{r['round']}: {r['location']} ({r['dates']})")
                
        except Exception as e:
            print(f"JSON 解析失败: {e}")
            # 保存片段以供检查
            with open('failed_fragment.txt', 'w', encoding='utf-8') as f:
                f.write(schedule_raw)
    else:
        print("未发现 secondaryNavigationSchedule 关键词")

if __name__ == "__main__":
    parse_next_f('raw.html')
