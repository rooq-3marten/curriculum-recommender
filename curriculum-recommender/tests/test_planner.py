import unittest

from backend.planner import build_learning_plan, compute_skill_value


class PlannerTests(unittest.TestCase):
    def test_compute_skill_value_uses_importance_level_and_alignment(self) -> None:
        value = compute_skill_value("Python", level="Intermediate", importance=1.0, alignment=0.9)
        self.assertGreater(value, 0.8)

    def test_build_learning_plan_respects_prerequisites_and_returns_reasoning(self) -> None:
        profile = {
            "skills": ["Python", "SQL"],
            "career_goal": "Backend Engineer",
            "target_level": "Intermediate",
        }
        result = build_learning_plan(profile, max_courses=3)
        self.assertTrue(result["plan"])
        self.assertTrue(result["missing_skills"])
        self.assertTrue(result["recommended_courses"])
        self.assertIn("reasoning", result)

    def test_build_learning_plan_prefers_prerequisite_chain(self) -> None:
        profile = {
            "skills": ["Python"],
            "career_goal": "Backend Engineer",
            "target_level": "Intermediate",
        }
        result = build_learning_plan(profile, max_courses=2)
        plan_ids = [item["id"] for item in result["recommended_courses"]]
        self.assertIn("python-foundations", plan_ids)
        self.assertIn("fastapi-production", plan_ids)


if __name__ == "__main__":
    unittest.main(verbosity=2)
