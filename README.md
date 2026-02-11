# F1 Data Hub - Collector

这是 F1 数据的自动化采集、处理与同步端，专门针对 F1 官方网站的 RSC (React Server Component) 数据结构设计。

---

## 🔄 自动化流水线

1. **采集 (Harvesting)**: 解析官网 Next.js RSC 碎片数据，处理 Base64 负载。
2. **增强 (Refinement)**: 注入 GMT 时区偏移量、赛道线稿 CDN 映射、以及高清肖像取景参数。
3. **分发 (Sync)**: 执行 JSON 热更新同步与 SQLite 数据注入。

---

## 📂 核心指令

### 1. 赛前准备 (赛历/资产)
```bash
python scraper.py
python research/final_refine_2026.py
python sync_data.py --schedule-only
```

### 2. 赛中/赛后 (成绩)
```bash
python scraper_results_2026.py
python sync_data.py --results-only
```

---

## 🛠️ 环境要求
- Python 3.9+
- 依赖项见 `requirements.txt`

---

**详细操作规程请参考 [WORKFLOW.md](./WORKFLOW.md)**
