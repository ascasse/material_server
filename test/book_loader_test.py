import unittest
from book_loader import process_book, read_file, load_json_book


class BookLoaderTest(unittest.TestCase):

    def setUp(self):
        self.no_lines = read_file('./test/data/book.txt')
        self.lines = read_file('./test/data/book_lines.txt')
        self.lines_mixed = read_file('./test/data/book_lines_mixed.txt')

    def test_process_book_lines_mixed(self):
        book = process_book(self.lines_mixed)
        self.assertIsNotNone(book)
        self.assertEqual(len(book['pages']), 5)
        self.assertEqual(len(book['pages'][0]['lines']), 2)
        self.assertEqual(len(book['pages'][1]['lines']), 1)
        self.assertEqual(len(book['pages'][2]['lines']), 1)
        self.assertEqual(len(book['pages'][3]['lines']), 1)

    def test_process_book_no_lines(self):
        book = process_book(self.no_lines)
        self.assertIsNotNone(book)
        self.assertEqual(len(book['pages']), 4)
        self.assertEqual(len(book['pages'][0]['lines']), 1)
        self.assertEqual(len(book['pages'][1]['lines']), 1)
        self.assertEqual(len(book['pages'][2]['lines']), 1)

    def test_process_book_lines(self):
        book = process_book(self.lines)
        self.assertIsNotNone(book)
        self.assertEqual(len(book['pages']), 4)
        self.assertEqual(len(book['pages'][0]['lines']), 3)
        self.assertEqual(len(book['pages'][1]['lines']), 1)
        self.assertEqual(len(book['pages'][2]['lines']), 2)

    def test_load_json_book(self):
        book = load_json_book(1, './test/data/las moscas y la miel.json')
        self.assertIsNotNone(book)
        self.assertEqual(len(book['pages']), 5)
        self.assertEqual(book['id'], 1)
