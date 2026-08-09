import json
import tempfile
import unittest
from pathlib import Path

import backend.recommend as recommend_mod


class PopularityTests(unittest.TestCase):
    def test_popularity_boosts_beginner(self):
        payload = [
            {"skill_name": "Skill A", "curriculum_level": "Beginner", "popularity": 1.0},
            {"skill_name": "Skill B", "curriculum_level": "Advanced", "popularity": 1.0},
        ]

        with tempfile.TemporaryDirectory() as tmp_dir:
            data_path = Path(tmp_dir) / "recommendations.json"
            data_path.write_text(json.dumps(payload), encoding="utf-8")

            original_data_path = recommend_mod.DATA_PATH
            try:
                recommend_mod.DATA_PATH = data_path
                results = recommend_mod.recommend_for_skills(["Skill"], method="keyword")
            finally:
                recommend_mod.DATA_PATH = original_data_path

        self.assertTrue(results)
        self.assertGreater(results[0]["match_score"], results[1]["match_score"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
