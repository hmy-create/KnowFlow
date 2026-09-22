# KnowFlow Portfolio Documentation

本目录记录 KnowFlow 从产品问题定义到可信 RAG 设计、评测与工程化落地的核心材料。

## Documents

### 1. System Architecture

[02_architecture.md](02_architecture.md)

介绍 KnowFlow 的整体技术架构，以及 Router、Permission、Version、Retrieval、Evidence State、Citation、Trace、Eval 与 Docker 的关系。

### 2. Business Flow

[03_business_flow.md](03_business_flow.md)

从 AI 产品经理视角说明 KnowFlow 为什么需要 Permission、Version、Clarify、Conflict、Refuse 等机制。

### 3. Trusted RAG Design

[04_trusted_rag.md](04_trusted_rag.md)

解释 KnowFlow 与普通 RAG 的核心区别，以及 Permission-aware、Version-aware、Evidence State、Citation 与 Trace 的可信设计。

### 4. Eval & Badcase

[05_eval_badcase.md](05_eval_badcase.md)

记录自动评测体系、代表性 Badcase、Root Cause Analysis 与 Regression 闭环。

---

> 本项目所有企业制度与业务数据均为模拟测试数据。