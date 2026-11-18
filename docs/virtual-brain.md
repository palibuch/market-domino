# Virtual research brain: staged design

## What we are building

Market Domino can grow into a research assistant that proposes and tests market hypotheses, maintains an auditable memory of evidence, and reports uncertainty. It cannot be made into a literal human-like mind by increasing a neuron count. A large neural network is a parameterized function; learning, reasoning, and reliable conclusions require data contracts, objectives, evaluation, and traceable evidence as much as model capacity.

The first implementation milestone is `market_domino.neural.NeuralRegressor`: a deterministic, small tanh multilayer perceptron for numeric experiments. It is deliberately modest, has no external data access, and does not claim to understand markets. It is a component to compare against the existing linear model, not an automatic replacement.

## Why not billions of neurons now?

A dense network with one billion weights requires at least 4 GB just to store float32 weights, before gradients, optimizer state, activations, or data. Training would need large, licensed, point-in-time datasets and suitable accelerators. A billion-neuron target without a defined task or validated data would add cost, not evidence of capability. The library currently has no market-data dependency and should preserve that boundary.

## Research architecture

1. **Point-in-time data and provenance:** store event time, publication/availability time, retrieval time, source/license, and content hash. Features available at a forecast timestamp must not incorporate later publications or revised data.
2. **Task-specific learners:** keep separate models for return regression, direction classification, volatility/risk estimation, and scenario-edge ranking. Do not mix their scores or call them one universal probability.
3. **Compact model portfolio:** compare a zero-return predictor, training median, current linear baseline, and neural candidates. Use only chronological expanding/rolling folds; fit preprocessing on each training fold only.
4. **Auditable memory:** retain hypotheses, evidence identifiers, counter-evidence, assumptions, model/version, timestamps, and outcomes. A language model may summarize this record but must not fabricate evidence or alter measurements.
5. **Learning and drift:** update only after labels become observable; monitor feature/label drift and out-of-sample performance; retrain by an explicit reproducible schedule and keep a rollback model.
6. **Decision gate:** require net-of-cost improvement over baselines across multiple periods, uncertainty intervals, and stress/regime slices before treating a model as useful. Never wire research output to broker execution.

## Neural baseline contract

`NeuralRegressor.fit` accepts numeric rows and targets from one training fold, standardizes from that fold, uses seeded initialization, and optimizes a one-hidden-layer tanh network by full-batch gradient descent. The fitted object is immutable. The API does not perform time splitting, hyperparameter selection, data download, or live adaptation. Those belong in an evaluation/pipeline layer with explicit point-in-time rules.

The training MSE is in-sample only and must not be used to claim predictive quality. Evaluate with repeated walk-forward folds and compare against the same-fold baselines. Synthetic data is useful for testing code paths and known relationships, but not evidence of market edge.

## Scaling path

- **Now:** test the compact model on synthetic functions; benchmark against `SimpleLinearModel`; validate deterministic fit and finite behavior.
- **Next:** add walk-forward evaluation that fits all preprocessing and models independently per fold, reports MAE/MSE and baseline deltas, and prevents overlapping label horizons.
- **Then:** integrate licensed point-in-time data through a separate adapter and add regime/drift and uncertainty diagnostics.
- **Only after evidence:** consider a maintained tensor framework and larger architectures. Use sparse routing or retrieval for scale where justified; keep a compact model reproducible for audits.

The engine's goal is not to imitate a brain by neuron count. Its differentiator should be a disciplined loop: observe with provenance, propose a falsifiable hypothesis, test it out of sample, preserve counter-evidence, and revise confidence transparently.
