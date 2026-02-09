import sqlite3
import json
import os
import re

def sync_schedule(json_path, db_path):
    if not os.path.exists(json_path):
        print(f"Error: {json_path} not found.")
        return

    if not os.path.exists(db_path):
        print(f"Error: {db_path} not found.")
        return

    print(f"Syncing data from {json_path} to {db_path}...")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    with open(json_path, 'r', encoding='utf-8') as f:
        schedule = json.load(f)

    # 简单的赛道名称映射 (后续可根据数据库实际 circuit_id 扩展)
    # 这里我们主要保证 races 表中有 2026 的赛程占位
    for race in schedule:
        round_text = race.get('round', '')
        # 提取数字
        round_match = re.search(r'\d+', round_text)
        round_num = int(round_match.group(0)) if round_match else 0
        
        if race.get('isTest'): continue # 跳过测试站
        
        name = race.get('location', 'Unknown Race')
        date_str = race.get('dates', '')
        
        # 插入或更新 races 表
        # 注意：此处假设数据库表结构包含 year, round, race_name, race_date
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO races (year, round, race_name, race_date)
                VALUES (?, ?, ?, ?)
            """, (2026, round_num, name, date_str))
            print(f"Synced Round {round_num}: {name}")
        except Exception as e:
            print(f"Failed to sync {name}: {e}")

    conn.commit()
    conn.close()
    print("Database sync completed.")

if __name__ == "__main__":
    # 默认路径配置 (可根据 NAS 实际目录调整)
    current_dir = os.path.dirname(os.path.abspath(__file__))
    json_file = os.path.join(current_dir, 'schedule_2026.json')
    db_file = os.path.join(current_dir, '../f1-website/public/f1.db')
    
    sync_schedule(json_file, db_file)
