import sqlite3
import json
import os

# 路径配置
# 路径配置
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 优先使用环境变量 (CI环境)，否则回退到相对路径 (本地开发)
default_db_path = os.path.join(os.path.dirname(CURRENT_DIR), 'f1-website', 'public', 'f1.db')
DB_PATH = os.environ.get('F1_DB_PATH', default_db_path)
SCRAPER_PATH = os.path.join(CURRENT_DIR, 'scraper_drivers_2026.py')
JSON_OUT_PATH = os.path.join(CURRENT_DIR, 'data', 'drivers_2026.json')
TEAM_JSON_PATH = os.path.join(CURRENT_DIR, 'data', 'teams_2026.json')

def get_accurate_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Driver Mapping: 2026 Code -> (First Name, Last Name) in DB
    code_to_name = {
        "HAM": ("Lewis", "Hamilton"),
        "VER": ("Max", "Verstappen"),
        "NOR": ("Lando", "Norris"),
        "LEC": ("Charles", "Leclerc"),
        "ALO": ("Fernando", "Alonso"),
        "PIA": ("Oscar", "Piastri"),
        "RUS": ("George", "Russell"),
        "SAI": ("Carlos", "Sainz"),
        "ALB": ("Alexander", "Albon"),
        "GAS": ("Pierre", "Gasly"),
        "PER": ("Sergio", "Perez"),
        "BOT": ("Valtteri", "Bottas"),
        "HUL": ("Nico", "Hulkenberg"),
        "OCO": ("Esteban", "Ocon"),
        "STR": ("Lance", "Stroll"),
        "ANT": ("Kimi", "Antonelli"),
        "BEA": ("Oliver", "Bearman"),
        "COL": ("Franco", "Colapinto"),
        "HAD": ("Isack", "Hadjar"),
        "LIN": ("Arvid", "Lindblad"),
        "BOR": ("Gabriel", "Bortoleto"),
        "LAW": ("Liam", "Lawson"),
        "TSU": ("Yuki", "Tsunoda"),
        "ZHO": ("Guanyu", "Zhou")
    }
    
    authoritative = {}
    
    for code, (first, last) in code_to_name.items():
        # Get driver_id
        cur.execute("SELECT driver_id FROM drivers WHERE first_name = ? AND last_name = ?", (first, last))
        row = cur.fetchone()
        if not row:
            # Fallback for newcomers or name variations
            authoritative[code] = {
                "wins": 0, "podiums": 0, "poles": 0, "points": 0, "entries": 0, "championships": 0,
                "signature": {"debut": 2026, "avgPoints": 0, "peak": "Rookie", "winRate": "0%"}
            }
            continue
            
        did = row[0]
        
        # Get championships
        cur.execute("SELECT COUNT(*) FROM driver_championships WHERE driver_id = ? AND rank = 1", (did,))
        championships = cur.fetchone()[0]
        
        # Get aggregate stats from driver_season_stats
        cur.execute("""
            SELECT SUM(wins), SUM(podiums), SUM(poles), SUM(points), SUM(races), MIN(season)
            FROM driver_season_stats 
            WHERE driver_id = ?
        """, (did,))
        wins, podiums, poles, points, entries, first_year = cur.fetchone()
        
        wins = int(wins or 0)
        podiums = int(podiums or 0)
        poles = int(poles or 0)
        points = round(float(points or 0), 1)
        entries = int(entries or 0)
        first_year = first_year or 2026
        
        # Peak position
        cur.execute("SELECT MIN(position) FROM driver_season_stats WHERE driver_id = ?", (did,))
        peak_pos = cur.fetchone()[0]
        peak_str = f"P{peak_pos}" if peak_pos and peak_pos > 1 else "世界冠军" if championships > 0 else "Rookie"
        
        avg_points = round(points / entries, 2) if entries > 0 else 0
        win_rate = f"{round((wins / entries) * 100, 1)}%" if entries > 0 else "0%"
        
        authoritative[code] = {
            "wins": wins,
            "podiums": podiums,
            "poles": poles,
            "points": int(points) if points == int(points) else points,
            "entries": entries,
            "championships": championships,
            "signature": {
                "debut": int(first_year),
                "avgPoints": avg_points,
                "peak": peak_str,
                "winRate": win_rate
            }
        }
    
    # Team stats calculation
    try:
        from calculate_team_stats import get_stats
        teams_authoritative = get_stats()
        print("Team stats calculated from database successfully.")
    except Exception as e:
        print(f"Warning: Failed to calculate team stats from DB ({e}). Falling back to static.")
        teams_authoritative = {}
    
    conn.close()
    return authoritative, teams_authoritative
    
    conn.close()
    return authoritative, teams_authoritative

def update_collector_scraper():
    # 这个脚本将读取 scraper 并注入数据
    # 实际上由于 scraper 是个 python 文件，直接字符串替换比较危险。
    # 我们改为更新生成后的 JSON，并建议用户以后在采集端维护这些“静态”属性。
    pass

if __name__ == "__main__":
    # 1. 运行原有的 scraper
    os.system(f"python {SCRAPER_PATH}")
    
    # 2. 读取生成的 JSON 并回填精准数据
    with open(JSON_OUT_PATH, 'r', encoding='utf-8') as f:
        drivers = json.load(f)
        
    stats, team_stats = get_accurate_stats()
    
    for d in drivers:
        code = d['code']
        if code in stats:
            s = stats[code]
            d['careerStats'] = {k: v for k, v in s.items() if k != 'signature'}
            d['signatureStats'] = s['signature']
        
    with open(TEAM_JSON_PATH, 'r', encoding='utf-8') as f:
        teams = json.load(f)
        
    for t in teams:
        tid = t['id']
        if tid in team_stats:
            ts = team_stats[tid]
            t['history'] = ts['history']
            t['stats'] = ts['stats']
            
    with open(TEAM_JSON_PATH, 'w', encoding='utf-8') as f:
        json.dump(teams, f, indent=4, ensure_ascii=False)
        
    # 5. 写回 collector 的 JSON
    with open(JSON_OUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(drivers, f, indent=4, ensure_ascii=False)
        
    print("Collector's drivers & teams JSON updated with accurate stats and signatures.")
