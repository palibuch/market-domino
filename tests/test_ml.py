from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_domino.ml import (
    PriceBar,
    SimpleLinearModel,
    chronological_splits,
    evaluate_model,
    features,
)


class MachineLearningTests(unittest.TestCase):
    def test_walk_forward_windows_do_not_overlap(self):
        splits = list(chronological_splits(100, 60, 20))
        self.assertEqual(len(splits), 2)
        train, test = splits[0]
        self.assertEqual((train.start, train.stop), (0, 60))
        self.assertEqual((test.start, test.stop), (60, 80))

    def test_leak_free_feature_row_only_uses_existing_close(self):
        close = [100 + index for index in range(30)]
        result = features(close)
        self.assertEqual(len(result), 10)
        self.assertEqual(len(result[0]), 4)

    def test_linear_model_trains_and_predicts(self):
        model = SimpleLinearModel.fit(
            [[0.0], [1.0], [2.0], [3.0]],
            [1.0, 3.0, 5.0, 7.0],
        )
        self.assertGreater(model.predict([4.0]), 8.0)

    def test_timezone_aware_bars_are_required(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            PriceBar(datetime(2025, 1, 1), 100.0)

    def test_evaluate_model_rejects_short_training(self):
        now = datetime(2025, 1, 1, tzinfo=timezone.utc)
        bars = [PriceBar(now + timedelta(days=index), 100.0 + index) for index in range(25)]
        with self.assertRaisesRegex(ValueError, "fewer than 10"):
            evaluate_model(bars, range(0, 5), range(5, 25))


if __name__ == "__main__":
    unittest.main()
