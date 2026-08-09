import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from backend.api import app
from backend import profiles


class ApiTests(unittest.TestCase):
    def setUp(self) -> None:
        if profiles.PROFILES_PATH.exists():
            profiles.PROFILES_PATH.unlink()

    def tearDown(self) -> None:
        if profiles.PROFILES_PATH.exists():
            profiles.PROFILES_PATH.unlink()
    def test_health_endpoint(self) -> None:
        client = TestClient(app)
        response = client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_health_alias_endpoint(self) -> None:
        client = TestClient(app)
        response = client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")

    def test_recommend_endpoint(self) -> None:
        client = TestClient(app)
        response = client.get("/recommend", params={"skills": "Python,Data Science"})
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["input_skills"], ["Python", "Data Science"])
        self.assertTrue(payload["recommendations"])

    def test_post_recommend_with_params(self) -> None:
        client = TestClient(app)
        body = {"skills": ["Python", "SQL"]}
        response = client.post("/recommend?method=keyword&top_n=2", json=body)
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["input_skills"], ["Python", "SQL"])
        self.assertTrue(isinstance(payload["recommendations"], list))

    def test_profiles_support_extended_preferences(self) -> None:
        client = TestClient(app)
        create_response = client.post(
            "/profiles",
            json={
                "name": "Maya",
                "prefs": {"area": "Data Science", "level": "Intermediate"},
                "goals": ["Become a data analyst"],
                "career_focus": "Analytics",
                "last_skills": ["Python", "SQL"],
            },
        )
        self.assertEqual(create_response.status_code, 200)
        profile_id = create_response.json()["profile"]["id"]

        update_response = client.put(
            f"/profiles/{profile_id}",
            json={
                "name": "Maya",
                "prefs": {"area": "Programming", "level": "Advanced"},
                "goals": ["Build production-ready tools"],
                "career_focus": "Software Engineering",
                "last_skills": ["Python", "FastAPI"],
                "learning_style": "project-based",
            },
        )
        self.assertEqual(update_response.status_code, 200)
        payload = update_response.json()["profile"]
        self.assertEqual(payload["goals"], ["Build production-ready tools"])
        self.assertEqual(payload["career_focus"], "Software Engineering")
        self.assertEqual(payload["last_skills"], ["Python", "FastAPI"])
        self.assertEqual(payload["learning_style"], "project-based")


if __name__ == "__main__":
    unittest.main(verbosity=2)
