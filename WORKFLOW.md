# F1 Data Collection Workflow

本文档详细说明了 F1 2026 赛季数据的采集、处理、增强及同步流程。

---

## 🛠️ 核心组件

1. **`scraper.py` (核心采集器)**
   - **功能**: 从 F1 官网爬取直播数据、比赛日程及原始结果。
   - **技术**: 
     - 基础解析：使用 `requests` 获取 HTML。
     - **RSC 解析**: 针对 2026 赛季，通过正则和 `BeautifulSoup` 解码 Next.js 的 RSC (React Server Component) 碎片数据（通常封装在 `data-f1rd-a7s-context` 的 Base64 中）。
   - **输出**: `schedule_2026.json`。

2. **`sync_data.py` (数据同步器)**
   - **功能**: 执行“混合架构”同步逻辑：
     - **日程同步**: 将 `schedule_2026.json` 同步至 `f1-website/src/data/`。
     - **结果注入**: 将赛后结果直接注入到 `f1-website/src/data/f1.db` (SQLite)。

3. **核心数据源**
   - **2026 调试源**: `debug_2026.html` (包含全量 24 站 Next.js 数据的本地快照)。

---

## 🔄 2026 增强管道 (2026 Enhancement Pipeline)

### 1. 高级数据提取
由于 2026 赛历数据在官网以碎片化 RSC 形式存在，采集流程包含以下关键步骤：
- **Base64 解码**: 提取 `data-f1rd-a7s-context` 属性并解码为 JSON。
- **混合大小写日期修复**: 从页面文本中提取 `13 - 15 Mar` 格式的日期，替代原始全大写或 "TBC" 站位符。

### 2. 视觉资产映射
- **本地 SVG 国旗**: 
  - 存储于 `assets/flags/`。
  - 规则：所有 SVG 均标准化为 `viewBox="0 0 56 56"`，支持前端圆形切边展示。
- **赛道线稿图 (Track Outlines)**:
  - 模式：使用 F1 官方 CDN 路径 `https://media.formula1.com/image/upload/.../2026track{slug}blackoutline.svg`。
  - 映射表：在 `research/final_refine_2026.py` 中定义维护（如 Australia -> `melbourne`, Belgium -> `spafrancorchamps`）。

---

## 📁 目录结构规范

- **`maintenance/`**: 存放修正脚本（如 `standardize_svgs.py`）。
- **`research/`**: 归档调研过程中产生的临时脚本、HTML 快照及碎片化数据包。
- **`assets/flags/`**: 官方 2026 风格 SVG 国旗库。

---

## 🚀 运维操作

### 修复赛历或资产
若赛历数据受损或赛道图不显示，请按顺序运行：
1. `python research/final_refine_2026.py` (执行全量 RSC 提取与资产映射)。
2. `python maintenance/standardize_svgs.py` (确保国旗缩放比例正确)。
3. `python sync_data.py` (推送至前端)。
