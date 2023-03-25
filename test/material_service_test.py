"""
    MaterialService tests
"""


from unittest import TestCase

from material_service import MaterialService
from model import Category, Item
from sqlite_repository import SQLiteRepository


class MaterialServiceTest(TestCase):
    """MaterialServiceTest"""

    @classmethod
    def setUpClass(cls) -> None:
        cls.repository = SQLiteRepository(db_location=":memory:")
        cls.service = MaterialService(cls.repository)
        return super().setUpClass()

    def setUp(self) -> None:
        self.repository.run_script("./Material_database.sql")
        # Create a collection of categories for testing
        # Odd categories are bits and even ones are vocabulary
        test_categories = [
            Category(
                name=f"category{m:02}",
                type=m % 2,
                items=[
                    Item(text=f"item{n:02}")
                    for n in range(10 * (m - 1) + 1, 10 * m + 1)
                ],
            )
            for m in range(1, 11)
        ]

        # Populate database
        for category in test_categories:
            self.repository.save_category(category)

    def test_get_recent(self):
        """test_get_recent"""
        categories = self.service.get_recent()
        self.assertIsNotNone(categories)
        self.assertEqual(self.service.recent_count, len(categories))
        self.assertEqual(self.service.batch_size, len(categories[0].items))

    def test_get_category(self):
        category = self.service.get_category(1)

        self.assertIsNotNone(category)
        self.assertEqual(1, category.id)
        self.assertEqual("category01", category.name)
        self.assertEqual(0, category.type)
        self.assertEqual(10, len(category.items))

        category = self.service.get_category(2)
        self.assertEqual(1, category.type)

    def test_update_batch(self):
        """test_update_batch"""
        categories = self.service.get_recent()
        batch = categories[0]
        self.service.update_batch(batch)

        categories = self.service.get_recent()
        batch = categories[0]
        self.assertIsNotNone(batch.last_view)
        self.assertEqual(1, batch.items[0].views)

    def test_get_batch(self):
        category = self.service.get_category(1)

        batch = self.service.get_batch(category)
        self.assertIsNotNone(batch)
        self.assertEqual(1, batch.id)
        self.assertEqual(self.service.batch_size, len(batch.items))
