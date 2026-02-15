#!/usr/bin/env python3
"""
F1 Data Syncer — 跨环境数据同步工具

自动检测环境并定位展示站路径：
  - 本地开发（源码目录）：检测到 package.json → 写入 public/data/ 和 public/
  - NAS 部署（网页产物）：检测到 dist/ 目录 → 优先写入 dist/data/ 实现热更新
  - NAS 部署（根目录模式）：若无 dist/ → 降级写入根目录 data/

NAS 实际部署结构 (模式 B):               本地开发源码结构 (模式 A):
  /workspace/ (或 web/)                 /your-path/oc/ (或 Desktop/oc/)
  ├── f1-collector/ (抓取工具)           ├── f1-collector/ (抓取工具)
  │   ├── syncer.py                     │   ├── syncer.py
  │   └── data/*.json                   │   └── data/*.json
  └── f1-website/   (生产产物)           └── f1-website/   (React 源码)
      ├── index.html                    ├── package.json
      ├── f1.db                         ├── public/
      └── data/*.json  <-- 同步点        │   ├── f1.db
                                        │   └── data/*.json  <-- 同步点
                                        └── src/

用法：
  python syncer.py               # 同步所有 2026 JSON (热更新推荐)
  python syncer.py --db          # 同步 f1.db (仅当 collector 目录下有 db 时)
  python syncer.py --all         # 同步 JSON + DB
  python syncer.py --scrape      # 运行抓取并立即同步至网页
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

# 环境检测：有 package.json 说明是本地源码开发环境
IS_LOCAL = os.path.exists(os.path.join(WEBSITE_DIR, 'package.json'))

JSON_SOURCE = os.path.join(COLLECTOR_DIR, 'data')

if IS_LOCAL:
    # 本地开发：目标是源码的 public 目录
    ENV_NAME = '本地源码环境 (Development)'
    JSON_TARGET = os.path.join(WEBSITE_DIR, 'public', 'data')
    DB_TARGET = os.path.join(WEBSITE_DIR, 'public')
else:
    # NAS 部署：目标通常是构建好的产物目录 (dist)
    potential_dist = os.path.join(WEBSITE_DIR, 'dist')
    if os.path.exists(potential_dist):
        DEPLOY_ROOT = potential_dist
        ENV_NAME = f'NAS 生产构建环境 (Target: {os.path.basename(potential_dist)})'
    else:
        DEPLOY_ROOT = WEBSITE_DIR
        ENV_NAME = f'NAS 根目录环境 (Target: {os.path.basename(WEBSITE_DIR)})'
    
    JSON_TARGET = os.path.join(DEPLOY_ROOT, 'data')
    DB_TARGET = DEPLOY_ROOT

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
        log(f'[!] 源文件不存在: {source}')
        return False

    os.makedirs(JSON_TARGET, exist_ok=True)

    # 验证 JSON 合法性
    try:
        with open(source, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        log(f'[!] JSON 格式错误 {filename}: {e}')
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
    log(f'[OK] {filename} ({count} entries) → {target}')
    return True


def sync_db():
    """同步 f1.db"""
    source = os.path.join(COLLECTOR_DIR, 'f1.db')
    target = os.path.join(DB_TARGET, 'f1.db')

    if not os.path.exists(source):
        log(f'[!] 数据库文件不存在: {source}')
        return False

    if os.path.exists(target):
        if os.path.getsize(source) == os.path.getsize(target):
            log(f'• f1.db 大小未变 ({os.path.getsize(source)} bytes)，跳过')
            return True

    shutil.copy2(source, target)
    log(f'[OK] f1.db ({os.path.getsize(target):,} bytes) → {target}')
    return True


def sync_assets():
    """同步 assets 目录 (包含新赛季本地化图片)"""
    source = os.path.join(COLLECTOR_DIR, 'assets')
    target = os.path.join(DB_TARGET, 'photos')  # 对应 public/photos 或 dist/photos

    if not os.path.exists(source):
        return True

    log(f'[...] 同步 assets 目录 → {target}')
    
    # 使用 shutil.copytree 实现增量或覆盖同步
    if os.path.exists(target):
        # 如果目标已存在，手动遍历拷贝以实现“合并/覆盖”
        for root, dirs, files in os.walk(source):
            relative_path = os.path.relpath(root, source)
            dest_dir = os.path.join(target, relative_path)
            os.makedirs(dest_dir, exist_ok=True)
            for f in files:
                src_file = os.path.join(root, f)
                dst_file = os.path.join(dest_dir, f)
                # 仅当文件不存在或大小不同时拷贝
                if not os.path.exists(dst_file) or os.path.getsize(src_file) != os.path.getsize(dst_file):
                    shutil.copy2(src_file, dst_file)
    else:
        shutil.copytree(source, target)
    
    log(f'[OK] Assets 目录同步完成')
    return True


def run_scraper():
    """运行 scraper.py"""
    scraper = os.path.join(COLLECTOR_DIR, 'scraper.py')
    if not os.path.exists(scraper):
        log('[!] scraper.py 不存在')
        return False

    log('[...] 运行 scraper.py ...')
    result = subprocess.run(
        [sys.executable, scraper],
        cwd=COLLECTOR_DIR,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        log(f'[!] scraper.py 失败:\n{result.stderr}')
        return False

    if result.stdout.strip():
        for line in result.stdout.strip().split('\n'):
            log(f'  scraper: {line}')
    log('[OK] scraper.py 完成')
    return True


def main():
    parser = argparse.ArgumentParser(description='F1 数据同步工具')
    parser.add_argument('--schedule', action='store_true', help='仅同步赛程')
    parser.add_argument('--db', action='store_true', help='同步 f1.db')
    parser.add_argument('--assets', action='store_true', help='仅同步 assets 资源')
    parser.add_argument('--all', action='store_true', help='JSON + DB + Assets 全部同步')
    parser.add_argument('--scrape', action='store_true', help='先采集再同步')
    args = parser.parse_args()

    log('=' * 50)
    log(f'F1 Syncer | 环境: {ENV_NAME}')
    log(f'采集端: {COLLECTOR_DIR}')
    log(f'JSON ←  {JSON_SOURCE}')
    log(f'JSON →  {JSON_TARGET}')
    log('=' * 50)

    if not os.path.exists(WEBSITE_DIR):
        log(f'[!] 展示站目录不存在: {WEBSITE_DIR}')
        sys.exit(1)

    if args.scrape:
        if not run_scraper():
            log('[!] 采集失败，继续同步已有数据...')

    if args.schedule:
        sync_json('schedule_2026.json')
    elif args.db:
        sync_db()
    elif args.assets:
        sync_assets()
    elif args.all:
        for f in JSON_FILES:
            sync_json(f)
        sync_db()
        sync_assets()
    else:
        # 默认同步所有 JSON 和 Assets
        for f in JSON_FILES:
            sync_json(f)
        sync_assets()

    log('同步完成 [OK]')


if __name__ == '__main__':
    main()
