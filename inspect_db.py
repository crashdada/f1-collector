import sqlite3
import json

DB_PATH = r'C:/Users/jaymz/Desktop/oc/f1-website/public/f1.db'

def inspect():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    tables = ['teams', 'race_results', 'team_championships']
    for t in tables:
        print(f"--- {t} ---")
        cur.execute(f"PRAGMA table_info({t})")
        for col in cur.fetchall():
            print(col)
            
    # Sample data to see values
    print("\n--- teams sample ---")
    cur.execute("SELECT * FROM teams LIMIT 1")
    print(cur.fetchone())
    
    conn.close()

if __name__ == "__main__":
    inspect()
