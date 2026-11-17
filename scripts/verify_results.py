"""Independent standard-library check; does not call model metrics or pandas."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    with (ROOT / 'data/SOURCE_MANIFEST.csv').open(encoding='utf-8-sig', newline='') as f:
        manifest = list(csv.DictReader(f))
    for record in manifest:
        path = ROOT / record['destination']
        assert hashlib.sha256(path.read_bytes()).hexdigest() == record['destination_sha256'], path
        if record['action'] == 'byte-identical copy':
            assert record['source_sha256'] == record['destination_sha256'], path
    with (ROOT / 'results/baseline/test_predictions.csv').open(encoding='utf-8-sig', newline='') as f:
        rows = list(csv.DictReader(f))
    metrics = json.loads((ROOT / 'results/baseline/metrics.json').read_text())
    checked = {}
    for name, score in metrics.items():
        matches = sum(int(r['label']) == int(r[name]) for r in rows)
        accuracy = matches / len(rows)
        assert abs(accuracy - score['accuracy']) < 1e-12
        assert score['n'] == len(rows)
        tp = sum(int(r['label']) == 1 and int(r[name]) == 1 for r in rows)
        fp = sum(int(r['label']) == 0 and int(r[name]) == 1 for r in rows)
        fn = sum(int(r['label']) == 1 and int(r[name]) == 0 for r in rows)
        f1 = 2 * tp / (2 * tp + fp + fn) if 2 * tp + fp + fn else 0
        assert abs(f1 - score['f1']) < 1e-12
        checked[name] = dict(correct=matches, n=len(rows), accuracy=accuracy, f1=f1)
    for r in rows:
        assert r['target_date'] > r['date']
        assert int(r['label']) == int(float(r['next_yield_change_pctpoint']) <= 0)
    with (ROOT / 'data/processed/formal/dataset.csv').open(encoding='utf-8-sig', newline='') as f:
        dataset = list(csv.DictReader(f))
    train = [r for r in dataset if r['split'] == 'train']
    val = [r for r in dataset if r['split'] == 'validation']
    test = [r for r in dataset if r['split'] == 'test']
    assert max(r['target_date'] for r in train) < min(r['date'] for r in val)
    assert max(r['target_date'] for r in val) < min(r['date'] for r in test)
    assert len(test) == len(rows)
    result = dict(status='passed', imported_files_verified=len(manifest), independently_recomputed=checked,
                  checks=['SHA256', 'label from next observed yield', 'chronological partition boundaries', 'accuracy and F1 via csv counts'])
    (ROOT / 'results/baseline/verification.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
