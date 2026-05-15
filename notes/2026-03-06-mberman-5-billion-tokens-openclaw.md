---
title: I&#39;ve spent 5 BILLION tokens perfecting OpenClaw
channel: Matthew Berman
duration: 40:00
date: 2026-02-24
---

# I've spent 5 BILLION tokens perfecting OpenClaw

**频道**: Matthew Berman
**发布**: 2026-02-24
**时长**: 40:00
**链接**: https://www.youtube.com/watch?v=3110hx3ygp0

## 核心观点

### 1. 多版本 Prompt 管理：不同模型需要不同的提示策略
[00:09:13 - 00:11:30]

不同模型有不同的提示最佳实践。例如 Claude Opus 不喜欢全大写，而 GPT 则欢迎全大写强调。Matthew 建立了双版本提示栈：根目录是 Claude 优化的文件，另一个文件夹存放其他模型的优化版本。每晚自动同步检查，确保两个版本的核心信息一致且无漂移，如有差异会通过 Telegram 提醒他修正。这种做法让模型切换变得无缝，同时保持提示质量。

### 2. 把 OpenClaw 当作"全职员工"：赋予独立邮箱和工作流
[00:06:54 - 00:08:56]

Matthew 给 OpenClaw 分配了独立的邮箱地址，让它像真正的员工一样处理业务邮件。工作流程包括：从三个邮箱账户拉取邮件、隔离和 Frontier 扫描（安全检测）、评分分类、更新 HubSpot、打标签、高风险邮件推送到 Telegram、生成本地存储并撰写回复草稿。这个渐进式授权过程让他逐步信任 OpenClaw 处理从邮件到销售管道的各种任务。

### 3. CRM 系统的智能整合：邮件、日历、知识库的跨域连接
[00:14:58 - 00:16:58]

OpenClaw 的 CRM 系统不仅扫描和分类邮件，还会主动研究联系人公司、自动发现和保存相关新闻文章。真正的价值在于跨系统整合：当收到潜在赞助商邮件时，它能参考之前的类似对话、查找知识库中关于该公司的文章、自动汇总所有相关信息。这种连接能力让 OpenClaw 能够做出超越简单数据存储的智能决策。

### 4. 会议智能：从转录到行动项的自动化流程
[00:17:28 - 00:18:46]

使用 Fathom 笔记机器人自动转录所有会议。转录后，OpenClaw 匹配参会者到 CRM、提取洞察和行动项、生成本地嵌入（使用 Nomic 模型），如有行动项则发送到 Telegram 请求确认后同步到 Todoist 和 HubSpot。系统还能自动识别每个行动项的负责人并关联到正确的 HubSpot deal，实现完全自动化的会议后续管理。

### 5. 知识库：内容收集与语义检索的个人图书馆
[00:18:48 - 00:20:52]

知识库是 Matthew 存放所有想保存内容的地方——文章、视频、推文等。通过 Telegram 或 Slack 的保存命令，OpenClaw 会抓取内容、进行安全检查、分块嵌入、存入 SQLite 数据库并跨平台分享给团队。关键价值在于：可与 CRM 联动自动发现联系人相关文章、支持自然语言语义查询、帮助生成视频创意时引用相关素材。

### 6. 多层安全架构：从网络层到数据层的纵深防御
[00:21:56 - 00:24:18]

Matthew 实施了多层安全机制：网络层包括网关加固和 SSH 密钥认证；输入层有提示注入和 SQL 注入检测、沙箱隔离、Frontier 扫描；输出层对敏感信息和个人身份信息进行脱敏；数据层使用加密数据库、数据分类分级、预提交钩子阻止敏感文件上传。还有夜间安全委员会检查、系统和 Cron 健康检查等自动化监控。

### 7. Cron 调度策略：在配额限制下优化资源使用
[00:24:54 - 00:26:06]

对于有 API 配额限制的用户，Matthew 建议将大型 Cron 任务分散到夜间执行。例如凌晨 1 点 Instagram 分析、1:15 X/Twitter 分析、1:30 YouTube、2 点 CRM 更新等。这样做的好处是避免白天活跃使用 OpenClaw 时触发额外的配额消耗，确保主任务有足够资源，同时保证后台数据同步任务按时完成。

### 8. 记忆问题解决方案：使用 Topic 分离上下文
[00:26:08 - 00:27:55]

很多人抱怨 OpenClaw 记忆系统差，但 Matthew 从未遇到问题。他给出两个关键建议：第一，使用 Telegram 群组的 Topic 功能，每个话题有独立上下文，减少了需要记住的内容量，只保留相关讨论；第二，定期检查 `/status` 命令中的上下文使用率，如果接近满载就需要清理或调整消息过期时间。他还设置了自动 Cron 来修剪提示文件，平均每两天精简约 10% 内容。

## 关键引用

> "I've slowly given it more and more authority, more and more permission to be automated from end to end. And there's still so much more to do. I actually have a vision where my OpenClaw can actually handle the sales pipeline all the way up until the point that a sponsor wants to get on a call with us."

> "Once you have all of this information, when you have a CRM, and when you scan your emails and calendar and Slack messages, a knowledge base, once you have all of that, OpenClaw will start to make connections that you didn't even think were possible."

> "If you're not storing absolutely everything... you really should be store everything."

> "I basically haven't touched memory and it has worked great. So many of you have talked about how bad the memory system is in OpenClaw, how it constantly forgets things. And I think it actually can be solved by one thing."