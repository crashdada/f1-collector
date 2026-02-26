# AGENTS.md - F1 Collector 代码规范与工作流指南

本文档定义了 F1 Data Collector 项目的代码规范、编排规则和核心工作流。
系统已经过重构，能够根据当前日历年份自动处理动态赛季的抓取（例如 2026、2027 等）。

## 构建/测试/代码规范检查

```bash
# 安装依赖
pip install -r requirements.txt

# 运行主爬虫 (核心工作流，自动检测当前赛季)
python scraper.py

# 为当前赛季生成车手 (Drivers) 和 车队 (Teams) 数据
python scraper_drivers.py
python scraper_teams.py

# 同步数据到网站项目 (自动检测本地或 NAS 环境，自动将官方 CDN URL 替换为本地离线路径)
python syncer.py
python syncer.py --schedule     # 仅同步赛程 (Schedule) JSON
python syncer.py --db           # 仅同步数据库 (f1.db)
python syncer.py --assets       # 仅同步图片与资产数据 (photos/assets)
python syncer.py --all          # 同步所有：JSON + DB + 资产
python syncer.py --scrape       # 先运行爬虫，然后再同步

# 覆盖默认的本年度赛季参数 (多数脚本支持该命令行参数)
python scraper_results.py --season 2027
```

## 🏗️ 架构与设计原则

### 1. 职责分离 (Separation of Concerns)
- **采集端 (`f1-collector`)**: 仅负责抓取内容并生成数据文件（JSON / 数据库）。
- **展示端 (`f1-website`)**: 仅负责前端展示，不包含任何抓取相关的逻辑。
- **桥接中心 (`syncer.py`)**: 安全可靠地将数据从采集端同步至展示端。

### 2. 混合存储与热更新 (Hybrid Storage & Hot Reload)
- 动态数据（车手、车队、赛程）存放在 `data/*.json` 中。
- 历史比赛结果数据存放在 `data/f1.db` (SQLite 数据库) 中。
- 展示层（前端）会在**运行时**拉取这些数据。通过 `syncer.py` 更新的数据能够立即生效，不需要重新构建前端项目（无需 `npm run build`）。

## 目录结构
```
f1-collector/
├── scraper.py                    # 赛历采集 → data/schedule_{season}.json
├── scraper_drivers.py            # 车手数据生成 → data/drivers_{season}.json
├── scraper_teams.py              # 车队数据生成 → data/teams_{season}.json
├── scraper_results.py            # 赛后单场成绩采集 → results_{season}/
├── syncer.py                     # 统一同步器 (核心逻辑：实时更新展示端，自动处理路径)
├── refine_with_stats.py          # 注入历史统计数据至车手 JSON
├── data/                         # 📦 采集产物 (Source of Truth)
│   ├── f1.db                     # 历史数据库源文件
│   └── *_config_{season}.json    # 手动维护的底板或基础配置 (如 drivers_config_2026.json)
├── assets/                       # 视觉资源库 (由 syncer 同步至展示网站的 photos/ 目录下)
├── photos/                       # 额外照片存储仓库
└── .github/workflows/
    └── scrape.yml                # GitHub Actions：每日自动在云端采集
```

## 🔄 同步机制：`syncer.py`

这是一个统一的数据同步脚手架，具备**自动化环境侦测功能**：
- **本地开发环境**：检测到上级目录存在 `../f1-website/package.json`，则写入 `public/data/` 目录。
- **NAS 生产环境部署**：未找到 `package.json` 时，自动降级写入 `dist/data/` （或网站根目录 `data/`）。

核心的同步逻辑不仅是复制文件，还会**自动拦截和修改 JSON 格式数据**，将其中的官方动态网络 CDN 图片路径强行替换为前端统一架构下的本地离线资源目录 (`/photos/...`)。

## 📅 赛前与日常运维任务 (Pre-Race / Setup)

1. **采集基础数据**：
   ```bash
   python scraper.py                          # 采集赛历
   ```
2. **生成包含赛季状态的动态团队与车手内容**：
   ```bash
   python scraper_drivers.py
   python scraper_teams.py
   # 若数据库中有历史数据需要与新赛季的数据整合用于展示，推荐运行：
   python refine_with_stats.py
   ```
3. **将内容推送到前端展示端**：
   ```bash
   python syncer.py --all
   ```

## 🏁 赛中/赛后数据收尾 (Post-Race)

1. **检测窗口并获取最新单场比赛成绩**：
   ```bash
   python scraper_results.py             # 将自动判断今天是否正处在“赛后3天内”的更新窗口期并执行结果抓取
   python scraper_results.py --force     # 若出问题或错过窗口期，使用此命令强制抓取距离现在最近的一场比赛
   ```

## 🖥️ NAS 部署与持续集成

```
Docker 自动定时任务机制 (配合 GitHub Action)
  ├── 1. 拉取 (Pull) 本仓库代码至云端
  ├── 2. 运行 scraper.py / scraper_drivers.py / scraper_teams.py 等爬虫保证数据最新
  ├── 3. 运行 scraper_results.py 动态检测是否需要更新成绩结果 (赛后生效)
  └── 4. 将所有产生的数据变更直接合并推送提交 (git commit --auto-update)
```
注意：基于该架构，实体化部署生产环境 (NAS) 时，只需要启动一个 Docker，每日定时将此 `f1-collector` 仓库最新分支重新拉取到本地，然后运行 `syncer.py` 后；再配合 Web Station 等服务软件将 `f1-website` 的构建好的 `dist` 目录设为静态托管，便能够一劳永逸地实现数据的**无头热更新体验**。

## 代码规范与系统原则 (Code Style Guidelines)

### Python 规范说明
- **命名规范 (Naming)**: 方法和变量名使用全小写下划线 `snake_case`；类名为驼峰格式 `PascalCase`。
- **缩进 (Indentation)**: 4 个空格对齐 (不使用 Tabs)。
- **行长度约束**: 尽量保持单行少于 ~100 字符。
- **引号用法**: 处理字符串时推荐使用单引号 `'`。若有需要逃避引号，可使用双引号。

### 错误捕获与数据处理 (Error Handling & Data)
- 需要充分支持优雅降级机制与配置补救措施 (Fallback Configurations)。
- 以 `try/except` 进行精准异常定位。
- 输出处理 JSON 文件时必须全面强制使用 `encoding='utf-8'` 和 `ensure_ascii=False` 以确保多语言环境的安全。

## 开发警示 (Notes)
- 这是一个数据采集相关的核心微服务项目——在请求和处理频率上务必小心避免被 F1 官方风控，并经常留意和防范 `TBC` ("To Be Confirmed"，待确认) 这类数据标识以免报错。
- 当下的自适应逻辑主要是调用了 `datetime.now().year`。如果需要离线或者提前测试后续赛季 (如 2027 赛季)，务必在需要跑测的个别测试脚本命令后加上 `--season 2027` 这个强制覆盖参数。
