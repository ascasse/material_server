from datetime import datetime
import unittest
import json
import model
from model_encoder import ModelEncoder


class ModelSerializeTests(unittest.TestCase):
    def test_serialize_category(self):
        category = model.from_dict(
            model.Category,
            {"id": "1", "name": "test", "last_view": datetime(2020, 10, 5)},
        )
        json_str = json.dumps(category, cls=ModelEncoder)
        self.assertIsNotNone(json_str)

    def test_serialize_item(self):
        item = model.from_dict(
            model.Item, {"text": "Item1", "views": 3, "last_view": datetime.today()}
        )
        json_str = json.dumps(item, cls=ModelEncoder)
        self.assertIsNotNone(json_str)

    def test_serialize_item_list(self):
        items = []
        items.append(
            model.from_dict(
                model.Item, {"text": "Item1", "views": 3, "last_view": datetime.today()}
            )
        )
        items.append(
            model.from_dict(
                model.Item,
                {"text": "Item2", "views": 5, "last_view": datetime(2023, 4, 1)},
            )
        )
        json_str = json.dumps(items, cls=ModelEncoder)
        self.assertIsNotNone(json_str)
