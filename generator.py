from os import environ, path
import logging
import json

from json.decoder import JSONDecodeError
from pathlib import Path
from dotenv import load_dotenv

from model import Category, Bit, category_encoder, category_decoder, group_decoder



logger = logging.getLogger(__name__)


class Generator:
    def __init__(self, base_path):
        self.path = Path(base_path)
        self.categories = []
        self.groups = []

        self.plugins = []

        # Load previous categories
        old_categories = load_model(self.path.joinpath("categories.json"), category_decoder)
        logger.info(f'Loaded previously saved categories: {len(old_categories)}')

        # Load current categories in file system
        self.generate()
        logger.info('Loaded categories from file system: {len(current)}')

        # Merge previous category data with newly loaded categories
        if old_categories:
            self.categories = merge(old_categories, self.categories)
        else:
            self.index_categories()

        if not self.categories:
            return
        logger.info('Save new categories')
        self.save_categories()

        self.load_groups()

    def generate(self):
        self.process_dir(self.path)

    def process_dir(self, data_path):
        '''
        Build categories for directories containing images (jpg or png)
        '''
        image_files = [f for f in data_path.iterdir() if (f.suffix.lower() == '.jpg' or f.suffix.lower() == '.png')]
        if image_files:
            bits = []
            for image in image_files:
                imagefile_path = path.relpath(str(image), self.path)
                bit = Bit(image.stem[:60] if len(image.stem) > 60 else image.stem, imagefile_path)
                bits.append(bit)
            self.categories.append(Category(data_path.stem, images=bits))
            logger.info(f'Category: {data_path.stem}')

        for directory in [d for d in data_path.iterdir() if Path.is_dir(d)]:
            self.process_dir(directory)

    def load_groups(self):
        try:
            with open(self.path.joinpath('groups.json'), 'r', encoding='utf-8') as fp:
                data = fp.read()
                self.groups = json.loads(data, object_hook=group_decoder)
        except FileNotFoundError:
            self.groups = []

    def add_group(self, group):
        self.ensure_group_name_unique(group)
        self.groups.append(group)

    def get_bits(self):
        bits = []
        for category in self.categories:
            bits.append(category.images)
        return bits

    def get_category(self, category_id):
        for category in self.categories:
            if category.id == category_id:
                return category
        return None

    def get_group(self, group_id):
        for group in self.groups:
            if group.id == group_id:
                return group
        return None

    def get_bit(self, bit_id):
        for category in self.categories:
            for bit in category.images:
                if bit.id == bit_id:
                    return bit
        return None

    def get_recent_groups(self):
        return self.groups

    def category_count(self):
        return len(self.categories)

    def group_count(self):
        return len(self.groups)

    def bit_count(self):
        count = 0
        for category in self.categories:
            count += len(category.images)
        return count

    def create_group(self, json_dict):
        try:
            group = group_decoder(json_dict)
        except Exception as e:
            logger.error(f'create_group: {str(e)}')
            raise

        self.ensure_group_name_unique(group)
        self.index_group(group)
        self.groups.append(group)

        self.save_groups()
        return group

    def update_group(self, json_dict):
        try:
            group = group_decoder(json_dict)
        except Exception as e:
            logger.error(f'update_group: {str(e)}')
            raise

        found_group = self.get_group(group.id)
        if found_group is None:
            logger.error(f'update_group: Not found')
            raise Exception("Not found")

        if found_group.name != group.name:
            self.ensure_group_name_unique(group)
            found_group.name = group.name
        found_group.images = group.images

        self.save_groups()
        return group

    # def update_group(self, json_group):
    #     try:
    #         group = json.loads(json_group, object_hook=group_decoder)
    #     except Exception as e:
    #         logger.error(f'update_group: {str(e)}')
    #         raise

    #     found_group = self.get_group(group.id)
    #     if found_group is None:
    #         logger.error(f'update_group: Not found')
    #         raise Exception("Not found")

    #     if found_group.name != group.name:
    #         self.ensure_group_name_unique(group)
    #         found_group.name = group.name
    #     found_group.images = group.images

    #     self.save_groups()
    #     return group

    def index_categories(self):
        '''
            Set an id for every category and image.
            Category and image ids are 0 after processing file system. 
        '''
        category_id = 0
        bit_id = 0
        for category in self.categories:
            category_id += 1
            category.id = category.id = category_id
            for bit in category.images:
                bit_id += 1
                bit.id = bit_id

    def index_group(self, group):
        if group.id != 0:
            return group
        new_id = 1
        ids = set([group.id for group in self.groups])
        while new_id in ids:
            new_id += 1
        group.id = new_id
        return group

    def ensure_group_name_unique(self, group):
        names = set([group.name for group in self.groups])
        if group.name in names:
            raise ValueError("Group name already exists.")

    def __str__(self):
        json_string = json.dumps(self.categories, default=category_encoder, ensure_ascii=False).encode('utf-8')
        return json_string.decode()

    def save_categories(self):
        self.save_as_json(self.path.joinpath('categories.json'), self.categories)

    def save_groups(self):
        self.save_as_json(self.path.joinpath('groups.json'), self.groups)

    def save_as_json(self, filepath, data):
        with open(filepath, 'w', encoding='utf-8') as fdata:
            json.dump(data, fdata, indent=2, default=category_encoder, ensure_ascii=False)


def load_model(model_path, hook):
    try:
        with open(model_path, "r", encoding='utf-8') as fmodel:
            return json.load(fmodel, object_hook=hook)
    except FileNotFoundError:
        logger.info(f'Categories file not found.')
        return []
    except JSONDecodeError as json_error:
        logger.error(f'Invalid json data: {str(json_error)}')
        return []
    except OSError as os_error:
        logger.error(f'Error reading data: {str(os_error)}')
        return []


def merge(old_categories, current):
    dict_categories = {}
    dict_bits = {}
    for category in old_categories:
        dict_categories[category.name] = category
        for bit in category.images:
            dict_bits[bit.imagefilepath] = bit

    for category in current:
        if category.name in dict_categories:
            if category.id == 0:
                category.id = dict_categories[category.name].id
            for bit in category.images:
                if bit.imagefilepath in dict_bits:
                    if bit.id == 0:
                        bit.id = dict_bits[bit.imagefilepath].id

    logger.info('Reindex elements')
    category_id = 1
    bit_id = 1
    category_ids = set([category.id for category in dict_categories.values()])
    bit_ids = set([bit.id for bit in dict_bits.values()])
    for category in current:
        if category.id == 0:
            while category_id in category_ids:
                category_id += 1
            category.id = category_id
            category_id += 1
        for bit in category.images:
            if bit.id == 0:
                while bit_id in bit_ids:
                    bit_id += 1
                bit.id = bit_id
                bit_id += 1
    return current


if __name__ == "__main__":

    load_dotenv(verbose=True)
    MATERIAL = environ.get('MATERIAL', '.')
    PATH = Path(MATERIAL).joinpath('bits')

    # Create a Generator for the given path
    generator = Generator(PATH)

    # Print categories info
    print(generator)

    # Save categories info to a json file
    generator.save_categories()
