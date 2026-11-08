# Task 4：二元工具变量（IV）识别

本目录包含第二次任务中二元工具变量识别部分的独立实现。模型中，工具变量 `Z`、实际处理 `D` 和结果 `Y` 均为二元变量，并假设个体之间不存在干扰。

## 内容

- `cfm_id/iv_types.py`：枚举潜在响应类型；不施加单调性时有 16 类，施加 `D(1) >= D(0)` 后有 12 类。
- `cfm_id/iv_contract.py`：检查输入的八个条件概率单元。
- `cfm_id/iv_late_solver.py`：在假设已获审核接受且第一阶段满足要求时，按 Wald 公式计算 LATE。
- `cfm_id/iv_ate_solver.py`：通过潜在响应类型线性规划计算 ATE 的上下界。
- `cfm_id/iv_ate_verify.py`：检查上下界对应的原始问题与对偶证书。
- `examples/iv_demo.py`：合成数据示例。
- `tests/test_iv_task4.py`：自动测试。
- `docs/`：模型推导、文件说明和交付范围。

## 安装与运行

需要 Python 3.11 或更高版本。在本目录下执行：

```bash
python -m venv .venv
```

Windows PowerShell 激活环境：

```powershell
.venv\\Scripts\\Activate.ps1
```

macOS 或 Linux 激活环境：

```bash
source .venv/bin/activate
```

安装依赖并运行测试和示例：

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m examples.iv_demo
```

## 输入约定

求解器接收映射 `{(z, d, y): probability}`，包含 `z,d,y` 的全部八种组合。每个 `Z` 组内四个条件概率之和应为 1。输入表示总体条件分布 `P(D=d,Y=y | Z=z)`，不是未经处理的原始样本频数。

## 识别假设与适用范围

代码不会根据观测分布证明工具变量独立性、排除限制、一致性、无干扰或单调性。LATE 函数中的 `assumptions_accepted=True` 是调用方提供的审核确认，不是统计检验结论。

本实现分别处理遵从者局部平均处理效应（LATE）和全体平均处理效应（ATE）。LATE 使用 Wald 比值；ATE 返回潜在响应类型模型下的线性规划界限。二者是不同的目标量，不应混为一谈。

当前交付包可独立运行，但尚未接入 CFM 主仓库的业务读取、统一 contract、证书接口或 gateway。合并前需要对照主仓库当前实现完成接口适配，并在项目环境中运行集成测试。本包也不实现 2SLS、弱工具变量推断、有限样本置信区间或网络 IV 模型。
