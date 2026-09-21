# KnowFlow Evaluation Datasets

## core_61.csv

S9 冻结核心回归集。

- 61 cases
- Core61 baseline
- 冻结后不再修改
- Final result: 61/61 PASS

## gold_39.csv

S9-10 在 Core61 基础上新增的扩展 Gold Case。

- 39 cases
- 覆盖 paraphrase、version boundary、permission attack、
  clarify、refuse、conflict 等冻结能力边界

## gold_100.csv

KnowFlow S9 最终正式 Gold Dataset。

- Core61 + Gold39
- 100 cases
- 这是规范数据文件（canonical dataset）

## gold_v1.csv

`gold_100.csv` 的运行时别名。

当前 `eval/run_eval.py` 的 CLI 注册名称为：

- `core_61`
- `gold_v1`

因此最终 100 条测试通过：

```powershell
python eval/run_eval.py --dataset gold_v1