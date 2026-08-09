import os
import sys
import unittest

os.chdir(r"c:\Users\user\Desktop\python pj\curriculum-recommender")
suite = unittest.defaultTestLoader.discover("tests")
result = unittest.TextTestRunner(verbosity=2).run(suite)
with open("test_results.txt", "w", encoding="utf-8") as handle:
    handle.write("PASS\n" if result.wasSuccessful() else "FAIL\n")
sys.exit(0 if result.wasSuccessful() else 1)
