'''
    loader.py
    Classification of elements found in the file system.
'''

import logging
import json
from plugins.books.book_loader import load_book, load_json_book


logger = logging.getLogger(__name__)


class MaterialLoader:
    '''
    Categorizes all the GIF files found in a given path.

    Builds an array of categories.
    Each category is defined by:
        - id:   sequentially asigned when found
        - name: directory relative path to the base: dir1_dir2_dir
        - images: gifs found in the directory
    Every image is a dictionary containing id, name and path keys.

    '''

    def __init__(self, basepath):
        logger.debug(f'Loading from {basepath}')
        self.path = basepath
        self.categories = []
        self.counter = 0
        self.category_counter = 0
        self.groups = []
        self.groups_path = self.path.joinpath('groups.json')

    def load(self):
        ''' Launches a recursive search '''
        if not self.path.exists():
            return self.categories
        self.category_counter = 0
        self.counter = 1
        self.categories = []
        self.load_from_dir(self.path)
        return self.categories

    def load_from_dir(self, working_dir):
        ''' Parse directory looking for books and images '''
        elements = []
        data = [
            item for item in working_dir.iterdir()
            if (item.is_file() and item.suffix in ['.gif', '.txt', '.json']) or item.is_dir()
        ]
        for item in data:
            if item.is_dir():
                self.load_from_dir(item)
            elif item.suffix == '.txt':
                book_dict = load_book(self.counter, item)
                if book_dict is not None:
                    elements.append(book_dict)
                    self.counter += 1
            elif item.suffix == '.json':
                book_dict = load_json_book(self.counter, item)
                if book_dict is not None:
                    elements.append(book_dict)
                    self.counter += 1
            else:
                elements.append(
                    {"id": self.counter, "title": item.stem, "imagefilepath": str(item)})
                self.counter += 1
        if elements:
            category_name = '_'.join(working_dir.relative_to(self.path).parts)
            if not category_name:
                category_name = self.path.stem
            self.category_counter += 1
            category = self.build_category(
                self.category_counter, category_name, elements)
            self.categories.append(category)

    def build_category(self, category_id, name, elements):
        category = {
            "id": category_id,
            "name": name,
            "images": [],
            "books": []}
        for element in elements:
            if "imagefilepath" in element:
                category['images'].append(element)
            else:
                category['books'].append(element)
        return category

    def get_categories(self):
        ''' Current categories '''
        return self.categories

    def get_element_count(self, element_type):
        category_count = 0
        element_count = 0
        for category in self.categories:
            count = len(category[element_type])
            if count:
                category_count += 1
                element_count += count
        return category_count, element_count

    def find_category(self, category_id):
        for category in self.categories:
            if category['id'] == category_id:
                return category
        return None

    def find_image(self, img_id):
        for category in self.categories:
            for img in category['images']:
                if img['id'] == img_id:
                    return img
        return None

    def find_book(self, book_id):
        for category in self.categories:
            for book in category['books']:
                if book['id'] == book_id:
                    return category, book
            for img in category['images']:
                if img['id'] == book_id:
                    return category, img
        return (None, None)

    def load_groups(self):
        try:
            with open(str(self.groups_path), 'r', encoding='utf-8') as file_handler:
                data = file_handler.read()
                self.groups = json.loads(data)
        except FileNotFoundError:
            self.groups = []
        return self.groups

    def save_groups(self):
        try:
            with open(str(self.groups_path), 'w', encoding='utf-8') as file_handler:
                file_handler.write(json.dumps(self.groups))
        except OSError as os_error:
            logger.error(os_error)

    def find_group(self, group_id):
        for group in self.groups:
            if group['id'] == group_id:
                return group
        return None

    def update_group(self, updated_group):
        to_update = self.find_group(updated_group['id'])
        if to_update is None:
            logger.error('Update_group: Not found')
            return

        to_update['name'] = updated_group['name']
        to_update['images'].clear()
        for img in updated_group['images']:
            to_update['images'].append(img)

        self.save_groups()
        return to_update

    def create_group(self, new_group):
        self.ensure_group_name_unique(new_group)
        self.index_group(new_group)
        self.groups.append(new_group)
        self.save_groups()
        return new_group

    def index_group(self, group):
        if group['id'] != 0:
            return group
        new_group_id = 1
        ids = set([group['id'] for group in self.groups])
        while new_group_id in ids:
            new_group_id += 1
        group['id'] = new_group_id
        return group

    def ensure_group_name_unique(self, group):
        names = set([group['name'] for group in self.groups])
        if group['name'] in names:
            raise ValueError("Group name already exists.")
