import unittest

from backend.advanced_recommender import build_gap_report, optimize_course_selection


class AdvancedRecommenderTests(unittest.TestCase):
    def test_gap_report_and_course_selection(self) -> None:
        profile = {
            "email": "student@example.com",
            "display_name": "Ali",
            "skills": ["Python", "SQL"],
            "career_goal": "Backend Engineer",
            "target_level": "Intermediate",
        }
        report = build_gap_report(profile)
        self.assertTrue(report["gap_skills"])
        self.assertTrue(report["recommended_courses"])
        selection = optimize_course_selection(report["recommended_courses"], max_courses=2)
        self.assertLessEqual(len(selection), 2)


if __name__ == "__main__":
    unittest.main(verbosity=2)
