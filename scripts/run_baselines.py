"""Reproduce transparent classification benchmarks; optional logistic regression."""
import argparse
import importlib.metadata
import json
import platform
from pathlib import Path

import numpy as np
import pandas as pd

from prepare_data import ROOT, build


def metrics(y, pred):
    y, pred = np.asarray(y), np.asarray(pred)
    tp = int(((y == 1) & (pred == 1)).sum())
    fp = int(((y == 0) & (pred == 1)).sum())
    fn = int(((y == 1) & (pred == 0)).sum())
    tn = int(((y == 0) & (pred == 0)).sum())
    return dict(n=len(y), accuracy=float((y == pred).mean()),
                precision=tp / (tp + fp) if tp + fp else 0,
                recall=tp / (tp + fn) if tp + fn else 0,
                f1=2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0,
                tp=tp, fp=fp, fn=fn, tn=tn)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--logistic', action='store_true', help='Requires scikit-learn; fixed settings, no test tuning')
    args = ap.parse_args()
    df = build('formal')
    train, test = df.loc[df['split'] == 'train'], df.loc[df['split'] == 'test']
    majority = int(train['label'].mean() >= .5)
    predictions = test[['target_date', 'yield_pct', 'next_yield_change_pctpoint', 'label']].copy()
    predictions['majority'] = majority
    predictions['persistence'] = test['persistence_prediction'].astype(int)
    models = ['majority', 'persistence']
    if args.logistic:
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
        columns = ['yield_change_1d', 'yield_change_5d', 'yield_ma5_gap', 'yield_vol20',
                   '国债5yYTM_change1d', '国开5yYTM_change1d', 'DR007_change1d',
                   'tier2_cdb_spread', 'tier2_curve_5y3y']
        model = make_pipeline(SimpleImputer(strategy='median'), StandardScaler(),
                              LogisticRegression(C=1., max_iter=2000, random_state=6109))
        model.fit(train[columns], train['label'])
        predictions['logistic'] = model.predict(test[columns])
        models.append('logistic')
    out = ROOT / 'results/baseline'
    out.mkdir(parents=True, exist_ok=True)
    predictions.to_csv(out / 'test_predictions.csv', encoding='utf-8-sig')
    scores = {name: metrics(test['label'], predictions[name]) for name in models}
    (out / 'metrics.json').write_text(json.dumps(scores, indent=2), encoding='utf-8')
    versions = {p: importlib.metadata.version(p) for p in ['numpy', 'pandas', 'openpyxl']}
    (out / 'environment.json').write_text(json.dumps(dict(python=platform.python_version(), packages=versions,
        logistic_executed=args.logistic), indent=2), encoding='utf-8')
    print(json.dumps(scores, indent=2))


if __name__ == '__main__':
    main()
