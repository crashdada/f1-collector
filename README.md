<div align="center">

# F1 Data Hub - Collector

🏎️ **F1 官方数据自动化采集、处理与同步端**

[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![Data Pipeline](https://img.shields.io/badge/Pipeline-Active-success.svg)]()
[![Automated Season](https://img.shields.io/badge/Season-Dynamic-orange.svg)]()
</div>

----

## 🏁 简介 (Introduction)

**F1 Collector** 是 F1 Data Hub 项目的后端数据引擎。它专门针对 F1 官方网站的 RSC (React Server Component) 数据结构进行解析，实现对 F1 **赛历**、**车手**、**车队** 以及 **比赛成绩** 等数据的全自动抓取与结构化。

它旨在与展示端项目解耦：以极为克制且低频率的方式执行日常信息同步与爬虫任务，并将结果输出成干净、离线可用的 JSON 文件和 SQLite 历史数据库。

### ✨ 核心特性

- 🤖 **完全自适应赛季**: 告别硬编码！架构自动根据当前服务器所在的物理年份读取对应的动态数据（兼容任意未来的 2026 / 2027 赛季）。
- 🔌 **“热更新”同步机制**: 展示端无须重新构建（No rebuild），支持将产出的 JSON/DB 自动且安全地直推至 NAS、展示站等目标的 `data/` 结构下。
- 📦 **自动本地化资源**: 能够将官方包含限流鉴权的媒体 CDN 链接，无感知地替换为系统内置本地离线资源的结构。
- 🕒 **GitHub Actions 配合**: 内置全自动定时任务脚本，并在进入“赛后三天窗口期”时动态触发赛果计分的抓取更新。

---

## 🚀 极速上手 (Quick Start)

请确保你的环境搭载了 **Python 3.9+**。

```bash
# 1. 安装项目纯净依赖
pip install -r requirements.txt

# 2. 一键执行新赛季/当赛季的全链路爬虫
python scraper_drivers.py    # 抓取车手
python scraper_teams.py      # 抓取车队

# 3. 数据同步与分发
python syncer.py --all
```

---

## 📖 开发者与架构文档

这只是一个门面！关于项目的详尽架构设计图、文件目录结构、以及全方位的命令行工具使用指南，请移步阅读我们精心整理的万物指南：

👉  [**《AGENTS.md - F1 Collector 代码规范与系统工作流》**](./AGENTS.md)
