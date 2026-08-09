import json
import tempfile
import unittest
from pathlib import Path

import backend.recommend as recommend_mod


class AggregationTests(unittest.TestCase):
    def test_aggregate_by_curriculum_title(self):
        payload = [
            {"skill_name": "Intro A", "curriculum_title": "Path X", "curriculum_area": "Area 1", "curriculum_level": "Beginner"},
            {"skill_name": "Advanced A", "curriculum_title": "Path X", "curriculum_area": "Area 1", "curriculum_level": "Advanced"},
            {"skill_name": "Intro B", "curriculum_title": "Path Y", "curriculum_area": "Area 2", "curriculum_level": "Beginner"},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            data_path = Path(tmp_dir) / "recommendations.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")

            original_data_path = recommend_mod.DATA_PATH
            try:
                recommend_mod.DATA_PATH = data_path
                results = recommend_mod.recommend_for_skills(["Intro"], method="keyword", aggregate_by="curriculum_title")
            finally:
                recommend_mod.DATA_PATH = original_data_path

        self.assertTrue(results)
        self.assertIsInstance(results[0]["aggregate_score"], float)
        self.assertGreaterEqual(results[0]["skill_count"], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
