"""Create a portable, auditable Tier 2 dataset; does not call Wind or iFind."""
import argparse
import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def build(track='formal'):
    cfg = json.loads((ROOT / 'configs/project.json').read_text(encoding='utf-8'))
    source = ROOT / cfg[f'{track}_input']
    target = cfg[f'{track}_target']
    raw = pd.read_excel(source)
    raw['date'] = pd.to_datetime(raw['date'], errors='raise')
    if raw['date'].duplicated().any():
        raise ValueError('Duplicate dates must be reconciled before preparing data')
    raw = raw.sort_values('date').set_index('date')
    numeric = raw.apply(pd.to_numeric, errors='coerce').replace([np.inf, -np.inf], np.nan)
    # Preserve observed yield levels. Do not impute labels or treat holidays as observations.
    observed = numeric.loc[numeric[target].notna()].copy()
    ytm = observed[target]
    dates = pd.Series(observed.index, index=observed.index)
    next_change = ytm.shift(-1) - ytm
    result = pd.DataFrame(index=observed.index)
    result['target_date'] = dates.shift(-1)
    result['yield_pct'] = ytm
    result['next_yield_change_pctpoint'] = next_change
    result['label'] = (next_change <= 0).astype(int)
    result['yield_change_1d'] = ytm.diff()
    result['yield_change_5d'] = ytm.diff(5)
    result['yield_ma5_gap'] = ytm - ytm.rolling(5).mean()
    result['yield_vol20'] = ytm.diff().rolling(20).std()
    result['persistence_prediction'] = (ytm.diff() <= 0).astype(int)
    result = result.loc[next_change.notna() & ytm.diff().notna()]
    if track == 'formal':
        result = result.loc[(result.index >= cfg['start']) & (result.index <= cfg['test_end'])]
        val_start, test_start = pd.Timestamp(cfg['validation_start']), pd.Timestamp(cfg['test_start'])
    else:
        # A separate exploratory window: do not compare its score to the formal track directly.
        val_start = result.index[int(len(result) * .64)]
        test_start = result.index[int(len(result) * .8)]
    result['split'] = 'test'
    result.loc[result.index < test_start, 'split'] = 'validation'
    result.loc[result.index < val_start, 'split'] = 'train'
    # Purge observations whose outcome would only be learned in the following partition.
    purge = ((result['split'] == 'train') & (result['target_date'] >= val_start)) | (
        (result['split'] == 'validation') & (result['target_date'] >= test_start))
    result.loc[purge, 'split'] = 'purged'
    if track == 'formal':
        # A small interpretable feature set; keep candidate library unchanged on disk.
        for col in ['国债5yYTM', '国开5yYTM', '二级3yYTM', 'DR007', 'R007', 'Repo5Y', 'Repo1Y']:
            result[f'{col}_change1d'] = observed[col].diff().reindex(result.index)
        result['tier2_cdb_spread'] = ytm - observed['国开5yYTM']
        result['tier2_curve_5y3y'] = ytm - observed['二级3yYTM']
    folder = ROOT / 'data/processed' / track
    folder.mkdir(parents=True, exist_ok=True)
    result.index.name = 'date'
    result.to_csv(folder / 'dataset.csv', encoding='utf-8-sig')
    dictionary = pd.DataFrame({'field': numeric.columns, 'nonmissing': numeric.notna().sum().values,
                               'missing_fraction': numeric.isna().mean().values})
    dictionary.to_csv(folder / 'source_columns.csv', index=False, encoding='utf-8-sig')
    summary = dict(track=track, source=source.relative_to(ROOT).as_posix(), raw_rows=len(raw), raw_feature_columns=len(raw.columns),
                   observed_target_rows=len(observed), observed_start=str(observed.index.min().date()),
                   observed_end=str(observed.index.max().date()), target=target,
                   weekend_target_observations=int((observed.index.dayofweek >= 5).sum()),
                   positive_class='next observed yield is lower or unchanged',
                   partitions={}, purged_rows=int(purge.sum()))
    for split in ['train', 'validation', 'test']:
        part = result.loc[result['split'] == split]
        summary['partitions'][split] = dict(n=len(part), start=str(part.index.min().date()),
                                            end=str(part.index.max().date()), positive_rate=float(part['label'].mean()))
    (folder / 'summary.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return result


if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--track', choices=['formal', 'autogluon'], default='formal')
    build(ap.parse_args().track)
