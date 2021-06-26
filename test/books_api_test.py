"""
    Books module tests
"""
import unittest
from pathlib import Path
from plugins.books.book_loader import process_book, load_book, read_file
from api.books.books_api import find_book_cover


class BooksAPITest(unittest.TestCase):
    '''Books module API tester class
    '''

    def setUp(self):
        self.lines = read_file('./test/data/book.txt')

    def test_process_book(self):
        book_dict = process_book(self.lines)
        self.assertTrue('font-weight' in book_dict)
        self.assertTrue(len(book_dict['pages']) == 4)

    def test_process_book_empty_book(self):
        book_dict = process_book([])
        self.assertTrue(len(book_dict.keys()) == 1)
        self.assertTrue(book_dict['pages'] == [])

    def test_load_book(self):
        book_dict = load_book(1, Path('./test/data/book.txt'))
        self.assertEqual(book_dict['id'], 1)

    def test_load_book_image_pages(self):
        book = load_book(1, Path('./test/data/book.txt'))
        self.assertTrue('image' not in book)
        pages = book['pages']
        image = None
        for element in pages:
            if 'image' in element:
                image = element['image']
        self.assertIsNotNone(image)

    def test_get_text_book_cover(self):
        book = load_book(1, Path('./test/data/book.txt'))
        cover = find_book_cover(None, book)
        self.assertEqual(cover.name, 'image.jpg')


if __name__ == "__main__":
    unittest.main()
