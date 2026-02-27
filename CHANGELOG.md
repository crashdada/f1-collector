# 更新日志 (Changelog) - F1 Collector

记录 `f1-collector` 数据采集引擎的迭代改动、爬虫升级与数据修复记录。

## 2026-02-27
### ✨ 新特性与优化
- **车手号码自动化管理**：
  - 新增 `scraper_official_numbers.py`：支持从 F1 官网自动抓取最新的车手号码映射。
  - 新增 `apply_number_updates.py`：支持手动/自动批量更新号码数据，并具备历史回溯功能。
- **号码历史保留逻辑**：更新 `data/drivers_config_2026.json` 结构，增加 `history.numbers` 字段。变更号码时，旧号码会自动备份至该数组，确保数据 100% 可追溯。
- **CI/CD 自动化闭环**：
  - 更新 `.github/workflows/scrape.yml`：增加了 `push` 触发器，修改配置或脚本后立即触发数据刷新。
  - 修复了 Action 中的 `git push` 权限细节，改用 `GH_PAT` 显式认证，彻底解决云端生成 JSON 后无法推送回仓库的“静默失败”问题。

### 📊 数据更新
- **2026 赛季号码对齐**：
  - Max Verstappen: 1 ➡️ 3 (History: [1])
  - Lando Norris: 4 ➡️ 1 (History: [4])
  - Arvid Lindblad: 17 ➡️ 41
  - Isack Hadjar: 20 ➡️ 6

## 2026-02-25
- **本地化路径策略**：修改 `scraper_drivers.py` 和 `scraper_teams.py`，默认将 JSON 中的图片路径生成为本地 `/photos/...` 路径，确保在离线或 CDN 网络波动时仍能正确显示头像。

## 2026-02-20
- **数据一致性对齐**：修复了 2026 赛季中部分车手/车队 Slug 的映射错误。
- **历史统计注入**：优化 `refine_with_stats.py`，增加环境变量 `F1_DB_PATH` 支持，以便在 GitHub Actions 和 本机/NAS 环境中灵活切换数据库源。
