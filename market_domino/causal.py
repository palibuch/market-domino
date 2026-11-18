"""Auditable scenario propagation for research graphs.

This module computes illustrative scenario-impact scores. It does not identify
causal effects from observational data and does not produce price forecasts.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from datetime import datetime
from hashlib import sha256
import json
import math
import random
from typing import Literal

NodeKind = Literal["event", "indicator", "sector", "asset", "risk"]
EdgeStatus = Literal["draft", "testing", "confirmed", "rejected"]
HypothesisStatus = Literal["draft", "testing", "confirmed", "rejected"]


def _require_aware(value: datetime, field_name: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field_name} must be timezone-aware.")


def _bounded(value: float, lower: float, upper: float, name: str) -> None:
    if not math.isfinite(value) or not lower <= value <= upper:
        raise ValueError(f"{name} must be finite and in [{lower}, {upper}].")


@dataclass(frozen=True)
class MarketNode:
    id: str
    name: str
    kind: NodeKind
    source: str
    observed_at: datetime
    confidence: float = 1.0
    metadata: dict[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.name.strip():
            raise ValueError("Node id and name are required.")
        if not self.source.strip():
            raise ValueError("Node source is required.")
        _require_aware(self.observed_at, "observed_at")
        _bounded(self.confidence, 0.0, 1.0, "confidence")


@dataclass(frozen=True)
class Hypothesis:
    id: str
    title: str
    invalidation_rule: str
    created_at: datetime
    status: HypothesisStatus = "draft"
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        if not self.id.strip() or not self.title.strip():
            raise ValueError("Hypothesis id and title are required.")
        if not self.invalidation_rule.strip():
            raise ValueError("An explicit invalidation_rule is required.")
        _require_aware(self.created_at, "created_at")


@dataclass(frozen=True)
class MarketEdge:
    source_id: str
    target_id: str
    hypothesis_id: str
    effect: float
    confidence: float
    observed_at: datetime
    valid_from: datetime
    lag_sessions: int = 0
    effect_std: float = 0.0
    evidence_ids: tuple[str, ...] = ()
    evidence_count: int = 0
    status: EdgeStatus = "draft"
    valid_until: datetime | None = None

    def __post_init__(self) -> None:
        _bounded(self.effect, -1.0, 1.0, "effect")
        _bounded(self.confidence, 0.0, 1.0, "confidence")
        if not math.isfinite(self.effect_std) or self.effect_std < 0:
            raise ValueError("effect_std must be finite and non-negative.")
        if self.lag_sessions < 0 or self.evidence_count < 0:
            raise ValueError("lag_sessions and evidence_count must be non-negative.")
        _require_aware(self.observed_at, "observed_at")
        _require_aware(self.valid_from, "valid_from")
        if self.valid_until is not None:
            _require_aware(self.valid_until, "valid_until")
            if self.valid_until <= self.valid_from:
                raise ValueError("valid_until must be later than valid_from.")

    def active_at(self, as_of: datetime, include_testing: bool = False) -> bool:
        accepted_statuses = {"confirmed"}
        if include_testing:
            accepted_statuses.add("testing")
        return (
            self.status in accepted_statuses
            and self.observed_at <= as_of
            and self.valid_from <= as_of
            and (self.valid_until is None or as_of < self.valid_until)
        )


@dataclass(frozen=True)
class ImpactSummary:
    node_id: str
    node_name: str
    median_impact: float
    lower_90: float
    upper_90: float
    probability_positive: float
    probability_negative: float
    median_path_confidence: float
    representative_lag_sessions: int
    representative_path: tuple[str, ...]
    hypothesis_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    conflicting: bool


@dataclass(frozen=True)
class ScenarioResult:
    id: str
    source_id: str
    source_name: str
    shock: float
    as_of: datetime
    draws: int
    seed: int
    impacts: tuple[ImpactSummary, ...]
    disclaimer: str = (
        "Scenario scores are illustrative normalized impacts, not causal-effect "
        "estimates, return forecasts, or investment advice."
    )


class MarketDominoEngine:
    """Versioned DAG with point-in-time filtering and reproducible simulation."""

    def __init__(self) -> None:
        self.nodes: dict[str, MarketNode] = {}
        self.hypotheses: dict[str, Hypothesis] = {}
        self.edges: list[MarketEdge] = []
        self._outgoing: dict[str, list[MarketEdge]] = {}

    def add_node(self, node: MarketNode) -> None:
        if node.id in self.nodes:
            raise ValueError(f"Duplicate node id: {node.id}")
        self.nodes[node.id] = node
        self._outgoing[node.id] = []

    def add_hypothesis(self, hypothesis: Hypothesis) -> None:
        if hypothesis.id in self.hypotheses:
            raise ValueError(f"Duplicate hypothesis id: {hypothesis.id}")
        self.hypotheses[hypothesis.id] = hypothesis

    def _has_path(self, start: str, goal: str) -> bool:
        pending = [start]
        visited: set[str] = set()
        while pending:
            current = pending.pop()
            if current == goal:
                return True
            if current in visited:
                continue
            visited.add(current)
            pending.extend(e.target_id for e in self._outgoing.get(current, ()))
        return False

    def add_edge(self, edge: MarketEdge) -> None:
        if edge.source_id not in self.nodes or edge.target_id not in self.nodes:
            raise ValueError("Both edge endpoints must exist before adding an edge.")
        if edge.source_id == edge.target_id or self._has_path(edge.target_id, edge.source_id):
            raise ValueError("Edge would introduce a cycle; causal map must be a DAG.")
        hypothesis = self.hypotheses.get(edge.hypothesis_id)
        if hypothesis is None:
            raise ValueError("Edge must reference a registered hypothesis.")
        if hypothesis.status == "rejected" or edge.status == "rejected":
            raise ValueError("Rejected hypotheses/edges cannot be added.")
        if edge.observed_at < hypothesis.created_at:
            raise ValueError("Edge cannot predate the hypothesis that supports it.")
        self.edges.append(edge)
        self._outgoing[edge.source_id].append(edge)

    @staticmethod
    def _quantile(sorted_values: list[float], q: float) -> float:
        if len(sorted_values) == 1:
            return sorted_values[0]
        position = (len(sorted_values) - 1) * q
        low = int(position)
        high = min(low + 1, len(sorted_values) - 1)
        weight = position - low
        return sorted_values[low] * (1 - weight) + sorted_values[high] * weight

    def propagate(
        self,
        source_id: str,
        shock: float,
        as_of: datetime,
        *,
        draws: int = 2_000,
        seed: int = 42,
        max_hops: int = 6,
        max_path_expansions_per_draw: int = 20_000,
        include_testing: bool = False,
    ) -> ScenarioResult:
        _require_aware(as_of, "as_of")
        _bounded(shock, -1.0, 1.0, "shock")
        if source_id not in self.nodes:
            raise ValueError(f"Unknown source node: {source_id}")
        if self.nodes[source_id].observed_at > as_of:
            raise ValueError("Source node is not available at as_of.")
        if not 100 <= draws <= 100_000:
            raise ValueError("draws must be between 100 and 100000.")
        if max_hops < 1 or max_path_expansions_per_draw < 1:
            raise ValueError("Path limits must be positive.")

        rng = random.Random(seed)
        samples: dict[str, list[float]] = {}
        confidence_samples: dict[str, list[float]] = {}
        path_records: dict[str, dict[tuple[str, ...], tuple[float, int, set[str], set[str]]]] = {}
        node_confidence = self.nodes[source_id].confidence

        for _ in range(draws):
            # Contributions from separate paths are summed, then bounded. This is
            # a scenario aggregation rule, not an identified structural model.
            totals: dict[str, float] = {}
            weighted_confidence: dict[str, float] = {}
            absolute_weight: dict[str, float] = {}
            stack = [(source_id, shock, node_confidence, 0, (source_id,), (), ())]
            expansions = 0

            while stack:
                current, impact, confidence, lag, path, used_hypotheses, used_evidence = stack.pop()
                if len(path) - 1 >= max_hops:
                    continue
                for edge in self._outgoing.get(current, ()):
                    if not edge.active_at(as_of, include_testing):
                        continue
                    target = self.nodes[edge.target_id]
                    hypothesis = self.hypotheses[edge.hypothesis_id]
                    if target.observed_at > as_of or hypothesis.created_at > as_of:
                        continue
                    if hypothesis.status == "rejected":
                        continue
                    expansions += 1
                    if expansions > max_path_expansions_per_draw:
                        raise RuntimeError("Path expansion budget exceeded; reduce max_hops or graph size.")

                    sampled_effect = edge.effect
                    if edge.effect_std:
                        sampled_effect = min(1.0, max(-1.0, rng.gauss(edge.effect, edge.effect_std)))
                    next_impact = impact * sampled_effect
                    next_confidence = confidence * edge.confidence * target.confidence
                    next_lag = lag + edge.lag_sessions
                    next_path = path + (target.id,)
                    next_hypotheses = used_hypotheses + (edge.hypothesis_id,)
                    next_evidence = used_evidence + edge.evidence_ids

                    totals[target.id] = totals.get(target.id, 0.0) + next_impact
                    totals[target.id] = min(1.0, max(-1.0, totals[target.id]))
                    weight = abs(next_impact)
                    weighted_confidence[target.id] = weighted_confidence.get(target.id, 0.0) + weight * next_confidence
                    absolute_weight[target.id] = absolute_weight.get(target.id, 0.0) + weight

                    records = path_records.setdefault(target.id, {})
                    if next_path not in records:
                        records[next_path] = (0.0, next_lag, set(), set())
                    old_score, old_lag, old_hypotheses, old_evidence = records[next_path]
                    records[next_path] = (
                        old_score + abs(next_impact) * next_confidence,
                        old_lag,
                        old_hypotheses | set(next_hypotheses),
                        old_evidence | set(next_evidence),
                    )
                    stack.append((target.id, next_impact, next_confidence, next_lag,
                                  next_path, next_hypotheses, next_evidence))

            for node_id, value in totals.items():
                samples.setdefault(node_id, []).append(value)
                denom = absolute_weight[node_id]
                confidence_samples.setdefault(node_id, []).append(
                    weighted_confidence[node_id] / denom if denom else 0.0
                )

        summaries: list[ImpactSummary] = []
        for node_id, values in samples.items():
            # A node not reached in a draw has zero impact. Keeping zeros avoids
            # overstating the probability of a path that only exists sometimes.
            if len(values) < draws:
                values.extend([0.0] * (draws - len(values)))
                confidence_samples[node_id].extend([0.0] * (draws - len(confidence_samples[node_id])))
            ordered = sorted(values)
            positive = sum(v > 0 for v in ordered) / draws
            negative = sum(v < 0 for v in ordered) / draws
            median = self._quantile(ordered, 0.5)
            candidates = path_records[node_id]
            representative, (_, lag, hypothesis_ids, evidence_ids) = max(
                candidates.items(), key=lambda item: item[1][0]
            )
            confidence_sorted = sorted(confidence_samples[node_id])
            summaries.append(ImpactSummary(
                node_id=node_id,
                node_name=self.nodes[node_id].name,
                median_impact=median,
                lower_90=self._quantile(ordered, 0.05),
                upper_90=self._quantile(ordered, 0.95),
                probability_positive=positive,
                probability_negative=negative,
                median_path_confidence=self._quantile(confidence_sorted, 0.5),
                representative_lag_sessions=lag,
                representative_path=representative,
                hypothesis_ids=tuple(sorted(hypothesis_ids)),
                evidence_ids=tuple(sorted(evidence_ids)),
                conflicting=positive >= 0.1 and negative >= 0.1,
            ))
        summaries.sort(key=lambda item: abs(item.median_impact) * item.median_path_confidence, reverse=True)

        identity = {
            "source": source_id, "shock": shock, "as_of": as_of.isoformat(),
            "draws": draws, "seed": seed, "max_hops": max_hops,
            "edges": [asdict(e) for e in self.edges if e.active_at(as_of, include_testing)],
        }
        result_id = sha256(json.dumps(identity, sort_keys=True, default=str).encode()).hexdigest()
        return ScenarioResult(result_id, source_id, self.nodes[source_id].name,
                              shock, as_of, draws, seed, tuple(summaries))
