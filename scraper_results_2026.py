#!/usr/bin/env python3
"""
F1 2026 Race Results Scraper — 赛后成绩采集框架

功能：
  - 检测赛后窗口（比赛结束后 1-3 天自动触发）
  - 从 F1 官网采集比赛成绩
  - 输出结构化 JSON，供 syncer.py 同步到展示端

用法：
  python scraper_results_2026.py                  # 自动检测窗口
  python scraper_results_2026.py --force           # 强制采集最近一场
  python scraper_results_2026.py --round 3         # 采集指定轮次

注意：2026 赛季尚未开始，本脚本为预备框架。
      实际解析逻辑需根据赛季开始后的页面结构微调。
"""

import json
import os
import re
import sys
import datetime
import argparse

# 复用 scraper.py 的核心能力
from scraper import F1DataCollector


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
SCHEDULE_FILE = os.path.join(SCRIPT_DIR, 'data', 'schedule_2026.json')
RESULTS_DIR = os.path.join(SCRIPT_DIR, 'results_2026')


def load_schedule():
    """加载赛历"""
    if not os.path.exists(SCHEDULE_FILE):
        print(f'[!] 赛历不存在: {SCHEDULE_FILE}')
        return []
    with open(SCHEDULE_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def find_recent_race(schedule):
    """找到最近结束的比赛（赛后 1-3 天内）"""
    today = datetime.date.today()
    months = {
        'JAN': 1, 'FEB': 2, 'MAR': 3, 'APR': 4, 'MAY': 5, 'JUN': 6,
        'JUL': 7, 'AUG': 8, 'SEP': 9, 'OCT': 10, 'NOV': 11, 'DEC': 12
    }

    for race in schedule:
        if race.get('isTest', False):
            continue

        dates = race.get('dates', '')
        match = re.search(r'-\s+(\d+)\s+([A-Z]{3})', dates)
        if not match:
            continue

        day = int(match.group(1))
        month = months.get(match.group(2).upper())
        if not month:
            continue

        try:
            race_end = datetime.date(2026, month, day)
            delta = (today - race_end).days
            if 0 <= delta <= 3:
                return race
        except ValueError:
            continue

    return None


def find_race_by_round(schedule, round_num):
    """按轮次查找比赛"""
    for race in schedule:
        round_text = race.get('round', '')
        match = re.search(r'(\d+)', round_text)
        if match and int(match.group(1)) == round_num:
            return race
    return None


def scrape_race_results(collector, race):
    """
    采集单场比赛成绩
    
    TODO: 2026 赛季开始后，根据实际页面结构完善解析逻辑
    目前使用 scraper.py 中的 get_race_results() 作为基础
    """
    slug = race.get('slug', '')
    country = race.get('country', race.get('location', 'unknown'))
    round_text = race.get('round', '')

    # 构造结果页 URL
    # 格式可能为: /en/results/2026/races/round-X/slug/race-result
    result_url = f"{collector.base_url}/en/results/2026/races/{slug}/race-result"

    print(f'Race: 采集: {country} ({round_text})')
    print(f'   URL: {result_url}')

    # 获取页面 HTML
    html = collector.fetch_page(result_url, max_retries=2, initial_delay=60)
    if not html:
        print(f'   [!] 页面获取失败')
        return None

    # 解析成绩（直接传入已有 HTML，避免二次 fetch）
    results = collector.get_race_results(html)
    if not results:
        print(f'   [!] 未找到成绩数据（页面结构可能已变化）')
        return None

    # 构造输出
    output = {
        'round': round_text,
        'country': country,
        'slug': slug,
        'scraped_at': datetime.datetime.now().isoformat(),
        'results': results
    }

    print(f'   [OK] 获取到 {len(results)} 条成绩')
    return output


def save_results(data, race):
    """保存采集结果"""
    os.makedirs(RESULTS_DIR, exist_ok=True)

    slug = race.get('slug', 'unknown')
    filename = f'{slug}_results.json'
    filepath = os.path.join(RESULTS_DIR, filename)

    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f'   💾 保存至 {filepath}')
    return filepath


def main():
    parser = argparse.ArgumentParser(description='F1 2026 赛后成绩采集')
    parser.add_argument('--force', action='store_true',
                        help='强制采集最近一场（忽略窗口检测）')
    parser.add_argument('--round', type=int,
                        help='采集指定轮次的成绩')
    args = parser.parse_args()

    print('=' * 50)
    print('F1 2026 Results Scraper')
    print('=' * 50)

    schedule = load_schedule()
    if not schedule:
        sys.exit(1)

    collector = F1DataCollector(season=2026)

    # 确定目标比赛
    if args.round:
        race = find_race_by_round(schedule, args.round)
        if not race:
            print(f'[!] 未找到第 {args.round} 轮比赛')
            sys.exit(1)
    elif args.force:
        # 取最近的非测试赛事
        races = [r for r in schedule if not r.get('isTest', False)]
        race = races[-1] if races else None
        if not race:
            print('[!] 赛历中无有效赛事')
            sys.exit(1)
    else:
        race = find_recent_race(schedule)
        if not race:
            print('今天不在赛后窗口内，无需采集。')
            print('使用 --force 或 --round N 强制执行。')
            sys.exit(0)

    # 采集
    results = scrape_race_results(collector, race)
    if results:
        save_results(results, race)
        print('\n采集完成 [OK]')
    else:
        print('\n采集失败 [!]')
        sys.exit(1)


if __name__ == '__main__':
    main()
