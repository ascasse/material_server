import logging
from os import environ
from pathlib import Path

from flask import Blueprint, jsonify, abort
from dotenv import load_dotenv

from material_loader import MaterialLoader
from util import make_image_response

logger = logging.getLogger(__name__)

books_api = Blueprint('books_api', __name__)

load_dotenv()

MATERIAL = environ.get('MATERIAL', '.')
books_location = Path(MATERIAL).joinpath('books')
logger.info(f'Loading books from {str(books_location)}')
loader = MaterialLoader(books_location)
loader.load()
ctgs, books = loader.get_element_count('books')
logger.info(f'Found {books} books in {ctgs} categories.')


@books_api.route('/books/info')
def get_books_info():
    return jsonify(loader.get_element_count('books'))


@books_api.route('/books')
def get_books():
    logger.debug('get_books')
    return jsonify(loader.categories)


@books_api.route('/books/text/<int:book_id>')
def get_text_book(book_id):
    logger.debug('get_text_books')
    category, found_book = loader.find_book(book_id)
    if found_book is None:
        abort(404)
    return jsonify(found_book)


@books_api.route('/books/<int:book_id>')
def get_book(book_id):
    category, found_book = loader.find_book(book_id)
    if found_book is None:
        abort(404)
    if 'imagefilepath' in found_book:
        return make_image_response(found_book['imagefilepath'])
    else:
        return jsonify(found_book)


@books_api.route('/books/cover/<int:book_id>')
def get_book_cover(book_id):
    category, found_book = loader.find_book(book_id)
    if found_book is None:
        abort(404)
    book_cover = find_book_cover(category, found_book)
    if book_cover is None or not book_cover.exists():
        abort(404)
    return make_image_response(book_cover)


@books_api.route('/books/image/<int:book_id>', defaults={'ordinal': 0})
@books_api.route('/books/image/<int:book_id>/<int:ordinal>')
def get_book_image(book_id, ordinal=0):
    ''' Retrieve an image from a book '''
    category, found_book = loader.find_book(book_id)
    if found_book is None:
        abort(404)
    book_images = [page for page in found_book['pages'] if 'image' in page]
    if ordinal >= len(book_images):
        abort(404)
    return make_image_response(books_location.joinpath(category['name'], book_images[ordinal]['image']))


def find_book_cover(category, book):
    '''
        Get the image that will be used as book cover.
        For 'image' books look for a file ending with '_cover.jpg'
        For 'text' books look for a cover field
    '''
    if 'imagefilepath' in book:
        # image book
        book_path = Path(book['imagefilepath'])
        book_cover = book_path.parent.joinpath(book_path.stem + '_cover.jpg')
        if not book_cover.exists():
            if category is not None:
                return book_path.parent.joinpath(category, 'cover.jpg')
            else:
                return book_path.parent.joinpath('cover.jpg')
    else:
        # text book
        if 'cover' in book and book['cover'] is not None:
            if category is not None:
                return books_location.joinpath(category['name'], book['cover'])
            else:
                return books_location.joinpath(book['cover'])
        return None
