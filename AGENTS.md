# AGENTS.md - Coding Guidelines for F1 Collector

## Build/Test/Lint Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Run main scraper (Core Workflow)
python scraper.py

# Sync data to web project
python sync_data.py

# Historical/Maintenance scripts (in maintenance/)
python maintenance/update_flags_json.py

# Research scripts (in research/)
# These are for debugging or exploring new data structures
python research/deep_search_2026.py
```

## Directory Structure
- `/` - Core logic, data files (JSON), and CI/CD configurations.
- `maintenance/` - Scripts for data correction and one-time updates (e.g., flag URL fixes).
- `research/` - Experimental scripts, HTML analysis, and data discovery tools.

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
