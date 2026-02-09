import requests
import time
import json
import re
from bs4 import BeautifulSoup

import datetime

class F1DataCollector:
    def __init__(self, season=None):
        # 如果未指定年份，自动获取当前年份
        self.season = season or datetime.datetime.now().year
        self.base_url = "https://www.formula1.com"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def _reconstruct_next_data(self, html):
        """还原 Next.js 碎片数据"""
        pattern = r'self\.__next_f\.push\(\[1,\"(.*?)\"\]\)'
        matches = re.findall(pattern, html)
        full_text = "".join(matches).replace('\\"', '"').replace('\\\\', '\\')
        return full_text

    def check_is_race_window(self, schedule_path='schedule_2026.json'):
        """检测当前日期是否处于赛后数据更新窗口 (赛后 1-3 天)"""
        try:
            with open(schedule_path, 'r', encoding='utf-8') as f:
                schedule = json.load(f)
            
            today = datetime.date.today()
            for race in schedule:
                # 提取日期 (例如 "06 - 08 MAR")
                date_str = race.get('dates', '')
                if not date_str: continue
                
                # 简单解析结束日期 (假设格式为 "... - DD MMM")
                match = re.search(r'-\s+(\d+)\s+([A-Z]{3})', date_str)
                if match:
                    end_day = int(match.group(1))
                    end_month_str = match.group(2)
                    
                    # 月份映射
                    months = {
                        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
                        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
                    }
                    month = months.get(end_month_str.upper(), today.month)
                    
                    # 构造 race_end_date (注意：这里假设是当前年份)
                    race_end_date = datetime.date(self.season, month, end_day)
                    
                    # 判断今天是否在赛后 3 天内
                    delta = (today - race_end_date).days
                    if 0 <= delta <= 3:
                        print(f"Match found: {race['location']} ended {delta} days ago. Entering Scrape Window.")
                        return True
            
            print("Today is not in a primary post-race window. Skipping deep scrape.")
            return False
        except Exception as e:
            print(f"Schedule check failed: {e}. Defaulting to run.")
            return True

    def fetch_page(self, url, max_retries=5, initial_delay=1800):
        """获取页面并包含延后重试机制"""
        retries = 0
        while retries < max_retries:
            try:
                print(f"Fetching: {url} (Attempt {retries + 1})")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                # 检查数据是否就绪 (检查关键词如 TBC, TBD 或 缺少 rows)
                if "To be confirmed" in response.text or "TBC" in response.text:
                    if retries < max_retries - 1:
                        wait_time = initial_delay * (2 ** retries)
                        print(f"Data not ready (TBC). Retrying in {wait_time/60:.1f} min...")
                        time.sleep(wait_time)
                        retries += 1
                        continue
                
                return response.text
            except Exception as e:
                print(f"Request failed: {e}")
                if retries < max_retries - 1:
                    time.sleep(60)
                    retries += 1
                else:
                    return None
        return None

    def get_schedule(self):
        """获取并解析赛季日程"""
        url = f"{self.base_url}/en/racing/{self.season}"
        html = self.fetch_page(url, max_retries=1)
        if not html: return []

        full_text = self._reconstruct_next_data(html)
        
        # 寻找 secondaryNavigationSchedule
        start_tag = '"secondaryNavigationSchedule":['
        start_idx = full_text.find(start_tag)
        if start_idx == -1: return []
        
        content = full_text[start_idx + len(start_tag) - 1:]
        brace_count, end_idx = 0, 0
        for i, char in enumerate(content):
            if char == '[': brace_count += 1
            elif char == ']': brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
        
        try:
            data = json.loads(content[:end_idx])
            schedule = []
            for item in data:
                schedule.append({
                    "round": item.get("roundText"),
                    "location": item.get("meetingName"),
                    "dates": item.get("startAndEndDateForF1RD"),
                    "url": f"{self.base_url}{item.get('url')}" if item.get('url') else None,
                    "isTest": item.get("isTestEvent", False)
                })
            return schedule
        except:
            return []

    def get_race_results(self, race_url):
        """解析比赛结果"""
        html = self.fetch_page(race_url)
        if not html: return []
        
        full_text = self._reconstruct_next_data(html)
        
        # 寻找 rows
        start_tag = '"rows":['
        start_idx = full_text.find(start_tag)
        if start_idx == -1: return []
        
        content = full_text[start_idx + len(start_tag) - 1:]
        brace_count, end_idx = 0, 0
        for i, char in enumerate(content):
            if char == '[': brace_count += 1
            elif char == ']': brace_count -= 1
            if brace_count == 0:
                end_idx = i + 1
                break
        
        try:
            rows = json.loads(content[:end_idx])
            results = []
            for row in rows:
                # 简单解析逻辑 (具体索引需根据 Bahrain 2024 rows 分析微调)
                # 假设 Cell 0=Pos, Cell 2=Driver, Cell 3=Team, Cell 6=Pts
                res = {
                    "pos": row[0].get('content', [None])[0] if len(row) > 0 else None,
                    "no": row[1].get('content', [None])[0] if len(row) > 1 else None,
                    "points": row[6].get('content', [0])[0] if len(row) > 6 else 0
                }
                results.append(res)
            return results
        except:
            return []

if __name__ == "__main__":
    collector = F1DataCollector() # 自动获取当前年份
    
    print(f"Starting F1 Data Collector for Season {collector.season}...")
    
    # 首先检查是否需要执行深度爬取 (基于赛历)
    # 如果是手动触发或 schedule.json 不存在，则默认运行
    if collector.check_is_race_window():
        print("Fetching Schedule and Results...")
        sched = collector.get_schedule()
        for s in sched:
            print(f"{s['round']}: {s['location']} - {s['dates']}")
            # 后续可以增加对具体分站 URL 的结果抓取逻辑
    else:
        print("Scraper exited: Not in a post-race update window.")
