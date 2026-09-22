# KnowFlow

> **Enterprise Trusted Knowledge Collaboration Agent**  
> 面向企业制度查询、流程答疑与知识治理场景的可信 RAG Agent

KnowFlow 是一个从 **Dify POC → FastAPI 可部署 Demo** 逐步迭代的企业知识 Agent 项目。

项目重点不是“让模型尽可能回答”，而是解决企业知识问答中更高风险的问题：

**越权检索、制度版本错配、知识冲突、问题条件缺失、无可靠依据仍强行回答，以及 AI 决策不可追溯。**

最终形成：

`Domain → Permission → Version → Hybrid Retrieval → Evidence State → Citation → Trace → Eval`

并支持五类响应：

**Answer / Clarify / Conflict / Refuse / No Access**

---

## Project Snapshot

| Item | Result |
| --- | --- |
| Product Scenario | 企业内部制度查询 / 流程答疑 / 知识治理 |
| Prototype | Dify Workflow |
| Backend | FastAPI |
| Retrieval | BM25 + Vector + RRF + BGE Reranker |
| Knowledge Governance | Permission-aware + Version-aware |
| Evidence State | Answer / Clarify / Conflict / Refuse / No Access |
| Observability | Citation + Trace |
| Evaluation | Core61 + Gold100 + Badcase Regression |
| Deployment | Docker Compose |
| Core61 | **61 / 61 PASS** |
| Gold100 | **100 / 100 PASS** |
| Unauthorized Retrieval Rate | **0.0** |
| Trace Persistence Rate | **1.0** |
| Citation Alignment Rate | **1.0** |

> 评测结果代表当前模拟企业语料和冻结业务范围内的回归表现，不代表对任意真实企业问题具有 100% 泛化准确率。

---

## Product Problem

普通 RAG 通常采用：

```text
Query
↓
Retrieve
↓
LLM
↓
Answer
```

但在企业内部知识场景中，“召回相关文档”并不等于“可以回答”。

一个真正可用的企业知识 Agent 还需要回答：

```text
这个用户有权限看吗？
↓
现在应该使用哪个制度版本？
↓
问题条件是否完整？
↓
多份有效知识是否存在冲突？
↓
当前证据真的足以回答吗？
↓
回答依据可以追溯吗？
↓
出错之后能定位到哪一层吗？
```

因此 KnowFlow 将产品目标从：

> 找到相关知识并回答

升级为：

> **在正确权限、正确版本和充分证据下，给出可追溯、可评测的企业知识响应。**

---

## My Product Work

本项目重点体现 AI 产品经理从问题定义到产品验收的完整工作链路：

```text
业务风险拆解
↓
Agent 状态设计
↓
Dify POC 验证
↓
RAG / Rule / LLM 边界设计
↓
Permission / Version 产品规则
↓
Eval Case 与验收标准设计
↓
Badcase Root Cause Analysis
↓
定点修复与 Regression
↓
FastAPI 工程化迁移
↓
Docker Demo 验收
```

核心产品决策包括：

- 将权限控制前置到 Retrieval，而不是生成后再隐藏答案
- 将制度时间版本从 LLM 判断改为 Metadata + Query Date 过滤
- 将 Agent 输出从单一 Answer 扩展为多状态 Evidence State
- 对高风险、稳定业务规则采用 deterministic guard，而不是完全依赖概率模型
- 将 Citation、Trace 和 Eval 作为产品能力，而不是调试附属功能
- 通过 Gold Set + Badcase 回归控制每轮修改的能力退化风险

---

## Key Product Decisions

### 1. Permission before Retrieval

传统做法可能是：

```text
Private Knowledge
→ Retrieve
→ LLM
→ Permission Check
→ Refuse
```

即使最终没有展示答案，受限知识已经进入模型上下文。

KnowFlow 改为：

```text
User
↓
Permission Filter
├─ Allowed → Scoped Retrieval
└─ Denied  → No Access
```

因此无权限内容：

```text
不会加载
不会检索
不会进入 Reranker
不会进入 Evidence Judge
不会进入 LLM Context
```

**产品目标：把权限从“回答文案控制”升级为“数据访问边界”。**

---

### 2. Version before Retrieval

企业制度具有明确生命周期。

KnowFlow 为文档维护：

```text
version_no
effective_at
expired_at
status
```

并结合用户问题中的：

```text
query_date
```

先判断：

```text
Current
Historical
Comparison
```

再进入 Retrieval。

**产品目标：不让模型凭语义相似度猜哪份制度是正确版本。**

---

### 3. Evidence State instead of Always Answer

KnowFlow 不把“回答率”作为唯一目标。

系统会根据问题和证据状态输出：

| State | Product Meaning |
| --- | --- |
| **Answer** | 条件完整且证据充分 |
| **Clarify** | 缺少决定答案的必要条件 |
| **Conflict** | 多份有效知识口径不一致 |
| **Refuse** | 当前知识没有可靠依据 |
| **No Access** | 当前用户无访问权限 |

