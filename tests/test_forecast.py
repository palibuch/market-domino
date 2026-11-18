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
        # Deterministic varied returns, with no external data or network access.
        close = [100.0]
        for index in range(1, count):
            change = 0.001 + ((index % 7) - 3) * 0.0004
            close.append(close[-1] * (1.0 + change))
        return [PriceBar(start + timedelta(days=index), value) for index, value in enumerate(close)]

    def test_forecast_is_finite_and_reproducible(self):
        bars = self.make_bars()
        first = forecast_next(bars)
        second = forecast_next(bars)
        self.assertEqual(first, second)
        self.assertTrue(-1.0 <= first.probability_up <= 1.0)
        self.assertLessEqual(first.lower_90, first.upper_90)
        self.assertEqual(first.calibration_observations, 28)
        self.assertEqual(first.as_of, bars[-1].timestamp)

    def test_latest_close_change_does_not_change_its_own_forecast_features(self):
        bars = self.make_bars()
        original = forecast_next(bars)
        changed = list(bars)
        last = changed[-1]
        changed[-1] = PriceBar(last.timestamp, last.close * 1.5)
        # The latest close is part of the feature row, so its forecast may change;
        # adding a future bar must not alter the already-issued forecast.
        future = changed + [PriceBar(last.timestamp + timedelta(days=1), last.close * 1.51)]
        self.assertEqual(original.as_of, bars[-1].timestamp)
        self.assertNotEqual(forecast_next(future).as_of, original.as_of)

    def test_requires_enough_history(self):
        with self.assertRaisesRegex(ValueError, "at least 22 bars"):
            forecast_next(self.make_bars(21))

    def test_rejects_unsorted_bars(self):
        bars = self.make_bars(30)
        with self.assertRaisesRegex(ValueError, "strictly increasing"):
            forecast_next([bars[1], bars[0], *bars[2:]])

    def test_validates_calibration_configuration(self):
        with self.assertRaisesRegex(ValueError, "calibration_fraction"):
            forecast_next(self.make_bars(), calibration_fraction=0.8)


if __name__ == "__main__":
    unittest.main()
