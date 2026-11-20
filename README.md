# ECO6109 二级资本债量化研究

研究问题：已知当天收盘后的信息，能否预测下一交易日银行二级资本债 5 年期收益率方向？机器学习能否稳定超过多数类和方向延续基准？

这里整理了原实习项目的两条研究路径：**AutoGluon 二级资本债研究**，以及**153 个候选特征的正式模型比较研究**。共筛选导入 83 个文件，来源材料约 34.5 MB，另附协作说明和运行结果。原目录不作修改。课程项目应在这些材料上重新验证，写出小组自己的方法、结果和局限。

## 先读这些文件

**第一次接触项目、不会使用 GitHub 或 Wind 的组员，请先读 [项目说明与 Wind 数据提取指南](项目说明_组员必读.md)。** 其中包含直接下载 ZIP 的方法、数据内容、Wind 指标代码和提取示例。

1. [课程要求与时间表](docs/COURSE_REQUIREMENTS.md)：对照原始 `Guidance on Project.docx`。
2. [研究路径与已知问题](docs/RESEARCH.md)：两套样本、标签差异、历史结果的使用边界。
3. [协作约定与任务表](docs/COLLABORATION.md)：分工、文件规则、提交检查。
4. [一页英文 Proposal Word 版](deliverables/ECO6109_Project_Proposal.docx)及 [Markdown 正文](deliverables/proposal.md)：用于 2026 年 11 月 20 日的 proposal 提交。
5. [数据目录说明](data/README.md)与 [来源清单](data/SOURCE_MANIFEST.csv)：定位输入、版本和 SHA256。
6. [Word 研究报告](docs/references/固收量化报告-机器学习.docx)：实习时期报告原件，作为历史研究参考；课程原始要求见 [Guidance on Project.docx](Guidance%20on%20Project.docx)。

## 获取与同步

小组仓库：[Sundance0604/ECO6109](https://github.com/Sundance0604/ECO6109)。本目录对应仓库根目录，Word 报告、筛选后的原始数据和研究代码一并纳入版本管理。

```powershell
git clone git@github.com:Sundance0604/ECO6109.git
cd ECO6109
```

已有克隆先 `git pull --ff-only` 再开始修改；多人协作建议使用各自分支和 Pull Request。

## 目录

```text
configs/project.json       样本日期、目标字段、输入文件
data/original/formal/      因子库 09、10，旧处理表与二级债信号
data/original/autogluon/   二级债合并表及共享市场、曲线、因子快照
data/processed/            由脚本生成，不手工编辑
scripts/                  新增的离线准备、基准与可选训练入口
legacy/formal/            原始树模型、集成与时序模型 notebook
legacy/autogluon/         原始依赖、二级债单元摘录及旧训练示例
results/legacy/           实习时期保存的结果，未经统一重跑
results/baseline/         本次实际运行的简单基准与独立复核
docs/references/          原研究报告及既有二级债技术说明摘录
deliverables/             课程 proposal、报告和展示的协作草稿
tools/curate_sources.py   一次性筛选导入工具，正常研究无需运行
```

## 组员如何开始

在此目录打开终端，推荐 Python 3.11。以下步骤只使用本地数据，不需要 Wind、iFind 或实习机器路径。

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts/run_baselines.py
.\.venv\Scripts\python.exe scripts/verify_results.py
```

结果在 `results/baseline/`。第一条脚本会自动准备正式研究数据，输出多数类和方向延续基准，不会重跑旧 notebook。可选逻辑回归：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-ml.txt
.\.venv\Scripts\python.exe scripts/run_baselines.py --logistic
.\.venv\Scripts\python.exe scripts/verify_results.py
```

AutoGluon 独立环境与新入口：

```powershell
python -m venv .venv-ag
.\.venv-ag\Scripts\python.exe -m pip install -r requirements-autogluon.txt
.\.venv-ag\Scripts\python.exe scripts/train_autogluon.py --track formal --time-limit 300
```

`--track formal` 使用同一正式样本便于比较；`--track autogluon` 使用原 AutoGluon 二级债表及其自身时间划分。新入口先用 5 个目标历史特征、顺序验证集、不启用随机折叠和 stacking。原全因子研究材料完整另存，扩展特征前先审查可得时点和前视因子。

## 本次验证范围

已运行两条路径的数据准备、正式样本的简单基准和标准库独立复核；导入文件均记录哈希。完整结果与实际运行环境见 `results/baseline/`。当前工具环境没有 scikit-learn、AutoGluon，逻辑回归与 AutoGluon 新入口仅完成语法检查，未声称重现历史模型成绩。旧 notebook 保存了多轮试验，不能直接 Run All 得出一套统一结果。

没有复制黄金、独立期货择时、基差策略、永续债专用模型、大型模型缓存、压缩包、简历、日报和临时文件。共享的国债期货、权益、永续债等**解释变量**仍保留，因为二级资本债研究需要它们。
