# 禁用 Skills 索引

> 记录被禁用的 Skills 及其触发关键词，方便后续提示启用
> 最后更新：2026-03-26

---

## 已禁用 Skills 列表

| Skill | 功能 | 触发关键词 | 启用命令 |
|-------|------|-----------|---------|
| tarot | 塔罗牌占卜 | 塔罗、占卜、运势 | 启用 tarot skill |
| night-owl-shrimp | 深夜情绪陪伴 | 深夜、睡不着、孤独 | 启用 night-owl-shrimp skill |
| nutritionist | 营养师 | 饮食、营养、健康 | 启用 nutritionist skill |
| study-habits | 学习习惯 | 学习、备考、复习 | 启用 study-habits skill |
| slack-gif-creator | Slack GIF | Slack、GIF、动图 | 启用 slack-gif-creator skill |
| movie-advisor | 电影推荐 | 电影、推荐、影评 | 启用 movie-advisor skill |
| music-recommender | 音乐推荐 | 音乐、歌单、推荐 | 启用 music-recommender skill |
| travel-planner | 旅行规划 | 旅行、攻略、行程 | 启用 travel-planner skill |
| habit-coach | 习惯教练 | 习惯、自律、打卡 | 启用 habit-coach skill |
| habit-tracker | 习惯追踪 | 习惯、追踪、连续 | 启用 habit-tracker skill |
| goal-tracker | 目标追踪 | 目标、OKR、里程碑 | 启用 goal-tracker skill |
| earnings-tracker | 财报追踪 | 财报、earnings、业绩 | 启用 earnings-tracker skill |
| macro-monitor | 宏观经济 | GDP、利率、CPI | 启用 macro-monitor skill |
| market-researcher | 市场调研 | 市场调研、竞品分析 | 启用 market-researcher skill |
| quant-backtest | 量化回测 | 量化、回测、策略 | 启用 quant-backtest skill |
| github-ai-trends | GitHub AI趋势 | GitHub趋势、AI项目 | 启用 github-ai-trends skill |
| arxiv-reader | 论文阅读 | 论文、arXiv、学术 | 启用 arxiv-reader skill |
| arxiv-watcher | 论文监控 | 论文、最新研究 | 启用 arxiv-watcher skill |
| citation-manager | 引用管理 | 引用、参考文献 | 启用 citation-manager skill |
| internal-comms | 内部沟通 | 内部沟通、status report | 启用 internal-comms skill |
| analytics-dashboard | 数据看板 | 数据看板、KPI | 启用 analytics-dashboard skill |
| log-analyzer | 日志分析 | 日志、分析、监控 | 启用 log-analyzer skill |
| content-repurposer | 内容复用 | 内容复用、多平台 | 启用 content-repurposer skill |
| doc-coauthoring | 文档协作 | 协作文档、proposal | 启用 doc-coauthoring skill |
| theme-factory | 主题工厂 | 主题、样式、颜色 | 启用 theme-factory skill |
| brand-guidelines | 品牌规范 | 品牌、规范、设计 | 启用 brand-guidelines skill |
| algorithmic-art | 算法艺术 | 艺术、生成艺术、p5.js | 启用 algorithmic-art skill |
| web-artifacts-builder | Web组件 | React、组件、artifact | 启用 web-artifacts-builder skill |
| video-script | 视频脚本 | 视频脚本、分镜、Vlog | 启用 video-script skill |
| note-organizer | 笔记整理 | 笔记整理、知识管理 | 启用 note-organizer skill |
| idea-validator | 创意验证 | 创意验证、竞品分析 | 启用 idea-validator skill |
| humanize-ai-text | AI文本人性化 | 改写、人性化、检测 | 启用 humanize-ai-text skill |
| niuamaxia-scheduler | 日程管理 | macOS日程、日历 | 启用 niuamaxia-scheduler skill |
| agent-mbti | MBTI人格 | MBTI、人格测试 | 启用 agent-mbti skill |
| proactive-agent | 主动代理 | 主动、WAL、自动化 | 启用 proactive-agent skill |
| skill-creator | Skill创建 | 创建skill、编写skill | 启用 skill-creator skill |
| skill-vetter | Skill审查 | 审查skill、安全检查 | 启用 skill-vetter skill |
| mcp-builder | MCP构建 | MCP、FastMCP | 启用 mcp-builder skill |
| webapp-testing | Web测试 | Playwright、测试 | 启用 webapp-testing skill |
| healthcheck | 健康检查 | 安全、检查、hardening | 启用 healthcheck skill |
| node-connect | 节点连接 | 配对、连接失败 | 启用 node-connect skill |
| video-frames | 视频帧提取 | 视频帧、ffmpeg | 启用 video-frames skill |
| weather | 天气查询 | 天气、温度（有weather-advisor替代） | 启用 weather skill |

---

## 提示模板

当用户提到禁用 Skill 的功能时，回复：

> 这个功能需要 **{skill_name}** Skill，当前为禁用状态。
> 
> 要启用吗？说：**"启用 {skill_name} skill"**

---

## 已启用 Skills（核心功能）

以下 Skills 保持启用，不列入禁用索引：

- ✅ online-search（联网搜索）
- ✅ web_search / web_fetch（网页抓取）
- ✅ docx / xlsx / pptx / pdf（文档处理）
- ✅ canvas-design / frontend-design（设计）
- ✅ tencent-docs / feishu-*（办公协作）
- ✅ email-skill / imap-smtp-email（邮件）
- ✅ code-reviewer / explain-code / project-manager（自定义）
- ✅ searching-assistant / writing-assistant / task-dispatcher / web-crawler-doc（自定义）
- ✅ qclaw-env / qclaw-openclaw / qclaw-rules（系统）
- ✅ multi-search-engine / tech-news-digest / news-summary（搜索新闻）
- ✅ cloud-upload-backup（云存储）
- ✅ weather-advisor（天气）
- ✅ qclaw-calendar-guide（日程）
- ✅ find-skills / skillhub_install（Skill管理）
- ✅ memory_search / memory_get（记忆）
- ✅ browser / canvas / exec / read / write / edit（基础工具）
- ✅ message / tts（消息语音）
- ✅ sessions_* / subagents / agents_list（会话管理）
- ✅ gateway / cron（系统管理）
- ✅ 文件整理（文件管理）

---

## 维护规则

1. **禁用 Skill 时**：添加到上表
2. **启用 Skill 时**：从表中移除
3. **定期回顾**：每月检查是否有需要启用的 Skill
