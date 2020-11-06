"""
    Test Loader class
"""
import unittest
from pathlib import Path
from plugins.vocabulary.loader import Loader


class VocabularyTest(unittest.TestCase):
    def test_load_from_json(self):
        voc = Loader(0, "test/data")
        vocabulary = voc.load_json("test/data/Vocabulary/sample.json")
        print(*vocabulary)
        self.assertTrue(len(vocabulary) == 2, f"Found: {len(vocabulary)}")

    def test_load_from_text(self):
        voc = Loader(0, "test/data")
        vocabulary = voc.load_text("test/data/Vocabulary/sample.txt")
        self.assertTrue(len(vocabulary) > 0)
        print(*vocabulary)
        self.assertTrue(len(vocabulary) == 1, f"Found: {len(vocabulary)}")

    def test_load_from_location(self):
        voc = Loader(0, "data")
        vocabulary = voc.load_from_location(Path("test/data"))
        print(*vocabulary)
        self.assertTrue(len(vocabulary) == 3, f"Found: {len(vocabulary)}")
