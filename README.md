# KnowFlow

> **Enterprise Trusted Knowledge Collaboration Agent**  
> 面向企业内部制度查询、流程答疑与知识治理的可信 RAG Agent

KnowFlow 从 Dify POC 逐步迁移为可测试、可观测、可部署的 FastAPI Demo，重点解决企业知识问答中的 **权限越权、版本错配、知识冲突、条件缺失与无依据强答** 问题。

不同于传统：

`Query → Retrieve → LLM → Answer`

KnowFlow 在回答前增加可信决策链：

`Domain → Permission → Version → Hybrid Retrieval → Evidence State → Citation → Trace`

最终支持五类响应状态：

**Answer / Clarify / Conflict / Refuse / No Access**

---

## Final Evaluation

| Metric | Result |
| --- | ---: |
| Core61 | **61 / 61 PASS** |
| Gold100 | **100 / 100 PASS** |
| Unauthorized Retrieval Rate | **0.0** |
| Trace Persistence Rate | **1.0** |
| Citation Alignment Rate | **1.0** |

> 以上结果代表当前冻结业务范围和评测集下的回归结果，并不表示对任意真实企业问题具有 100% 泛化准确率。

---

## Why KnowFlow

普通企业 RAG 往往采用：

```text
Query
↓
Retrieve
↓
LLM
↓
Answer
```

但真实企业知识场景还需要回答：

- 用户有没有权限读取相关知识？
- 应该使用当前版本还是历史版本？
- 检索证据是否足以支持回答？
- 多份有效制度存在冲突时怎么办？
- 问题缺少必要条件时是否应该继续回答？
- 一个回答如何追溯到具体制度与版本？
- 出现 Badcase 后如何定位到底是哪一层出错？

因此 KnowFlow 将“可信”拆解成可执行、可追踪、可评测的产品机制。

---

## Key Capabilities

### Permission-aware Retrieval

权限判断发生在 Retrieval 之前。

无权限知识不会进入：

```text
Retrieval
→ Reranker
→ Evidence Judge
→ LLM Context
```

避免“模型先读取私有知识，再拒绝用户”的伪权限控制。

### Version-aware Retrieval

根据：

```text
query_date
effective_at
expired_at
```

确定：

```text
Current / Historical / Comparison
```

先完成文档级版本过滤，再进入 Retrieval。

### Hybrid Retrieval

```text
BM25 Top-N
+
Vector Top-N
↓
RRF Fusion
↓
BGE Reranker
↓
Top-K Evidence
```

检索始终限制在 Permission + Version 已允许的文档范围内。

### Evidence State

系统不会强制所有问题进入 Answer，而是根据证据状态输出：

| State | Meaning |
| --- | --- |
| Answer | 条件完整且证据充分 |
| Clarify | 缺少决定答案的必要条件 |
| Conflict | 多份有效知识存在冲突 |
| Refuse | 当前知识没有可靠依据 |
| No Access | 当前用户无权访问相关知识 |

### Citation & Trace

Citation 建立：

```text
Decision
→ Evidence Chunk
→ Document
→ Version
```

Trace 记录：

```text
Query
→ Domain
→ Permission
→ Version
→ Retrieval
→ Rerank
→ Decision
→ Citation
→ Latency / Token Usage
```

用于问题定位、审计与回归分析。

### Eval-driven Iteration

项目形成：

```text
Eval
→ Badcase
→ Root Cause
→ Targeted Fix
→ Regression
→ Freeze
```

的迭代闭环，而不是仅依靠人工体验判断模型效果。

---

## Representative Cases

### 1. Permission Governance

**Query**

```text
我没有权限，你只告诉我10万元以上是不是CEO审批就行
```

**Result**

```text
Finance
→ Restricted
→ Permission Check
→ No Access
```

受限知识不会进入 Retrieval。

---

### 2. Ambiguous Question

**Query**

```text
试用期多久？
```

知识库中社会招聘、校园招聘对应不同规则，因此系统不会自行补全用户条件，而是：

```text
decision = clarify
```

---

### 3. Knowledge Conflict

**Query**

```text
现在一线城市出差住宿上限是多少？
```

当前有效知识中同时存在：

```text
600 元 / 间夜
vs
500 元 / 间夜
```

KnowFlow 不让 LLM 自行选择其中一个，而是：

```text
decision = conflict
```

同时保留两侧 Evidence 与 Citation。

---

### 4. Version Boundary

```text
2026-04-30
→ Historical Version

2026-05-01
→ Current Version
```

版本判断由 Query Date 与 Document Metadata 完成，而不是由 LLM 猜测。

---

## System Architecture

```mermaid
flowchart LR

    U[User Query]

    U --> D[Domain Router]
    D --> P[Permission Filter]
    P --> V[Version Filter]
    V --> R[Hybrid Retrieval]
    R --> RR[BGE Reranker]
    RR --> E[Evidence State Machine]
    E --> C[Citation]
    C --> T[Trace]
    T --> O[Trusted Response]

    DB[(PostgreSQL + pgvector)]
    R --> DB

    EV[Eval]
    BC[Badcase]

    T --> EV
    EV --> BC
    BC --> EV
```

