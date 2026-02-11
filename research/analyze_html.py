from bs4 import BeautifulSoup
import json
import re

def analyze_scripts(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html = f.read()
    
    soup = BeautifulSoup(html, 'html.parser')
    scripts = soup.find_all('script')
    
    results = []
    for i, s in enumerate(scripts):
        script_id = s.get('id', 'No ID')
        script_type = s.get('type', 'No Type')
        content = s.string if s.string else ""
        length = len(content)
        preview = content[:100].replace('\n', ' ')
        results.append(f"Index: {i} | ID: {script_id} | Type: {script_type} | Length: {length} | Preview: {preview}")
        
        # 寻找包含赛程关键词的内容
        if "Australia" in content and "March" in content and length > 1000:
             print(f"--- Potential Schedule Script Found at Index {i} ---")
             with open(f'script_{i}.json', 'w', encoding='utf-8') as sf:
                 # 提取 JSON 部分
                 try:
                     # 假设是 JSON
                     data = json.loads(content)
                     json.dump(data, sf, indent=2, ensure_ascii=False)
                     print(f"Saved JSON content to script_{i}.json")
                 except:
                     sf.write(content)
                     print(f"Saved raw content to script_{i}.json")

    with open('scripts_summary.txt', 'w', encoding='utf-8') as f:
        f.write('\n'.join(results))
    print("Saved summary to scripts_summary.txt")

if __name__ == "__main__":
    analyze_scripts('raw.html')
