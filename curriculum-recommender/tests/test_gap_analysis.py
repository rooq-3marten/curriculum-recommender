import unittest

from fastapi.testclient import TestClient

from backend.api import app


class GapAnalysisTests(unittest.TestCase):
    def test_gap_analysis_endpoint(self) -> None:
        client = TestClient(app)
        response = client.post(
            "/gap-analysis",
            json={
                "curriculum_skills": ["Python", "SQL", "Data Science"],
                "job_posting_text": "We need a backend engineer skilled in Python, FastAPI, SQL, Docker, and Kubernetes.",
            },
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("Python", payload["matched_skills"])
        self.assertIn("FastAPI", payload["gap_skills"])
        self.assertGreaterEqual(payload["coverage_percent"], 0.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