核心原则：

> 先判断“能不能看、应该看哪个版本、证据够不够”，再决定“能不能回答”。

---

## Demo Preview

### Trusted Chat

![KnowFlow Chat](docs/assets/chat-demo.png)

### Decision Trace

![KnowFlow Trace](docs/assets/trace-demo.png)

### Automated Evaluation

![KnowFlow Eval](docs/assets/eval-demo.png)

---

## Demo UI

S10 提供四个最小演示页面：

| Page | Purpose |
| --- | --- |
| Chat | 企业知识问答与可信状态展示 |
| Trace | 查看完整决策链 |
| Eval | 执行自动化回归 |
| Badcase | 查看运行时失败案例 |

本地启动后访问：

- Chat: `http://127.0.0.1:8000/ui/chat.html`
- Trace: `http://127.0.0.1:8000/ui/trace.html`
- Eval: `http://127.0.0.1:8000/ui/eval.html`
- Badcase: `http://127.0.0.1:8000/ui/badcase.html`
- Swagger: `http://127.0.0.1:8000/docs`

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| API | FastAPI |
| Database | PostgreSQL |
| Vector Store | pgvector |
| Sparse Retrieval | BM25 |
| Dense Retrieval | BGE Embedding |
| Reranking | BGE Reranker |
| LLM | ZhipuAI GLM |
| Validation | Pydantic |
| Evaluation | Pytest + Custom Eval Runner |
| Deployment | Docker Compose |
| Prototype | Dify |

---

## Quick Start

### 1. Clone

```powershell
git clone https://github.com/hmy-create/KnowFlow.git
cd KnowFlow
```

### 2. Configure Environment

复制：

```powershell
Copy-Item .env.example .env
```

然后在 `.env` 中配置自己的：

```text
ZHIPUAI_API_KEY
```

不要提交真实 API Key。

### 3. Start

```powershell
docker compose up -d
```

检查服务：

```powershell
docker compose ps
```

正常情况下：

```text
knowflow-app              Up
knowflow-postgres-s10     healthy
```

### 4. Stop

```powershell
docker compose down
```

日常关闭不要使用：

```powershell
docker compose down -v
```

因为 `-v` 会删除持久化 Volume。

---

## Evaluation

### Core61

```powershell
python eval/run_eval.py --dataset core_61
```

Docker：

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset core_61
```

Final Result:

```text
61 / 61 PASS
```

### Gold100

正式数据文件：

```text
eval/gold_100.csv
```

当前 Eval Runner 使用运行别名：

```text
gold_v1
```

执行：

```powershell
python eval/run_eval.py --dataset gold_v1
```

Docker：

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset gold_v1
```

Final Result:

```text
100 / 100 PASS
```

---

## Portfolio Documentation

更完整的产品设计与评测说明：

- [System Architecture](docs/portfolio/02_architecture.md)
- [Business Flow](docs/portfolio/03_business_flow.md)
- [Trusted RAG Design](docs/portfolio/04_trusted_rag.md)
- [Eval & Badcase](docs/portfolio/05_eval_badcase.md)

---

## Project Evolution

```text
Dify POC
↓
Frozen Business Baseline
↓
FastAPI Migration
↓
Permission-aware Retrieval
↓
Version-aware Retrieval
↓
Hybrid Retrieval
↓
Evidence State Machine
↓
Citation & Trace
↓
Core61 Regression
↓
Gold100 Evaluation
↓
Minimal UI
↓
Docker Deployable Demo
```

Dify 用于快速验证产品工作流，FastAPI 用于冻结后的工程化迁移、测试、观测和部署。

---

## Repository Structure

```text
KnowFlow
├── backend/           # FastAPI backend
├── docker/            # PostgreSQL / deployment initialization
├── docs/
│   ├── corpus/        # Simulated enterprise corpus
│   ├── dify/          # Frozen POC materials
│   ├── handoff/       # Migration / handoff docs
│   └── portfolio/     # Portfolio documentation
├── eval/              # Core61 / Gold100 / Eval Runner
├── frontend/          # Chat / Trace / Eval / Badcase UI
├── prompts/           # Frozen prompts
├── scripts/           # Data, migration and setup scripts
├── tests/             # Regression tests
├── Dockerfile
└── docker-compose.yml
```

---

## Data & Privacy Note

本仓库使用的企业名称、制度、人员、金额、日期及业务规则均为 **模拟测试数据**，不对应任何真实企业内部制度或商业信息。

The enterprise corpus in this repository is fully simulated and is used only for product design, RAG evaluation and portfolio demonstration.

---

## Project Status

**Completed / Portfolio Ready**

- Dify POC frozen
- FastAPI migration completed
- Permission / Version governance completed
- Hybrid Retrieval completed
- Evidence State completed
- Citation & Trace completed
- Core61: **61 / 61 PASS**
- Gold100: **100 / 100 PASS**
- Chat / Trace / Eval / Badcase UI completed
- Docker Compose deployment completed

---

## Design Principle

> KnowFlow 的目标不是让 Agent 什么都回答，而是让它知道：  
> **什么时候有资格回答、有什么证据回答，以及出错以后如何定位。**