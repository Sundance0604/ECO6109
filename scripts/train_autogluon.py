"""Optional, conservative AutoGluon starter; not a replay of historical best results."""
import argparse
import importlib.metadata
import json
from datetime import datetime

from prepare_data import ROOT, build


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--track', choices=['formal', 'autogluon'], default='formal')
    ap.add_argument('--time-limit', type=int, default=300)
    args = ap.parse_args()
    try:
        from autogluon.tabular import TabularPredictor
    except ImportError as exc:
        raise SystemExit('Install requirements-autogluon.txt in a separate virtual environment first.') from exc
    df = build(args.track)
    # Only use explicitly constructed historical target features. The wide candidate
    # library needs an availability/leakage audit before it becomes model input.
    features = ['yield_pct', 'yield_change_1d', 'yield_change_5d', 'yield_ma5_gap', 'yield_vol20']
    cols = features + ['label']
    train = df.loc[df['split'] == 'train', cols].reset_index(drop=True)
    validation = df.loc[df['split'] == 'validation', cols].reset_index(drop=True)
    test = df.loc[df['split'] == 'test']
    run_id = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    out = ROOT / 'results/autogluon' / args.track / run_id
    out.mkdir(parents=True, exist_ok=False)
    predictor = TabularPredictor(label='label', problem_type='binary', eval_metric='accuracy',
                                 path=str(out / 'model')).fit(
        train_data=train, tuning_data=validation, time_limit=args.time_limit,
        hyperparameters={'GBM': {}}, num_bag_folds=0, num_stack_levels=0,
        dynamic_stacking=False, fit_weighted_ensemble=False, calibrate_decision_threshold=False)
    result = test[['target_date', 'yield_pct', 'label']].copy()
    result['prediction'] = predictor.predict(test[features]).to_numpy()
    result['probability_down_or_flat'] = predictor.predict_proba(test[features])[1].to_numpy()
    result.to_csv(out / 'test_predictions.csv', encoding='utf-8-sig')
    predictor.leaderboard(test[cols], silent=True).to_csv(out / 'leaderboard.csv', index=False)
    (out / 'run.json').write_text(json.dumps(dict(
        track=args.track, features=features, label='1 = lower or unchanged next observed yield',
        time_limit=args.time_limit, autogluon_version=importlib.metadata.version('autogluon.tabular'),
        role='New conservative starter; not historical all-factor reproduction'), indent=2), encoding='utf-8')
    print(out)


if __name__ == '__main__':
    main()
