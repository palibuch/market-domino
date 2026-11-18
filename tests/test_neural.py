from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_domino.neural import NeuralRegressor


class NeuralRegressorTests(unittest.TestCase):
    def test_training_is_deterministic_and_learns_simple_relationship(self):
        rows = [[index / 10.0, (index % 5) / 5.0] for index in range(40)]
        targets = [2.0 * row[0] - 0.5 * row[1] + 1.0 for row in rows]
        model = NeuralRegressor.fit(rows, targets, hidden_units=10, epochs=500, seed=7)
        repeated = NeuralRegressor.fit(rows, targets, hidden_units=10, epochs=500, seed=7)
        self.assertEqual(model, repeated)
        self.assertLess(model.training_mse, 0.05)
        self.assertAlmostEqual(model.predict(rows[10]), targets[10], delta=0.3)

    def test_constant_target_produces_finite_predictions(self):
        model = NeuralRegressor.fit([[1.0], [2.0], [3.0]], [0.25, 0.25, 0.25])
        self.assertTrue(abs(model.predict([2.0]) - 0.25) < 1e-9)
        self.assertEqual(model.training_mse, 0.0)

    def test_rejects_bad_shapes_and_non_finite_data(self):
        with self.assertRaisesRegex(ValueError, "equal, non-zero"):
            NeuralRegressor.fit([[1.0]], [])
        with self.assertRaisesRegex(ValueError, "same non-zero width"):
            NeuralRegressor.fit([[1.0], [1.0, 2.0]], [1.0, 2.0])
        with self.assertRaisesRegex(ValueError, "finite"):
            NeuralRegressor.fit([[float("nan")]], [1.0])

    def test_rejects_invalid_hyperparameters(self):
        with self.assertRaisesRegex(ValueError, "hidden_units"):
            NeuralRegressor.fit([[1.0]], [1.0], hidden_units=0)
        with self.assertRaisesRegex(ValueError, "epochs"):
            NeuralRegressor.fit([[1.0]], [1.0], epochs=0)
        with self.assertRaisesRegex(ValueError, "learning_rate"):
            NeuralRegressor.fit([[1.0]], [1.0], learning_rate=float("nan"))

    def test_prediction_validates_feature_width_and_finiteness(self):
        model = NeuralRegressor.fit([[1.0, 2.0], [3.0, 4.0]], [0.0, 1.0])
        with self.assertRaisesRegex(ValueError, "feature width"):
            model.predict([1.0])
        with self.assertRaisesRegex(ValueError, "finite"):
            model.predict([float("inf"), 2.0])


if __name__ == "__main__":
    unittest.main()
