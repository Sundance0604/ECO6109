"""Selectively copy research sources; never modify source directories.

python tools/curate_sources.py --yinhe PATH --me PATH
"""
import argparse
import ast
import copy
import csv
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--yinhe', type=Path, required=True)
    ap.add_argument('--me', type=Path, required=True)
    args = ap.parse_args()
    records = []

    def record(src, dst, action, reason):
        records.append(dict(source=str(src.resolve()), destination=dst.relative_to(ROOT).as_posix(),
                            action=action, reason=reason, bytes=dst.stat().st_size,
                            source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                            destination_sha256=hashlib.sha256(dst.read_bytes()).hexdigest()))

    def retain(src, target, reason):
        dst = ROOT / target
        dst.parent.mkdir(parents=True, exist_ok=True)
        if dst.exists() and dst.read_bytes() != src.read_bytes():
            raise FileExistsError(f'Refusing to replace changed file: {dst}')
        shutil.copy2(src, dst)
        record(src, dst, 'byte-identical copy', reason)

    for name in ['因子库_09.xlsx', '因子库_10.xlsx', 'factor_09.xlsx', 'sig_二级5yYTM_ada.xlsx']:
        retain(args.yinhe / name, f'data/original/formal/{name}', 'Formal Tier 2 research input or historical signal')
    retain(args.me / 'yinhe/固收量化报告-机器学习.docx',
           'docs/references/固收量化报告-机器学习.docx', 'Historical formal report; not a course submission')
    for name in ['machine_learning.ipynb', 'model_comparable.ipynb', 'model_comparable (1).ipynb']:
        retain(args.yinhe / name, f'legacy/formal/{name}', 'Tier 2 classical ML and sequence-model experiments')
    ag = args.yinhe / 'daily_factor'
    retain(ag / 'merged_tier2.xlsx', 'data/original/autogluon/merged_tier2.xlsx',
           'Tier 2 merged candidate table; keep all explanatory factors')
    for name in ['data.py', 'factor.py', 'new_factor.py', 'autoGluonTrain.py', 'update_output.py', '训练示例.ipynb']:
        retain(ag / name, f'legacy/autogluon/{name}', 'Shared dependencies for Tier 2; multi-target configuration remains historical')
    for name in ['二级资本债七年.xlsx', '资本债五年.xlsx', '资本债五年_extreme.xlsx']:
        retain(ag / 'feature_importance' / name, f'results/legacy/autogluon/{name}', 'Tier 2 feature importance export')
    for src in (ag / 'data').glob('*.xlsx'):
        retain(src, f'data/original/autogluon/market_inputs/{src.name}', 'Shared market explanatory input for Tier 2 factor construction')
    for src in (ag / 'factor').glob('*_20251029.xlsx'):
        retain(src, f'data/original/autogluon/factor_snapshot/{src.name}', 'One latest shared snapshot; not claimed to exactly regenerate older merged data')
    for src in (ag / 'factor').glob('20251029-因子清单.xlsx'):
        retain(src, f'data/original/autogluon/factor_snapshot/{src.name}', 'Factor dictionary for retained snapshot')
    for src in (args.yinhe / 'factor_data').glob('*.xlsx'):
        if src.name not in ['因子库.xlsx', '全因子.xlsx']:
            retain(src, f'data/original/autogluon/curve_inputs/{src.name}', 'Curve and relative-value explanatory input')
    for directory in ['reports', 'reports_gru_split', 'reports_tcn_split']:
        for src in (args.yinhe / directory).glob('*'):
            if src.is_file():
                retain(src, f'results/legacy/formal/{directory}/{src.name}', 'Saved Tier 2 result; not independently reproduced')
    for name in ['lstm_results_three_combo_no_leak_with_lags.xlsx', 'lstm_results_three_combo_no_leak.xlsx',
                 'lstm_best_param_results.xlsx', 'lstm_best_param_results_prelabel.xlsx',
                 'lstm_results_batch_train_then_predict.xlsx', 'lstm_results_use_existing_value_sort_no_leak.xlsx',
                 'lstm_results_use_existing_value_sort.xlsx', 'gru_results_best_8_2.xlsx', 'New_LSTM_results.xlsx',
                 'stacking_predictions.xlsx', 'stack_test_results.xlsx', 'test_predictions_xgb.xlsx',
                 'test_predictions-XGB.xlsx', 'test_predictions.xlsx']:
        retain(args.yinhe / name, f'results/legacy/formal/other_exports/{name}', 'Tier 2 notebook export; filename does not prove leakage-free design')
    src = ag / 'basis_ml.ipynb'
    nb = json.loads(src.read_text(encoding='utf-8'))
    indices = [6, 29, 30, 31, 32, 33, 34, 35, 36, 38, 39, 40, 75, 76]
    cells = [dict(cell_type='markdown', metadata={}, source=[
        '# AutoGluon 二级资本债历史摘录\n',
        '只保留二级资本债单元及共享合并函数。各段标签不同，不可依次执行作为统一实验。\n'])]
    for i in indices:
        cells.append(dict(cell_type='markdown', metadata={}, source=[f'原始 basis_ml.ipynb 单元索引 {i}（从 0 开始）']))
        cells.append(copy.deepcopy(nb['cells'][i]))
    dst = ROOT / 'legacy/autogluon/tier2_excerpts.ipynb'
    out = dict(nbformat=4, nbformat_minor=5, metadata=nb.get('metadata', {}), cells=cells)
    dst.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding='utf-8')
    record(src, dst, 'selected cells with saved outputs', f'Original zero-based indices: {indices}')
    # Extract only the reusable yield-signal backtest, excluding perpetual-specific runs.
    src = args.yinhe / 'data_train_backtest.py'
    code = src.read_text(encoding='utf-8')
    tree = ast.parse(code)
    cls = next(node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == 'DataTrain')
    methods = [node for node in cls.body if isinstance(node, ast.FunctionDef) and
               node.name in ['make_dirs', 'tradesignal', 'trade1', 'trade2', 'performance', 'backtest']]
    header = ('"""Historical yield backtest excerpt; not verified to reproduce the report.\n'
              'Source: data_train_backtest.py, DataTrain methods only.\n'
              'No Wind connection or perpetual-bond batch execution is included.\n"""\n'
              'import os\nimport math\nimport numpy as np\nimport pandas as pd\n'
              'import matplotlib.pyplot as plt\nimport matplotlib.ticker as ticker\n\n'
              'class LegacyYieldBacktest:\n')
    lines = code.splitlines(keepends=True)
    pieces = [''.join(lines[node.lineno - 1:node.end_lineno]) for node in methods]
    dst = ROOT / 'legacy/formal/yield_backtest_excerpt.py'
    dst.write_text(header + '\n\n'.join(pieces) + '\n', encoding='utf-8')
    record(src, dst, 'selected class methods', 'Reusable signal/duration/carry backtest; excludes other targets and Wind initialization')
    src = args.me / '银河三项量化策略_详细技术说明与面试答法.md'
    content = src.read_text(encoding='utf-8')
    selected = content[content.index('# 二、'):content.index('## 3.1')]
    if '# 三、' in selected:
        selected = selected[:selected.index('# 三、')]
    dst = ROOT / 'docs/references/二级资本债_既有技术说明摘录.md'
    dst.write_text('> 既有整理材料摘录；版本核对见 ../RESEARCH.md。\n\n' + selected.rstrip() + '\n', encoding='utf-8')
    record(src, dst, 'Tier 2 section excerpt', 'Exclude unrelated strategies and personal materials')
    with (ROOT / 'data/SOURCE_MANIFEST.csv').open('w', encoding='utf-8-sig', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)
    print(json.dumps(dict(imported_files=len(records), imported_mb=round(sum(r['bytes'] for r in records)/1e6, 2))))


if __name__ == '__main__':
    main()
