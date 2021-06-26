import sys
from os import environ, path
from argparse import ArgumentParser
import logging
import json

from pathlib import Path
from dotenv import load_dotenv
from material_db import run_script, create_category
from typing import List

from model import Category, Item

logger = logging.getLogger(__name__)


class Generator:
    """Construye una lista de categorías clasificando el contenido de un directorio."""

    def __init__(self, base_path):
        self.path = Path(base_path)

    def generate(self) -> List:
        return self.process_dir(self.path)

    def process_dir(self, data_path: str) -> List:
        """Build categories for directories containing images (jpg or png)"""
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
                items.append(
                    Item(
                        image.stem[:60] if len(image.stem) > 60 else image.stem,
                        imagefile_path,
                    )
                )
            categories.append(Category(data_path.stem, items))
            logger.info(f"Category: {data_path.stem}")

        for directory in [d for d in data_path.iterdir() if Path.is_dir(d)]:
            categories += self.process_dir(directory)

        return categories


def load_model(model_path, hook):
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


def merge(old_categories: List, current):
    dict_categories = {}
    dict_bits = {}
    for category in old_categories:
        dict_categories[category.name] = category
        for bit in category.items:
            dict_bits[bit.imagefilepath] = bit

    for category in current:
        if category.name in dict_categories:
            if category.id == 0:
                category.id = dict_categories[category.name].id
            for bit in category.items:
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


if __name__ == "__main__":

    load_dotenv(verbose=True)

    PATH = environ.get("database_path", "./")
    DATABASE = environ.get("database", None)
    SCRIPT = environ.get("script_create_database")

    BITS = environ.get("bits", ".")

    # Create a Generator for the given path
    generator = Generator(Path(BITS))

    # Print categories info
    found_categories = generator.generate()
    print(found_categories)

    argparse = ArgumentParser()
    argparse.add_argument(
        "-c", "--create", action="store_true", help="load material into database"
    )
    args = argparse.parse_args()
    if args.create:
        print("Create database")
        run_script(Path(PATH, DATABASE), SCRIPT)
        # run_script(Path("e:/git/learning/material_server/", "aaaa.db3"), SCRIPT)

        for category in found_categories:
            # create_category(
            #     Path("e:/git/learning/material_server/", "aaaa.db3"), category
            # )
            create_category(Path(PATH, DATABASE), category)

        sys.exit(0)

    print("Do nothing")
