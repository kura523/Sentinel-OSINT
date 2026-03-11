#  Sentinel-OSINT 威胁猎人框架

**Sentinel-OSINT** 是一个由 AI 驱动的自动化开源威胁情报（OSINT）采集与分析系统。
本项目旨在解决安全研究人员每天面对海量、非结构化且充满噪音（如垃圾外挂库、币圈营销）的安全资讯痛点。通过引入异步并发爬虫与大语言模型（LLM），实现从数据采集、降噪提炼、结构化入库到可视化大屏展示的全链路自动化。

##  核心特性

* **异步多源采集**：基于 `httpx` + `asyncio` 的高并发采集引擎，实时监控 GitHub 上的最新 CVE/PoC 以及各大顶级安全博客（Unit 42, Project Zero 等）的 RSS 订阅。
* **AI 降噪与提炼**：接入大模型（如 DeepSeek/GPT），通过精准的提示词工程（Prompt Engineering），自动过滤加密货币、游戏外挂等 SEO 垃圾库，并从长文本中提取精准的 `CVE 编号`、`受影响组件`及生成中文摘要。
* **全景态势大屏**：内置基于 FastAPI + Vue3 + Tailwind CSS 的轻量级 Web 面板，提供暗黑极客风的数据看板，实时渲染最新高价值情报。
* **无人值守调度**：内置基于 `schedule` 的调度中心，结合 Redis 集合去重，实现每天自动抓取、清洗并生成精美的 Markdown 格式《今日威胁情报日报》。

##  项目架构

```text
Sentinel-OSINT/
├── collectors/               # 数据采集器模块
│   ├── github_monitor.py     # GitHub 实时关键字爬虫
│   └── rss_monitor.py        # 安全博客 RSS 并发采集器
├── core/                     # 核心业务逻辑
│   ├── ai_engine.py          # LLM 交互与数据清洗引擎
│   ├── api.py                # FastAPI 后端数据接口
│   ├── database.py           # SQLite 持久化管理
│   └── reporter.py           # Markdown 日报生成器
├── reports/                  # 自动生成的日报存放目录
├── dashboard.html            # 纯前端 Web 可视化大屏
├── main.py                   # 爬虫与分析流水线入口
├── scheduler.py              # 全局自动化定时调度守护进程
└── requirements.txt          # 项目依赖

```

##  环境依赖与安装

本项目推荐在 Linux (Ubuntu/Debian) 或 WSL 环境下运行。

### 1. 基础环境准备

请确保系统中已安装 Python 3.10+ 和 Redis 服务：

```bash
sudo apt update
sudo apt install python3-pip python3-venv redis-server
sudo service redis-server start

```

### 2. 克隆与安装依赖

```bash
git clone https://github.com/YourUsername/Sentinel-OSINT.git
cd Sentinel-OSINT

# 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装核心依赖库
pip install httpx asyncio redis openai fastapi uvicorn schedule feedparser jinja2

```

### 3. 配置 API Key

打开 `core/ai_engine.py` 或 `main.py`，将 `YOUR_API_KEY` 替换为你真实有效的大模型 API Key。

## 运行指南

系统分为“可视化前端接口”和“后台自动化调度”两部分，建议在不同的终端窗口（或使用 `tmux`/`nohup`）中分别运行：

### 启动可视化大屏 (API 服务)

在虚拟环境中运行：

```bash
python3 core/api.py

```

服务启动后，直接在浏览器中双击打开项目根目录下的 `dashboard.html`，即可看到实时更新的威胁情报中心。

### 启动后台调度中心 (Daemon)

在虚拟环境中运行：

```bash
python3 scheduler.py

```

调度中心默认每天早上 08:00 自动执行一轮完整的“数据抓取 -> AI 清洗 -> 数据库更新 -> Markdown 日报生成”流程。你可以在 `scheduler.py` 中修改触发频率（如改为每分钟执行用于本地测试）。

*生成的日报会存放在 `reports/` 目录下。*

##  数据清理

系统使用 Redis 进行情报去重。如果你需要重置系统的“已读记忆”以进行深度测试，请运行：

```bash
redis-cli del sentinel:seen_ids sentinel:seen_urls

```

## 📜 License

本项目采用 [MIT License](https://www.google.com/search?q=LICENSE) 许可协议。欢迎提交 PR 或 Fork 进行二次开发！

