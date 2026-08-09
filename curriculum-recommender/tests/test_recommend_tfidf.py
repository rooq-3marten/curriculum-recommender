import json
import tempfile
import unittest
from pathlib import Path

import backend.recommend as recommend_mod


class TfidfTests(unittest.TestCase):
    def test_tfidf_prefers_semantic_match(self):
        payload = [
            {"skill_name": "Intro to Basketball", "curriculum_title": "Sports"},
            {"skill_name": "Advanced Basketball Tactics", "curriculum_title": "Sports"},
            {"skill_name": "Python for Data Science", "curriculum_title": "Programming"},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            data_path = Path(tmp_dir) / "recommendations.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")

            original_data_path = recommend_mod.DATA_PATH
            try:
                recommend_mod.DATA_PATH = data_path
                results = recommend_mod.recommend_for_skills(["Basketball"], method="auto")
            finally:
                recommend_mod.DATA_PATH = original_data_path

        self.assertTrue(results, "expected recommendations")
        self.assertIn("Basketball", results[0]["skill_name"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
