# AGENTS.md - Coding Guidelines for F1 Collector

## Build/Test/Lint Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main scraper (Core Workflow)
python scraper.py

# Sync data to web project (auto-detects local vs NAS)
python syncer.py

# Sync with options
python syncer.py --schedule    # Schedule JSON only
python syncer.py --db           # Database only
python syncer.py --all          # JSON + DB
python syncer.py --scrape       # Run scraper first, then sync
```

## Directory Structure
```
f1-collector/
├── scraper.py                    # 赛历采集 → data/schedule_2026.json
├── scraper_drivers_2026.py       # 车手数据生成 → data/drivers_2026.json
├── scraper_teams_2026.py         # 车队数据生成 → data/teams_2026.json
├── scraper_results_2026.py       # 赛后成绩采集框架（待实测）
├── syncer.py                     # 统一同步（自动检测本地/NAS）
├── refine_with_stats.py          # 数据增强辅助
├── requirements.txt
├── AGENTS.md / WORKFLOW.md / README.md
├── data/                         # 📦 采集产物（脚本与数据分离）
│   ├── schedule_2026.json
│   ├── drivers_2026.json
│   └── teams_2026.json
├── results_2026/                 # 赛后成绩（待赛季开始）
├── baseline_2026-02-12/          # 数据基线快照
├── assets/flags/                 # 国旗 SVG（56x56）
├── maintenance/
│   └── standardize_svgs.py
├── research/
│   ├── final_refine_2026.py
│   ├── extract_rsc_2026.py
│   └── debug_2026.html
└── .github/workflows/
    └── scrape.yml                # GitHub Actions：每日自动采集
```

## Data Architecture
- 脚本在根目录，产物在 `data/` — **脚本与数据分离**
- `syncer.py` 从 `data/` 读取 JSON，同步到展示端
- 展示端通过运行时 `fetch()` 加载，**不打包进 JS**，支持热更新

## Code Style Guidelines

### Python Conventions
- **Naming**: snake_case for functions/variables, PascalCase for classes, UPPER_CASE for constants
- **Indentation**: 4 spaces (no tabs)
- **Line length**: ~100 characters (soft limit)
- **Quotes**: Use single quotes for strings unless escaping is needed

### Imports
- Group imports: stdlib first, third-party second, local last
- Each group separated by a blank line
- Example:
  ```python
  import json
  import re
  import time
  
  import requests
  from bs4 import BeautifulSoup
  ```

### Functions & Classes
- Use docstrings for public methods (English preferred, Chinese acceptable for context)
- Keep functions focused and under 50 lines when possible
- Use `_` prefix for private methods (e.g., `_reconstruct_next_data`)

### Error Handling
- Use try/except with specific exceptions when possible
- Print errors with descriptive messages: `print(f"Error: {e}")`
- Return empty lists/None on failure rather than crashing

### Comments
- Mix of English and Chinese is acceptable (reflects project history)
- Use comments to explain WHY, not WHAT (code should be self-documenting)
- Inline comments for complex regex or parsing logic

### JSON/Data Handling
- Always use `ensure_ascii=False` when dumping JSON with non-ASCII content
- Use `encoding='utf-8'` for all file operations
- Validate data existence before accessing nested structures

### File Organization
- Keep utility scripts in root directory
- Output data files to project root
- Use descriptive filenames with timestamps when appropriate

## Git Workflow
- Automated via GitHub Actions (`.github/workflows/scrape.yml`)
- Schedule: Daily at 2 AM UTC
- Workflow commits JSON changes automatically
- Manual trigger available via `workflow_dispatch`

## Dependencies
- requests
- beautifulsoup4
- Python 3.9+ (as per CI configuration)

## Notes
- This is a data scraping project - be mindful of rate limiting
- F1 website structure may change; parsers are fragile
- Always check if data is "TBC" (To Be Confirmed) before processing
