import unittest
import json
import os
import logging
from pathlib import Path

from generator import Generator

logger = logging.getLogger(__name__)

PATH = "e:/material/bits"


class GeneratorTest(unittest.TestCase):
    def test_no_categories(self):
        Path.mkdir(Path("./test/no_data"))
        generator = Generator("./test/no_data")
        # generator = Generator(".")
        self.assertIsNotNone(generator)
        categories = generator.load_categories()
        Path.rmdir(Path("./test/no_data"))
        self.assertTrue(len(categories) == 0)

    def test_load_categories(self):
        generator = Generator(PATH)
        categories = generator.load_categories()
        self.assertIsNotNone(categories)
        self.assertTrue(categories)

        self.assertTrue(categories[0].id == 0)
        self.assertTrue(categories[0].items)
        self.assertTrue(categories[0].items[0].id == 0)
        self.assertTrue(categories[0].items[0].views == 0)
        self.assertTrue(categories[0].items[0].last_view is None)

    # def test_update_group(self):
    #     generator = Generator("./test")
    #     generator.groups.append(
    #         Group(1, "Group1", items=[Item("Bit1", id=1, image="path1")])
    #     )

    #     json_dict = {
    #         "name": "New_name",
    #         "id": 1,
    #         "items": [{"title": "Bit3", "id": 3, "imagefilepath": "path3"}],
    #     }
    #     group = generator.update_group(json_dict)

    #     self.assertIsNotNone(group)
    #     self.assertEqual(group.id, 1)
    #     self.assertEqual(group.name, "New_name")
    #     self.assertTrue(len(group.items) == 1)
    #     self.assertEqual(group.items[0].id, 3)

    @classmethod
    def tearDownClass(cls):
        try:
            if os.path.exists("./test/groups.json"):
                os.remove("./test/groups.json")
        except Exception as ex:
            logger.error(str(ex))
