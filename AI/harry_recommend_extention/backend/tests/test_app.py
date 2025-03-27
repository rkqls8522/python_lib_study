import unittest
from utils.keyword_extractor import extract_keywords_yake

class TestKeywordExtractor(unittest.TestCase):
    def test_extract_keywords(self):
        text = "This is a test text. It contains several words and some repeated words test test."
        keywords, elapsed_time = extract_keywords_yake(text)
        self.assertIsInstance(keywords, list)
        self.assertTrue(len(keywords) <= 4)

if __name__ == '__main__':
    unittest.main()
