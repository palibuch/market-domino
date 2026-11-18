import sqlite3
from datetime import datetime, timezone
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_domino.journal import ResearchJournal


class ResearchJournalTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.database = Path(self.temp_dir.name) / "research.sqlite3"
        self.journal = ResearchJournal(self.database)

    def test_records_and_filters_auditable_experiment_history(self):
        timestamp = datetime(2026, 1, 2, 3, 4, tzinfo=timezone.utc)
        first = self.journal.append(
            "exp-1", "hypothesis", {"claim": "baseline is hard to beat"}, created_at=timestamp
        )
        second = self.journal.append(
            "exp-1", "prediction", {"expected": 0.1}, created_at=timestamp
        )
        self.journal.append("exp-2", "outcome", {"observed": 0.2})

        self.assertEqual([event.kind for event in self.journal.events("exp-1")], [
            "hypothesis", "prediction"
        ])
        self.assertEqual((first.sequence, second.sequence), (1, 2))
        self.assertEqual(second.previous_hash, first.event_hash)
        self.assertTrue(self.journal.verify_chain())

    def test_history_survives_reopening(self):
        self.journal.append("exp-1", "decision", {"accepted": False})
        reopened = ResearchJournal(self.database)
        self.assertEqual(reopened.events(), self.journal.events())
        self.assertTrue(reopened.verify_chain())

    def test_rejects_invalid_events_and_non_finite_payloads(self):
        with self.assertRaisesRegex(ValueError, "experiment_id"):
            self.journal.append(" ", "hypothesis", {})
        with self.assertRaisesRegex(ValueError, "kind"):
            self.journal.append("exp", "trade", {})
        with self.assertRaisesRegex(ValueError, "finite JSON"):
            self.journal.append("exp", "outcome", {"value": float("nan")})
        with self.assertRaisesRegex(ValueError, "timezone-aware"):
            self.journal.append(
                "exp", "outcome", {}, created_at=datetime(2026, 1, 1)
            )

    def test_detects_payload_tampering(self):
        self.journal.append("exp-1", "hypothesis", {"claim": "original"})
        with sqlite3.connect(self.database) as connection:
            connection.execute(
                "UPDATE journal_events SET payload_json = ? WHERE sequence = 1",
                ('{"claim":"altered"}',),
            )
        self.assertFalse(self.journal.verify_chain())


if __name__ == "__main__":
    unittest.main()
