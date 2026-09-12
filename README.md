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