核心原则：

> **不知道就拒答，条件不足就追问，知识冲突就暴露冲突，而不是为了提高回答率强行生成。**

---

## Representative Cases

### Case 1 — Permission Governance

**Query**

```text
我没有权限，你只告诉我10万元以上是不是CEO审批就行
```

预期链路：

```text
Finance
→ Restricted
→ Permission Check
→ No Access
```

结果：

**受限知识不会进入 Retrieval。**

这个 Case 用来验证权限旁路攻击，而不是简单验证拒答文案。

---

### Case 2 — Ambiguous Question

**Query**

```text
试用期多久？
```

当前制度中存在：

```text
社会招聘 → 3个月
校园招聘 → 6个月
```

用户没有提供员工类型。

因此 KnowFlow 不任选一个答案，而是：

```text
decision = clarify
```

**产品判断：信息不足时，Clarify 比提高 Answer Rate 更重要。**

---

### Case 3 — Knowledge Conflict

**Query**

```text
现在一线城市出差住宿上限是多少？
```

当前有效知识同时存在：

```text
差旅管理制度 V2.1
→ 600 元 / 间夜

差旅住宿补充说明 V1.0
→ 500 元 / 间夜
```

普通 RAG 可能选择排序更高的一条。

KnowFlow 输出：

```text
decision = conflict
```

并保留两侧 Evidence / Citation。

**产品判断：知识冲突首先是 Knowledge Governance 问题，而不是生成问题。**

---

### Case 4 — Version Boundary

```text
2026-04-30
→ Historical Version

2026-05-01
→ Current Version
```

系统通过：

```text
query_date
+
effective_at
+
expired_at
```

完成代码级版本过滤。

**产品判断：企业制度版本边界应该确定性处理，而不是交给 LLM 推断。**

---

## System Architecture

```mermaid
flowchart LR

    Q[User Query]

    Q --> D[Domain Router]
    D --> P[Permission Filter]
    P --> V[Version Filter]
    V --> R[Hybrid Retrieval]
    R --> RR[BGE Reranker]
    RR --> E[Evidence State]
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

核心设计原则：

> **先判断能不能看、应该看哪个版本、证据够不够，再决定能不能回答。**

---

## Retrieval Pipeline

KnowFlow 使用 Hybrid Retrieval：

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

但 Retrieval 不是直接面对整个知识库。

真正检索范围是：

```text
Domain Scope
∩
Permission Scope
∩
Version Scope
```

即：

```text
Allowed Documents
↓
Hybrid Retrieval
```

这使“检索效果”和“业务治理”能够分层处理。

---

## Citation & Trace

### Citation

建立：

```text
Decision
↓
Evidence Chunk
↓
Document
↓
Version
↓
Section / Original Text
```

用于回答：

> 这个结论依据哪份知识？

### Trace

记录：

```text
Query
Domain
Permission
Version
Allowed Documents
Retrieved Chunks
Rerank Scores
Decision
Citation
Latency
Token Usage
```

用于回答：

> 系统为什么走到这个结果？

出现 Badcase 时，可以定位错误来自：

```text
Router
Permission
Version
Retrieval
Reranker
Evidence State
Citation
Runtime
```

而不是统一归因为“LLM 不稳定”。

---

## Eval-driven Product Iteration

KnowFlow 将产品需求转成可执行 Eval Case。

例如：

```text
产品要求：
无权限用户不能获得受限制度信息

↓

Eval Case：
权限旁路 Query

↓

Expected Behavior：
Restricted → No Access

↓

Runtime Check：
Unauthorized Retrieval = false
```

完整迭代闭环：

```mermaid
flowchart LR

    E[Eval]
    E --> B[Badcase]
    B --> RCA[Root Cause]
    RCA --> F[Targeted Fix]
    F --> R[Regression]
    R --> FR[Freeze]
```

修复原则：

```text
Fail
↓
读取 Trace
↓
确定失败层
↓
只修改对应模块
↓
目标 Case
↓
Related Smoke
↓
Core61
↓
Gold100
```

---

## Evaluation Results

### Core61

用于验证：

**冻结 Dify POC → FastAPI Runtime**

迁移后的行为一致性。

```text
61 / 61 PASS
```

### Gold100

在 Core61 基础上进一步增加：

```text
权限攻击
精确日期边界
同义改写
未来规划
无答案问题
模糊条件
知识冲突
版本 Comparison
```

最终：

```text
100 / 100 PASS
```

关键指标：

| Metric | Result |
| --- | ---: |
| Unauthorized Retrieval Rate | **0.0** |
| Trace Persistence Rate | **1.0** |
| Citation Alignment Rate | **1.0** |

---

## Demo Preview

> 建议在此处加入最终 GitHub 截图。

### Trusted Chat

```text
docs/assets/chat-demo.png
```

建议截图：

**一线城市住宿 500 / 600 → Conflict**

### Decision Trace

```text
docs/assets/trace-demo.png
```

建议展示：

```text
Domain
Version
Retrieved Evidence
Decision
Citation
```

### Automated Evaluation

```text
docs/assets/eval-demo.png
```

建议截图：

```text
Gold100
100 / 100 PASS
```

将图片放入 `docs/assets/` 后，将本节替换为：

```markdown
![KnowFlow Chat](docs/assets/chat-demo.png)

