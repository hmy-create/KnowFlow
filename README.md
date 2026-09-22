# KnowFlow

KnowFlow 企业可信知识协作 Agent

## Current Stage

Dify POC Frozen → FastAPI Deployable Demo

当前 Dify POC 已冻结，本仓库用于将已经验证的业务决策链迁移为可测试、可观测、可部署的 FastAPI 服务。

## Frozen Baseline

当前冻结版包含：

- Domain Router
  - HR
  - Finance
  - Product
  - Service
  - Other
- Finance Sensitivity
  - Normal
  - Restricted
- Version-aware logic
- Permission-aware logic
- Evidence Judge
- Core Eval Dataset
- P-FIX regression cases
- V102 query-date regression cases

## Current Development Stage

S0 - Repository & Baseline

Next:

S1 - FastAPI Minimal Skeleton

## Important

Do not modify the frozen Dify POC logic directly.

All FastAPI implementations must be validated against the frozen baseline.

---

## S10 Deployable Demo

KnowFlow 已完成从冻结 Dify POC 到可部署 FastAPI Demo 的迁移。

当前 S10 仅增加最小可演示界面与 Docker 部署能力，不重新设计已经冻结的 POC 业务逻辑。

### Demo Pages

Docker 启动后，可通过以下页面访问：

- Chat: http://127.0.0.1:8000/ui/chat.html
- Trace: http://127.0.0.1:8000/ui/trace.html
- Eval: http://127.0.0.1:8000/ui/eval.html
- Badcase: http://127.0.0.1:8000/ui/badcase.html
- Swagger: http://127.0.0.1:8000/docs

### Start

在项目根目录执行：

```powershell
docker compose up -d
```

查看服务状态：

```powershell
docker compose ps
```

正常情况下应看到：

- `knowflow-app` 为 Up
- `knowflow-postgres-s10` 为 healthy

### Stop

正常关闭：

```powershell
docker compose down
```

日常关闭不要使用：

```powershell
docker compose down -v
```

因为 `-v` 会删除 PostgreSQL、HuggingFace Cache 和运行时 Badcase 等持久化 Volume。

### Evaluation

S9/S10 最终冻结回归结果：

- Core61: 61 / 61 PASS
- Gold100: 100 / 100 PASS
- Unauthorized Retrieval Rate: 0.0
- Trace Persistence Rate: 1.0
- Citation Alignment Rate: 1.0

正式 Gold100 数据文件：

`eval/gold_100.csv`

当前 Eval Runner 的运行名称为：

`gold_v1`

因此运行最终 Gold100 使用：

```powershell
python eval/run_eval.py --dataset gold_v1
```

Docker 内运行：

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset gold_v1
```

Core61 Docker 回归：

```powershell
docker compose exec app python /app/eval/run_eval.py --dataset core_61
```

### S10 Architecture

当前 Demo 链路：

```text
Browser
  ↓
FastAPI
  ↓
Router
  ↓
Permission Filter
  ↓
Version Filter
  ↓
Hybrid Retrieval
  ↓
Evidence State Machine
  ↓
Citation / Trace
```

S10 Minimal UI 包含：

- Chat
- Trace
- Eval
- Badcase

S10 不修改冻结 POC 的核心判定逻辑。