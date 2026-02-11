import re
import json

def extract_results(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    
    # 查找 "rows":[...] 结构
    # 由于 rows 数据可能很大且包含嵌套，我们使用平衡括号查找
    start_tag = '"rows":['
    start_idx = data.find(start_tag)
    
    if start_idx != -1:
        # 从 [ 开始
        content = data[start_idx + len(start_tag) - 1:]
        brace_count = 0
        end_idx = 0
        for i, char in enumerate(content):
            if char == '[': brace_count += 1
            elif char == ']': brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
        
        rows_json = content[:end_idx]
        try:
            rows_data = json.loads(rows_json)
            print(f"Successfully extracted {len(rows_data)} rows.")
            
            # 保存前几行以供分析
            with open('bahrain_2024_rows.json', 'w', encoding='utf-8') as f:
                json.dump(rows_data[:3], f, indent=2, ensure_ascii=False)
            print("Saved representative rows to bahrain_2024_rows.json")
            
            # 打印第一行数据详情（通常是冠军）
            first_row = rows_data[0]
            print("First row structure preview:")
            for i, cell in enumerate(first_row):
                print(f"Cell {i}: {cell}")
                
        except Exception as e:
            print(f"JSON Parsing failed: {e}")
            with open('error_fragment.txt', 'w', encoding='utf-8') as f:
                f.write(rows_json)
    else:
        print("Could not find 'rows' structure in data.")

if __name__ == "__main__":
    extract_results('full_text_debug.txt')
