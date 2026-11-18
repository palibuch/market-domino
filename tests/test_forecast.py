from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_domino.forecast import forecast_next
from market_domino.ml import PriceBar


class ForecastTests(unittest.TestCase):
    def make_bars(self, count=160):
        start = datetime(2025, 1, 1, tzinfo=timezone.utc)
        close = [100.0]
        for index in range(1, count):
            change = 0.001 + ((index % 7) - 3) * 0.0004
            close.append(close[-1] * (1.0 + change))
        return [PriceBar(start + timedelta(days=index), value) for index, value in enumerate(close)]

    def test_forecast_is_finite_reproducible_and_reports_diagnostics(self):
        bars = self.make_bars()
        first = forecast_next(bars)
        self.assertEqual(first, forecast_next(bars))
        self.assertTrue(0.0 <= first.probability_up <= 1.0)
        self.assertLessEqual(first.lower_90, first.expected_return)
        self.assertGreaterEqual(first.upper_90, first.expected_return)
        self.assertEqual(first.calibration_observations, 28)
        self.assertGreaterEqual(first.calibration_mae, 0.0)
        self.assertGreaterEqual(first.baseline_calibration_mae, 0.0)
        self.assertEqual(first.as_of, bars[-1].timestamp)
        self.assertIn("conformal", first.interval_method)

    def test_unknown_future_label_is_not_used(self):
        bars = self.make_bars()
        forecast = forecast_next(bars)
        self.assertEqual(forecast.as_of, bars[-1].timestamp)
        # Appending a future observation can add one known training/calibration
        # target, but cannot change the timestamp of the earlier forecast.
        last = bars[-1]
        future = bars + [PriceBar(last.timestamp + timedelta(days=1), last.close * 1.01)]
        self.assertEqual(forecast_next(future).as_of, future[-1].timestamp)

    def test_requires_enough_history_for_train_and_calibration(self):
        with self.assertRaisesRegex(ValueError, "insufficient training data"):
            forecast_next(self.make_bars(40))

    def test_rejects_unsorted_bars(self):
        bars = self.make_bars(30)
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            forecast_next([bars[1], bars[0], *bars[2:]])

    def test_validates_calibration_configuration(self):
        with self.assertRaisesRegex(ValueError, "calibration_fraction"):
            forecast_next(self.make_bars(), calibration_fraction=0.8)
        with self.assertRaisesRegex(ValueError, "must be an integer"):
            forecast_next(self.make_bars(), min_calibration_observations=5.5)


if __name__ == "__main__":
    unittest.main()
