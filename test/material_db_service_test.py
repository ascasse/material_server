import unittest
from material_db_service import MaterialDbService
from model import Category, Item


class MaterialDbServiceTest(unittest.TestCase):
    def setUp(self):
        """Initialize service and create in-memory database."""
        # self.service = MaterialDbService(":memory:")
        # self.service.create_database(":memory:")

        self.service = MaterialDbService("test_db.db3")
        self.service.create_database("test_db.db3")

        category = Category("Test", [])
        category.items = [
            Item("Item1"),
            Item("Item2"),
            Item("Item3"),
            Item("Item4"),
        ]
        self.service.add_category(category)

    def test_get_recent(self):
        categories = self.service.get_recent()
        self.assertIsNotNone(categories)
        self.assertIsNotNone(categories[0]["LastUse"])

    def test_update_batch(self):
        recent = self.service.get_recent()
        self.service.update_batch(recent(0))
        recent = self.service.get_recent()
        self.assertIsNotNone(recent[0]["LastUse"])
