from bs4 import BeautifulSoup
import re

def clean_and_search():
    with open("debug_2026_new.html", "r", encoding="utf-8") as f:
        html = f.read()

    soup = BeautifulSoup(html, "html.parser")
    
    # 移除无用标签
    for script in soup(["script", "style"]):
        script.extract()

    # 查找所有 ROUND 文本
    # 注意：有的 ROUND 可能在属性中，有的在文本中
    # 我们先找文本
    round_elements = soup.find_all(string=re.compile(r'ROUND \d+'))
    print(f"Total ROUND text elements after cleaning: {len(round_elements)}")

    results = []
    for el in round_elements:
        # 获取周围的文本块
        parent = el.parent
        # 寻找包含日期的祖先
        container = parent
        date_str = "N/A"
        for _ in range(15):
            if not container: break
            t = container.get_text(" ", strip=True)
            # 匹配 13 - 15 MAR 这种格式
            m = re.search(r'(\d+)\s*-\s*(\d+)\s*([A-Z]{3})', t)
            if m:
                date_str = m.group(0)
                break
            container = container.parent
        
        if container:
            text = container.get_text("|", strip=True)
            results.append(f"{el.strip()} | {date_str} | {text[:150]}")

    unique = sorted(list(set(results)))
    print(f"Unique Rounds with dates: {len(unique)}")
    for r in unique:
        print(r)

if __name__ == "__main__":
    clean_and_search()
