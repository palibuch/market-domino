from datetime import datetime, timezone
import unittest

from market_domino import (
    Hypothesis,
    MarketDominoEngine,
    MarketEdge,
    MarketNode,
)

T0 = datetime(2025, 1, 1, tzinfo=timezone.utc)
T1 = datetime(2025, 1, 2, tzinfo=timezone.utc)
T2 = datetime(2025, 1, 3, tzinfo=timezone.utc)


def node(node_id: str, observed_at=T0, confidence=1.0) -> MarketNode:
    return MarketNode(node_id, node_id.title(), "indicator", "test-fixture", observed_at, confidence)


def hypothesis(hypothesis_id="h1", created_at=T0, status="confirmed") -> Hypothesis:
    return Hypothesis(hypothesis_id, "Testable relation", "Fails in two walk-forward windows", created_at, status)


def edge(source, target, *, effect=0.5, observed_at=T1, status="confirmed", hypothesis_id="h1", effect_std=0.0):
    return MarketEdge(source, target, hypothesis_id, effect, 0.8, observed_at, T1,
                      lag_sessions=2, effect_std=effect_std, evidence_ids=("ev-1",),
                      evidence_count=20, status=status)


class CausalEngineTests(unittest.TestCase):
    def make_engine(self):
        engine = MarketDominoEngine()
        for item in (node("a"), node("b", T1), node("c", T1)):
            engine.add_node(item)
        engine.add_hypothesis(hypothesis())
        return engine

    def test_propagates_through_path_and_is_reproducible(self):
        engine = self.make_engine()
        engine.add_edge(edge("a", "b", effect=-0.5))
        engine.add_edge(edge("b", "c", effect=0.5, hypothesis_id="h1"))
        first = engine.propagate("a", 0.8, T2, draws=100, seed=7)
        second = engine.propagate("a", 0.8, T2, draws=100, seed=7)
        self.assertEqual(first.id, second.id)
        impact_c = next(item for item in first.impacts if item.node_id == "c")
        self.assertLess(impact_c.median_impact, 0)
        self.assertEqual(impact_c.representative_path, ("a", "b", "c"))
        self.assertEqual(impact_c.evidence_ids, ("ev-1",))

    def test_rejects_cycle(self):
        engine = self.make_engine()
        engine.add_edge(edge("a", "b"))
        with self.assertRaisesRegex(ValueError, "cycle"):
            engine.add_edge(edge("b", "a"))

    def test_point_in_time_filter_excludes_future_edge(self):
        engine = self.make_engine()
        engine.add_edge(edge("a", "b", observed_at=T2))
        result = engine.propagate("a", 1.0, T1, draws=100)
        self.assertEqual(result.impacts, ())

    def test_draft_edges_are_not_used(self):
        engine = self.make_engine()
        draft = edge("a", "b", status="draft")
        engine.add_edge(draft)
        result = engine.propagate("a", 1.0, T2, draws=100)
        self.assertEqual(result.impacts, ())

    def test_deterministic_edge_has_exact_impact(self):
        engine = self.make_engine()
        engine.add_edge(edge("a", "b", effect=0.5))
        result = engine.propagate("a", 0.8, T2, draws=100)
        impact = result.impacts[0]
        self.assertAlmostEqual(impact.median_impact, 0.4)
        self.assertAlmostEqual(impact.lower_90, 0.4)
        self.assertAlmostEqual(impact.upper_90, 0.4)

    def test_validation_rejects_naive_datetime(self):
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            node("naive", datetime(2025, 1, 1))

    def test_requires_existing_hypothesis(self):
        engine = MarketDominoEngine()
        engine.add_node(node("a"))
        engine.add_node(node("b"))
        with self.assertRaisesRegex(ValueError, "registered hypothesis"):
            engine.add_edge(edge("a", "b", hypothesis_id="missing"))

    def test_rejects_future_source(self):
        engine = self.make_engine()
        with self.assertRaisesRegex(ValueError, "not available"):
            engine.propagate("b", 0.5, T0, draws=100)


if __name__ == "__main__":
    unittest.main()
