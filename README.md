# 🚀 AI 内容搬运工 | AI Content Factory |20260121
自动抓取 Twitter 上热门 AI 内容，并生成小红书风格图文，提供后台预览与模拟发布。
An AI-powered content pipeline that:
- Automatically fetches trending AI papers from Twitter
- Rewrites them into Xiaohongshu-style viral posts using LLMs
- Provides a lightweight CMS to preview and publish content
---

## 🌟 项目简介

大家好，我是谭晨！  
这个项目的目标是：**自动抓取 Twitter 热门 AI 内容 → 用 AI 改写为小红书风格图文 → 提供后台预览 & 模拟发布**。  

核心理念：  
> 作为一个 AI Hacker / Vibe Coder，我能把一个模糊需求拆成一个可运行的闭环，用最短时间实现 AI 产品落地 🔧✨

---

## 🎯 核心功能

- 🐦 自动抓取 Twitter 热门 AI 论文/推文  
- 🤖 GPT-5 （没毕业无信用卡无api）/Deepseek 改写成小红书风格文案  
  - 标题 + 正文 + 话题标签 + 图片建议  
- 🖥 Streamlit 后台预览、编辑、一键模拟发布、仿真小红书发布页
- ⏰ 每日自动抓取 & 成本可视化  

---

## 🛠 技术栈

| 模块 | 技术 / 工具 |
|------|------------|
| LLM | GPT-5/Deepseek |
| 抓取 | Apify Twitter Scraper  |
| Agent 编排 | LangChain (JS) |
| 前端 | Streamlit |
| 部署 | Streamlit |
| 数据存储 | JSON (`content_pool.json`) |

---

## 📌 产品流程图

```text
用户点击「生成内容」/或者自动抓取
         |
         v
fetch_trending_ai_papers() -> 抓取 3-5 条热门推文
         |
         v
generate_xhs_post() -> GPT-5/Deepseek 改写成小红书风格文案
         |
         v
Streamlit 前端展示：
 - 左侧功能导航
 - 右侧内容池 AI 生成内容预览 & 编辑 &模拟发布
         |
         v
更新状态 & 数据保存到 content_pool.json


