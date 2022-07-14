"""
    MaterialDbService tests
"""
import unittest
from datetime import datetime as dt
from material_db_service import MaterialDbService
from model import Category, Item


class MaterialDbServiceTest(unittest.TestCase):
    """MaterialDbService tests"""

    def setUp(self):
        # """Initialize service and create in-memory database."""
        # self.service = MaterialDbService(":memory:")
        # self.service.create_database(":memory:")

        self.service = MaterialDbService("test_db.db3")
        self.service.create_database("test_db.db3")

        category = Category("Test", [], dt.today)
        category.items = [
            Item("Item1"),
            Item("Item2"),
            Item("Item3"),
            Item("Item4"),
        ]
        self.service.add_category(category)

    def test_get_recent(self):
        """Get recent categories"""
        categories = self.service.get_recent()
        self.assertIsNotNone(categories)
        self.assertIsNotNone(categories[0]["LastUse"])

    def test_update_batch(self):
        recent = self.service.get_recent()
        result = self.service.update_batch(recent[0])
        self.assertTrue(result)
        recent = self.service.get_recent()

        self.assertIsNotNone(recent[0]["LastUse"])
        last_use = recent[0]["LastUse"]
        dt_last_use = dt.strptime(last_use, "%Y/%m/%d")
        self.assertEqual(dt_last_use.date(), dt.today().date())

        for bit in recent[0]["Items"]:
            self.assertEqual(
                bit["LastUse"], str(dt.today().date().strftime("%Y/%m/%d"))
            )
            self.assertEqual(bit["Views"], 1)
