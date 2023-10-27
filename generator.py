"""
    Builds category collection from directory content
"""

import sys
from argparse import ArgumentParser
from os import path

import logging
import json

from pathlib import Path
from typing import List

from repository import Repository
from model import Category, Item
from sqlite_repository import SQLiteRepository

logger = logging.getLogger(__name__)


class Generator:
    """Fills repository from a directory content"""

    def __init__(self, base_path: str, repository: Repository):
        self.path = Path(base_path)
        self.repository = repository

    def load_categories(self) -> List:
        return self.process_dir(self.path)

    def process_dir(self, data_path: Path) -> List:
        """Create categories for directories containing images (jpg or png)"""
        print(data_path)
        categories = []
        image_files = [
            f
            for f in data_path.iterdir()
            if (f.suffix.lower() == ".jpg" or f.suffix.lower() == ".png")
        ]
        if image_files:
            items = []
            for image in image_files:
                imagefile_path = path.relpath(str(image), self.path)
                items.append(Item(image.stem, imagefile_path))
            categories.append(Category(data_path.stem, items))
            logger.info(f"Category: {data_path.stem}")
            print(f"Items: {len(items)}")

        for directory in [d for d in data_path.iterdir() if Path.is_dir(d)]:
            categories += self.process_dir(directory)

        return categories

    def save_categories(self, categories: List):
        """Save given categories to repository"""
        for category in categories:
            self.repository.save_category(category)


def load_categories_json(model_path, hook):
    """Load categories from a json file"""
    try:
        with open(model_path, "r", encoding="utf-8") as fmodel:
            return json.load(fmodel, object_hook=hook)
    except FileNotFoundError:
        logger.info("Categories file not found.")
        return []
    # except JSONDecodeError as json_error:
    #     logger.error(f"Invalid json data: {str(json_error)}")
    #     return []
    except OSError as os_error:
        logger.error(f"Error reading data: {str(os_error)}")
        return []


def merge(old_categories: List, current: List):
    dict_categories = {}
    dict_bits = {}
    for categ in old_categories:
        dict_categories[categ.name] = categ
        for bit in categ.items:
            dict_bits[bit.imagefilepath] = bit

    for categ in current:
        if categ.name in dict_categories:
            if categ.id == 0:
                categ.id = dict_categories[categ.name].id
            for bit in categ.items:
                if bit.imagefilepath in dict_bits:
                    if bit.id == 0:
                        bit.id = dict_bits[bit.imagefilepath].id

    # logger.info("Reindex elements")
    # category_id = 1
    # bit_id = 1
    # category_ids = set([category.id for category in dict_categories.values()])
    # bit_ids = set([bit.id for bit in dict_bits.values()])
    # for category in current:
    #     if category.id == 0:
    #         while category_id in category_ids:
    #             category_id += 1
    #         category.id = category_id
    #         category_id += 1
    #     for bit in category.items:
    #         if bit.id == 0:
    #             while bit_id in bit_ids:
    #                 bit_id += 1
    #             bit.id = bit_id
    #             bit_id += 1
    # return current


def main():

    try:
        parser = ArgumentParser()
        parser.add_argument("directory", help="directory to process")
        parser.add_argument("database", help="output database")

        args = parser.parse_args()

        print(f"Processing directory: {args.directory}")
        print(f"Building database: {args.database}")

        repository = SQLiteRepository(args.database)
        repository.run_script("./Material_database.sql")
        generator = Generator(args.directory, repository)

        # Print categories info
        # found_categories = generator.load_categories()
        found_categories = generator.process_dir(args.directory)
        print(f"Found {len(found_categories)} categories")

        print("Saving to database")
        generator.save_categories(found_categories)

    except (SystemExit) as ex:
        print(ex)
        return


if __name__ == "__main__":
    sys.exit(main())

    # argparse = ArgumentParser()
    # argparse.add_argument(
    #     "-c", "--create", action="store_true", help="load material into database"
    # )
    # args = argparse.parse_args()
    # if args.create:
    #     print("Create database")
    #     run_script(Path(db_path, DATABASE), SCRIPT)
    #     # run_script(Path("e:/git/learning/material_server/", "aaaa.db3"), SCRIPT)

    #     for category in found_categories:
    #         # create_category(
    #         #     Path("e:/git/learning/material_server/", "aaaa.db3"), category
    #         # )
    #         create_category(Path(db_path, DATABASE), category)

    #     sys.exit(0)

    # print("Do nothing")
