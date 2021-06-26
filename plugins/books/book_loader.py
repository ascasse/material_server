'''
    book_loader.py
    Functions to build a book from a definition file.
'''
import logging
import json


logger = logging.getLogger(__name__)


def load_json_book(book_id, book_path):
    ''' Load a book from a json file '''
    logger.info(book_path)
    try:
        with open(book_path, 'r', encoding='utf-8') as json_book:
            book = json.load(json_book)
            book['id'] = book_id
            return book
    except TypeError as type_error:
        logger.error(f'Invalid format. {type_error}')
        return None
    except FileNotFoundError:
        return None


def load_book(book_id, book_path):
    ''' Build a text book from a file
        Parameters:
            integer book_id to assign to the book
            Path book_path: book definition file
    '''
    lines = read_file(book_path)
    book = process_book(lines)
    if book is not None:
        book['id'] = book_id
        if 'title' not in book:
            book['title'] = book_path.stem
    return book


def process_book(lines):
    book = {'pages': []}
    counter = 0
    page = {}
    try:
        for line in lines:
            counter += 1
            if line.strip() == 'page':
                if page.keys():
                    book['pages'].append({'lines': page['lines'].copy()})
                page['lines'] = []
                key = 'page'
                value = None
            else:
                try:
                    key, value = line.strip().split('---')
                    key = key.strip()
                    value = value.strip()
                except ValueError as value_error:
                    logger.debug(f'Invalid book format: {str(value_error)}')
                    return None
            if key == 'line':
                page['lines'].append({'line': value})
            elif key == 'page':
                if 'lines' in page and page['lines']:
                    # Found page after reading several lines
                    book['pages'].append({'lines': page['lines'].copy()})
                    page['lines'] = []
                if value is not None:
                    book['pages'].append({'lines': [{'line': value}]})
            elif key == 'image':
                if 'lines' in page and page['lines']:
                    # Found page after reading several lines
                    book['pages'].append({'lines': page['lines'].copy()})
                    page['lines'] = []
                book['pages'].append({'image': value})
            else:
                book[key.strip()] = value.strip()
    except ValueError as value_error:
        logger.error(f'Invalid format on line {counter}: {str(value_error)}')
        return None
    return book


def read_file(filename):
    logger.debug(f'Reading: {filename}')
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return f.readlines()
    except FileNotFoundError:
        print(f'{filename} does not exist.')