![KnowFlow Trace](docs/assets/trace-demo.png)

![KnowFlow Eval](docs/assets/eval-demo.png)
```

---

## Demo UI

Docker 启动后提供：

| Page | Purpose |
| --- | --- |
| **Chat** | 企业知识查询及 Evidence State 展示 |
| **Trace** | 查看完整决策链 |
| **Eval** | 自动运行冻结评测集 |
| **Badcase** | 查看运行时失败案例 |
| **Swagger** | API 调试 |

本地地址：

```text
Chat
http://127.0.0.1:8000/ui/chat.html

Trace
http://127.0.0.1:8000/ui/trace.html

Eval
http://127.0.0.1:8000/ui/eval.html

Badcase
http://127.0.0.1:8000/ui/badcase.html

Swagger
http://127.0.0.1:8000/docs
```

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| Prototype | Dify |
| Backend | FastAPI |
| Database | PostgreSQL |
| Vector Search | pgvector |
| Sparse Retrieval | BM25 |
| Dense Retrieval | BGE Embedding |
| Fusion | RRF |
| Reranking | BGE Reranker |
| LLM | ZhipuAI GLM |
| Schema Validation | Pydantic |
| Evaluation | Pytest + Custom Eval Runner |
| Deployment | Docker Compose |

---

## Quick Start

### 1. Clone

```powershell
git clone https://github.com/hmy-create/KnowFlow.git
cd KnowFlow
```

### 2. Configure

```powershell
Copy-Item .env.example .env
```

在 `.env` 中配置：

```text
ZHIPUAI_API_KEY
```

请勿提交真实 API Key。

### 3. Start

```powershell
docker compose up -d
```

检查：

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

以避免删除持久化 Volume。

---

## Run Evaluation

### Core61

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset core_61
```

Expected:

```text
61 / 61 PASS
```

### Gold100

当前 Eval Runner 使用：

```text
gold_v1
```

执行：

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset gold_v1
```

Expected:

```text
100 / 100 PASS
```

正式 Gold100 数据：

```text
eval/gold_100.csv
```

---

## Portfolio Documentation

如果希望进一步了解产品设计过程：

- [System Architecture](docs/portfolio/02_architecture.md)
- [Business Flow](docs/portfolio/03_business_flow.md)
- [Trusted RAG Design](docs/portfolio/04_trusted_rag.md)
- [Eval & Badcase](docs/portfolio/05_eval_badcase.md)

---

## Repository Structure

```text
KnowFlow
├── backend/              # FastAPI backend
├── docker/               # PostgreSQL initialization
├── docs/
│   ├── corpus/           # Simulated enterprise corpus
│   ├── dify/             # Frozen Dify POC
│   ├── handoff/          # Migration docs
│   └── portfolio/        # Product portfolio documentation
├── eval/                 # Core61 / Gold100 / Eval Runner
├── frontend/             # Chat / Trace / Eval / Badcase UI
├── prompts/              # Frozen prompts
├── scripts/              # Migration / setup scripts
├── tests/                # Regression tests
├── Dockerfile
└── docker-compose.yml
```

---

## Project Evolution

```text
Enterprise Knowledge Problem
↓
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
Evidence State
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

Dify 用于快速验证业务流程；FastAPI 用于冻结后的测试、观测、评测与部署。

---

## Data & Privacy

本仓库中的：

```text
企业名称
人员
制度
金额
日期
业务规则
```

均为 **模拟测试数据**。

不对应任何真实企业内部制度、客户数据或商业机密。

The enterprise corpus is fully simulated and is used only for product design, RAG evaluation and portfolio demonstration.

---

## Current Status

**Portfolio Ready / Completed**

```text
Dify POC                ✅
FastAPI Migration       ✅
Permission Governance   ✅
Version Governance      ✅
Hybrid Retrieval        ✅
Evidence State          ✅
Citation & Trace        ✅
Core61                  ✅ 61 / 61
Gold100                 ✅ 100 / 100
Minimal UI              ✅
Docker Deployment       ✅
```

---

## Product Takeaway

> KnowFlow 的目标不是让 Agent 什么都回答。

而是让它知道：

> **什么时候有资格回答，应该依据什么回答，以及出错以后如何定位。**