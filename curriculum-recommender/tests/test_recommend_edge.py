import unittest
from backend.recommend import _normalize_text, _tokenize, recommend_for_skills


class RecommendEdgeTests(unittest.TestCase):
    def test_normalize_text_removes_punctuation(self):
        self.assertEqual(_normalize_text("Data-Science!"), "data science")
        self.assertEqual(_normalize_text("  Python  "), "python")

    def test_tokenize_splits_tokens(self):
        self.assertEqual(_tokenize("Python Programming"), {"python", "programming"})

    def test_empty_input_returns_empty(self):
        self.assertEqual(recommend_for_skills([]), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
