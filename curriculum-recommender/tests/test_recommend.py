import json
import tempfile
import unittest
from pathlib import Path

import backend.recommend as recommend_mod


class RecommendationTests(unittest.TestCase):
    def test_normalizes_punctuation_and_prefers_related_matches(self) -> None:
        payload = [
            {"skill_name": "Data Science Basics", "curriculum_title": "Data Science Basics"},
            {"skill_name": "Python Programming", "curriculum_title": "Python Programming"},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            data_path = Path(tmp_dir) / "recommendations.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")

            original_data_path = recommend_mod.DATA_PATH
            try:
                recommend_mod.DATA_PATH = data_path
                results = recommend_mod.recommend_for_skills(["Data-Science", "Python"])
            finally:
                recommend_mod.DATA_PATH = original_data_path

        self.assertTrue(results, "expected at least one recommendation")
        self.assertEqual(results[0]["skill_name"], "Data Science Basics")
        self.assertGreater(results[0]["match_score"], 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
