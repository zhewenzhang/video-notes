---
title: Building the Feedback Loop for LLM Apps — TensorZero
channel: Data Driven NYC
duration: 10:25
date: 2026-03-02
tags: ["#LLM", "#TensorZero", "#学习飞轮", "#MLOps", "#持续改进"]
---

# Building the Feedback Loop for LLM Apps — TensorZero

**视频信息：**
- 标题：Building the Feedback Loop for LLM Apps — TensorZero's Viraj Mehta | Data Driven NYC

- 频道：Data Driven NYC (The MAD Podcast with Matt Turck)

- 时长：10:25

- 观看数：5,325

- 整理时间：2026-03-02

---

## 🎯 核心问题

**TensorZero 解决的问题：**

> "Every time we thought about language model applications, there was this desired quality where if you run your language model application, you should build up a data set of historical information about that application that allows you to make your application better the next time."

**翻译：**
> "每次我们思考语言模型应用时，都有一个理想特性：如果你运行语言模型应用，应该能积累历史数据，让你的应用变得越来越好。"

---

## 📊 核心概念：Learning Flywheel（学习飞轮）

### 什么是 Learning Flywheel？

应用运行 → 积累数据 → 优化模型 → 应用变得更好 → 继续运行...
    ↑                                              ↓

    └────────────── 形成复利资产 ──────────────────┘

**目标：**
- 建立复合资产

- 最终形成防御性

- 持续改进，而非静态性能

---

## 🔧 TensorZero 的解决方案

### 架构设计

组件功能**Gateway**统一接口，连接所有 LLM 提供商**数据库**存储结构化日志，你完全控制**优化层**支持多种优化策略
### 关键特性

**1. 统一接口**
- 一个 API 连接所有主要 LLM 提供商

- 也支持开源服务框架

- 无需为每个提供商单独集成

**2. 数据主权**
- 所有数据存储在你控制的数据库

- 没有供应商锁定

- 可以自由迁移

**3. 实验管理**
- 可以轻松切换 3% 流量测试新模型

- 不需要修改客户端代码

- 实时观察效果

---

## 💡 关键洞察：Interface vs Implementation

**Viraj 的核心思想：**

> "You might think of a language model call as a remote procedure call where you send business variables to a gateway and then eventually you get back business variables. Whatever happens in the middle is an implementation detail."

**翻译：**
> "你可以把语言模型调用看作远程过程调用：发送业务变量到网关，最终返回业务变量。中间发生什么是实现细节。"

### 这意味着什么？

实现接口GPT-4 + Prompt A相同的业务接口Claude + Prompt B相同的业务接口复杂策略 + Prompt C相同的业务接口
**好处：**
- 可以自由切换实现

- 不需要修改客户端代码

- 可以 A/B 测试不同策略

---

## 🚀 Demo：动态上下文学习

### 实验设置

**任务：** 命名实体识别（NER）

**对比：**
- 蓝线：GPT-4o mini + 标准提示

- 橙线：动态上下文学习

**动态上下文学习原理：**
1. 运行模型，获取输出

2. 给出反馈（正确/错误）

3. 将正确示例存入向量数据库

4. 下次推理时检索最相似的正确示例

5. 作为上下文提供给模型

### 效果

- 橙线持续上升

- 蓝线保持水平

- **实时改进**：演讲过程中系统就在学习和改进

---

## 🎯 对比：传统 ML vs LLM

维度传统 ML当前 LLM**学习曲线**持续上升静态（表格）**改进方式**积累经验，持续学习预训练 + 后训练，然后固定**用户期望**模型会越来越好性能基本不变
**Viraj 的遗憾：**
> "Reinforcement learning papers you always see this nice curve that goes up and to the right... we don't really see that with language LLMs today."

**翻译：**
> "强化学习论文里你总能看到漂亮的上升曲线……但今天的 LLM 我们看不到这个。"

---

## 📋 支持的优化策略

策略说明**Prompt 优化**如 DSPy**Fine-tuning**开源或闭源模型**强化学习**从反馈中学习**推理时优化**如 OpenAI o1**动态上下文学习**检索相似正确示例
---

## 💡 对开发者的启示

### 为什么需要这个？

**当前问题：**
- 各种工具不协同

- 数据分散在不同系统

- ETL 和"胶带拼接"太麻烦

- 切换提供商需要重写代码

**TensorZero 解决：**
- 统一框架

- 同一数据模型

- 无锁定

- 快速实验

### 使用场景

- LLM 应用需要持续改进

- 需要积累业务特定的数据

- 想建立防御性资产

- 需要实验不同模型/策略

---

## 🔑 关键引用

**关于学习飞轮：**
> "That would build a compounding asset that would be valuable to your business and eventually would become defensible."

**关于接口与实现：**
> "Whatever happens in the middle is an implementation detail."

**关于实时学习：**
> "As I'm talking right now this system is actually improving and learning how to get better at this named entity recognition task."

---

_整理完成：2026-03-02_

_视频来源：Data Driven NYC_

_标签：#LLM #TensorZero #学习飞轮 #MLOps #持续改进_