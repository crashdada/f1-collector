#!/usr/bin/env python3
"""
F1 NAS Syncer — 将采集到的数据同步至展示站目录

自动检测环境：
  - 本地开发（../f1-website/package.json 存在）→ 写入 public/data/ 和 public/
  - NAS 部署（无 package.json）→ 写入 data/ 和根目录

NAS 目录结构：                    本地目录结构：
  web/                             oc/
  ├── f1-collector/                ├── f1-collector/
  │   ├── syncer.py                │   ├── syncer.py
  │   └── *.json                   │   └── *.json
  └── f1-website/  (dist)          └── f1-website/  (源码)
      ├── index.html                   ├── package.json
      ├── f1.db                        ├── public/
      └── data/*.json                  │   ├── f1.db
                                       │   └── data/*.json
                                       └── src/

用法：
  python syncer.py               # 同步所有 JSON
  python syncer.py --schedule    # 仅同步赛程
  python syncer.py --db          # 同步数据库（f1.db）
  python syncer.py --all         # 同步 JSON + DB
  python syncer.py --scrape      # 先运行 scraper.py 再同步
"""

import json
import os
import shutil
import argparse
import subprocess
import sys
from datetime import datetime

# 路径计算
COLLECTOR_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(COLLECTOR_DIR)
WEBSITE_DIR = os.path.join(PARENT_DIR, 'f1-website')

# 环境检测：有 package.json 说明是本地源码环境
IS_LOCAL = os.path.exists(os.path.join(WEBSITE_DIR, 'package.json'))

if IS_LOCAL:
    # 本地开发：JSON → public/data/，DB → public/
    JSON_SOURCE = os.path.join(COLLECTOR_DIR, 'data')
    JSON_TARGET = os.path.join(WEBSITE_DIR, 'public', 'data')
    DB_TARGET = os.path.join(WEBSITE_DIR, 'public')
    ENV_NAME = '本地开发'
else:
    # NAS 部署：检测是否有 dist 目录（针对只部署生成的网页内容的情况）
    potential_dist = os.path.join(WEBSITE_DIR, 'dist')
    DEPLOY_ROOT = potential_dist if os.path.exists(potential_dist) else WEBSITE_DIR
    
    JSON_SOURCE = os.path.join(COLLECTOR_DIR, 'data')
    JSON_TARGET = os.path.join(DEPLOY_ROOT, 'data')
    DB_TARGET = DEPLOY_ROOT
    ENV_NAME = f'NAS 部署 (目标: {os.path.basename(DEPLOY_ROOT)})'

# 要同步的 JSON 文件
JSON_FILES = [
    'schedule_2026.json',
    'drivers_2026.json',
    'teams_2026.json',
]


def log(msg):
    ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print(f'[{ts}] {msg}')


def sync_json(filename):
    """同步单个 JSON 文件"""
    source = os.path.join(JSON_SOURCE, filename)
    target = os.path.join(JSON_TARGET, filename)

    if not os.path.exists(source):
        log(f'⚠ 源文件不存在: {source}')
        return False

    os.makedirs(JSON_TARGET, exist_ok=True)

    # 验证 JSON 合法性
    try:
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f'✗ JSON 格式错误 {filename}: {e}')
        return False

    # 跳过无变更的文件
    if os.path.exists(target):
        with open(target, 'r', encoding='utf-8') as f:
            try:
                if json.load(f) == data:
                    log(f'• {filename} 无变更，跳过')
                    return True
            except json.JSONDecodeError:
                pass

    shutil.copy2(source, target)
    count = len(data) if isinstance(data, list) else 'object'
    log(f'✓ {filename} ({count} entries) → {target}')
    return True


def sync_db():
    """同步 f1.db"""
    source = os.path.join(COLLECTOR_DIR, 'f1.db')
    target = os.path.join(DB_TARGET, 'f1.db')

    if not os.path.exists(source):
        log(f'⚠ 数据库文件不存在: {source}')
        return False

    if os.path.exists(target):
        if os.path.getsize(source) == os.path.getsize(target):
            log(f'• f1.db 大小未变 ({os.path.getsize(source)} bytes)，跳过')
            return True

    shutil.copy2(source, target)
    log(f'✓ f1.db ({os.path.getsize(target):,} bytes) → {target}')
    return True


def run_scraper():
    """运行 scraper.py"""
    scraper = os.path.join(COLLECTOR_DIR, 'scraper.py')
    if not os.path.exists(scraper):
        log('✗ scraper.py 不存在')
        return False

    log('🔄 运行 scraper.py ...')
    result = subprocess.run(
        [sys.executable, scraper],
        cwd=COLLECTOR_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        log(f'✗ scraper.py 失败:\n{result.stderr}')
        return False

    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            log(f'  scraper: {line}')
    log('✓ scraper.py 完成')
    return True


def main():
    parser = argparse.ArgumentParser(description='F1 数据同步工具')
    parser.add_argument('--schedule', action='store_true', help='仅同步赛程')
    parser.add_argument('--db', action='store_true', help='同步 f1.db')
    parser.add_argument('--all', action='store_true', help='JSON + DB 全部同步')
    parser.add_argument('--scrape', action='store_true', help='先采集再同步')
    args = parser.parse_args()

    log('=' * 50)
    log(f'F1 Syncer | 环境: {ENV_NAME}')
    log(f'采集端: {COLLECTOR_DIR}')
    log(f'JSON ←  {JSON_SOURCE}')
    log(f'JSON →  {JSON_TARGET}')
    log('=' * 50)

    if not os.path.exists(WEBSITE_DIR):
        log(f'✗ 展示站目录不存在: {WEBSITE_DIR}')
        sys.exit(1)

    if args.scrape:
        if not run_scraper():
            log('⚠ 采集失败，继续同步已有数据...')

    if args.schedule:
        sync_json('schedule_2026.json')
    elif args.db:
        sync_db()
    elif args.all:
        for f in JSON_FILES:
            sync_json(f)
        sync_db()
    else:
        for f in JSON_FILES:
            sync_json(f)

    log('同步完成 ✅')


if __name__ == '__main__':
    main()
