---
title: Stanford CS336: Language Modeling from Scratch - Overview
channel: 1:18:59
duration: 2026-03-03
tags: ["#Stanford", "#CS336", "#LanguageModel", "#Tokenizer", "#LLM", "#深度学习"]
---

# Stanford CS336: Language Modeling from Scratch - Overview

**来源**: Stanford CS336 课程  
**讲师**: 待确认  
**主题**: 从零构建语言模型  
**时长**: 1:18:59  
**整理时间**: 2026-03-03 08:27

---

## 课程概述

### CS336 课程目标
**从零开始构建语言模型** - 深入理解 LLM 原理

**核心内容**:
1. Tokenization (分词)

2. 模型架构 (Transformer)

3. 训练流程

4. 评估方法

5. 优化技术

---

## 第一讲：Overview and Tokenization

### Tokenization 基础

**什么是 Token**:
- 文本的基本单位

- 可以是词、子词、或字符

- 影响模型性能的关键

**主流 Tokenizer**:
方法代表特点BPEGPT 系列平衡效率 + 词汇量WordPieceBERTGoogle 系采用UnigramSentencePiece多语言支持Char-简单但效率低
### 实践要点

**词汇量选择**:
- 太小：序列过长，计算慢

- 太大：Embedding 参数多

- 平衡点：32k-100k

**特殊 Token**:
- `[BOS]` / `[EOS]` - 序列边界

- `[PAD]` - 填充

- `[UNK]` - 未知词

- `[SEP]` - 分隔符

---

## 课程项目

**预期产出**:
1. 实现自己的 Tokenizer

2. 构建小型 Transformer

3. 训练语言模型

4. 评估生成质量

---

## 学习资源

### 前置知识
- Python 编程

- 线性代数

- 概率论

- 基础机器学习

### 参考材料
- CS336 课程网站

- 《Language Models from Scratch》- Sebastian Raschka

- Hugging Face Tokenizers

---

## 对我的启发

1. **从 0 构建是最佳学习** - 理解每个细节

2. **Tokenizer 很重要** - 常被忽视但影响巨大

3. **实践驱动** - 理论 + 代码结合

---

## 后续行动

- [ ] 完成 CS336 全部课程

- [ ] 实现自己的 Tokenizer

- [ ] 训练小型语言模型

- [ ] 对比不同 Tokenization 方法

---

_标签：#Stanford #CS336 #LanguageModel #Tokenizer #LLM #深度学习_