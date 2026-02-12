import sqlite3
import json
import os

DB_PATH = r'C:/Users/jaymz/Desktop/oc/f1-website/public/f1.db'

def get_stats():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Mapping of 2026 IDs to historical names in database (name column in teams table)
    mapping = {
        "ferrari": ["Ferrari", "法拉利"],
        "red_bull": ["Red Bull Racing", "Red Bull", "红牛", "红牛车队"],
        "mercedes": ["Mercedes", "Mercedes-AMG", "梅赛德斯", "梅赛德斯-奔驰"],
        "mclaren": ["McLaren", "迈凯伦"],
        "aston_martin": ["Aston Martin", "Racing Point", "Force India", "Jordan", "Spyker", "Midland", "阿斯顿马丁"],
        "audi": ["Sauber", "Alfa Romeo", "BMW Sauber", "索伯", "阿尔法·罗密欧"],
        "williams": ["Williams", "威廉姆斯"],
        "alpine": ["Alpine", "Renault", "Lotus F1", "Benetton", "Toleman", "阿尔派", "雷诺"],
        "haas": ["Haas F1 Team", "Haas", "哈斯"],
        "rb": ["RB", "AlphaTauri", "Toro Rosso", "Minardi", "维萨RB"],
        "cadillac": []
    }
    
    results = {}
    
    for team_id, names in mapping.items():
        if not names:
            results[team_id] = {
                "history": {"championships": 0, "wins": 0, "podiums": 0, "poles": 0, "entries": 0, "firstEntry": "2026"},
                "stats": {"points": 0, "rank": 0, "wins": 0, "podiums": 0}
            }
            continue
            
        placeholders = ', '.join(['?' for _ in names])
        
        # Championship Count
        try:
            cur.execute(f"""
                SELECT COUNT(*) FROM team_championships tc
                JOIN teams t ON tc.team_id = t.team_id
                WHERE t.name IN ({placeholders}) AND tc.rank = 1
            """, names)
            championships = cur.fetchone()[0]
        except:
            championships = 0
            
        # Wins, Podiums, Poles from race_results
        cur.execute(f"""
            SELECT COUNT(*) FROM race_results res 
            JOIN teams t ON res.team_id = t.team_id 
            WHERE t.name IN ({placeholders}) AND res.position = 1
        """, names)
        wins = cur.fetchone()[0]
        
        cur.execute(f"""
            SELECT COUNT(*) FROM race_results res 
            JOIN teams t ON res.team_id = t.team_id 
            WHERE t.name IN ({placeholders}) AND res.position <= 3
        """, names)
        podiums = cur.fetchone()[0]
        
        cur.execute(f"""
            SELECT COUNT(*) FROM race_results res 
            JOIN teams t ON res.team_id = t.team_id 
            WHERE t.name IN ({placeholders}) AND res.grid_position = 1
        """, names)
        poles = cur.fetchone()[0]
        
        cur.execute(f"""
            SELECT COUNT(DISTINCT race_id) FROM race_results res 
            JOIN teams t ON res.team_id = t.team_id 
            WHERE t.name IN ({placeholders})
        """, names)
        entries = cur.fetchone()[0]
        
        # First entry year
        cur.execute(f"""
            SELECT MIN(r.season) FROM races r
            JOIN race_results res ON res.race_id = r.race_id
            JOIN teams t ON res.team_id = t.team_id
            WHERE t.name IN ({placeholders})
        """, names)
        first_year = cur.fetchone()[0] or 2026
        
        results[team_id] = {
            "history": {
                "championships": championships,
                "wins": wins,
                "podiums": podiums,
                "poles": poles,
                "entries": entries,
                "firstEntry": str(first_year)
            },
            "stats": {"points": 0, "rank": 0, "wins": 0, "podiums": 0}
        }
    
    conn.close()
    return results

if __name__ == "__main__":
    res = get_stats()
    print(json.dumps(res, indent=4))
