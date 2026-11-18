# First learning loop

The first neural-learning loop is implemented in `market_domino.neural_eval`.
It trains a fresh deterministic MLP for each expanding chronological fold and
compares its regression errors with a diagonal linear model, a zero-return
predictor, and a training-mean predictor. Preprocessing is fitted within each
fold by the neural model. Test folds are not used to fit that fold's model.

Example:

```python
from market_domino.neural_eval import evaluate_neural_walk_forward

report = evaluate_neural_walk_forward(
    price_bars,
    train_size=500,
    test_size=50,
    hidden_units=8,
    epochs=300,
    seed=42,
)
print(report.neural_mse, report.linear_mse, report.neural_beats_linear)
```

This is a research evaluation loop, not an autonomous live learner. It does not
fetch or invent financial observations, place trades, select hyperparameters
on test data, or update itself as future labels arrive. Use real, licensed,
point-in-time bars for a market study. Synthetic data is suitable only for
checking implementation behavior. A lower test error on one dataset is not
proof of persistent edge; inspect each fold, data provenance, costs, and
uncertainty before drawing conclusions.
