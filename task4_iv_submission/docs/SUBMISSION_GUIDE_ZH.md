# Task 4 文件说明与运行方法

## 1. 文件结构

- `cfm_id/iv_types.py`：潜在响应类型的枚举。
- `cfm_id/iv_contract.py`：观测条件概率表的输入检查。
- `cfm_id/iv_late_solver.py`：LATE 的 Wald 计算及停止条件。
- `cfm_id/iv_ate_solver.py`：基于潜在响应类型的 ATE 上下界求解。
- `cfm_id/iv_ate_verify.py`：检查 ATE 端点及 primal-dual 证书。
- `cfm_id/__init__.py`：模块对外接口。
- `examples/iv_demo.py`：使用合成总体分布运行 LATE 和 ATE 示例。
- `tests/test_iv_task4.py`：检查类型数量、LATE 停止规则、ATE 界限、证书和非法输入。
- `docs/IV_MATH_ZH.md`：模型定义和推导。
- `docs/DELIVERY_CHECKLIST_ZH.md`：本次实现范围及尚未完成的工作。

## 2. 运行步骤

建议使用 Python 3.11 或更高版本。在项目目录中创建并激活虚拟环境：

```bash
python -m venv .venv
```

Windows PowerShell：

```powershell
.venv\\Scripts\\Activate.ps1
```

macOS/Linux：

```bash
source .venv/bin/activate
```

安装项目及开发依赖：

```bash
python -m pip install -e ".[dev]"
```

运行测试：

```bash
python -m pytest -q
```

运行示例：

```bash
python -m examples.iv_demo
```

## 3. 输入格式

求解函数接收一个字典，键为 `(z,d,y)`，值为 `P(D=d,Y=y | Z=z)`。八种组合都需要提供；每个 `z` 对应的四个概率之和应为 1。示例使用的是人为构造的总体分布，不是从真实数据估计出的结果。

## 4. 当前实现范围

本目录是独立的 Task 4 实现。它没有修改或替换主仓库中的现有模块，也没有完成主仓库的业务读取、统一 contract、gateway 或 CI 集成。若要合并进主仓库，需要先核对现有接口，再调整导入路径、输入输出结构和测试配置。

`assumptions_accepted=True` 表示调用方已在外部审核相关识别假设；程序本身不能证明工具变量独立性、排除限制或单调性。提交时应如实说明这一点。
