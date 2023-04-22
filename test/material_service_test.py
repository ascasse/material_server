"""
    MaterialService tests
"""

from datetime import datetime as dt, timedelta
from doctest import testmod
from unittest import TestCase
from material_json_service import MaterialJsonService
from material_service import MaterialService
from model import Category
from model import Item
from sqlite_repository import SQLiteRepository


class MaterialServiceTest(TestCase):
    def __init__(self):
        super().__init__(self)
        repository = SQLiteRepository(":memory:")
        repository
        self.service = MaterialService(repository)

    def test_get_recent(self):
        """test_get_recent"""
        categories = self.service.get_recent()
        self.assertIsNotNone(categories)


# class JsonMaterialServiceTest(TestCase):
#     ''' '''
#     def setUp(self) -> None:
#         # self.service = JsonMaterialService("./test/data/db_test.json")
#         self.service = MaterialJsonService()
#         self.service.load("./test/data/db_test.json")
#         return super().setUp()

#     def test_get_categories(self):
#         categories = self.service.categories
#         self.assertIsNotNone(categories)
#         self.assertTrue(len(categories) > 0)
#         self.assertEqual(categories[0].id, 1)
#         self.assertEqual(categories[0].last_seen, dt(2020, 10, 22).date())

#     def test_get_recent(self):
#         data = [
#             Category(
#                 {
#                     "id": 1,
#                     "name": "category1",
#                     "last_seen": (dt.today() - timedelta(days=1)).date(),
#                 }
#             ),
#             Category(
#                 {
#                     "id": 2,
#                     "name": "category2",
#                     "last_seen": (dt.today() - timedelta(days=3)).date(),
#                 }
#             ),
#             Category(
#                 {
#                     "id": 3,
#                     "name": "category3",
#                     "last_seen": (dt.today() - timedelta(days=7)).date(),
#                 }
#             ),
#             Category(
#                 {
#                     "id": 4,
#                     "name": "category4",
#                     "last_seen": (dt.today() - timedelta(days=10)).date(),
#                 }
#             ),
#             Category({"id": 5, "name": "category5"}),
#         ]

#         self.service.categories = data
#         recent = self.service.get_recent()
#         self.assertIsNotNone(recent)
#         self.assertTrue(len(recent) == 3)
#         self.assertEqual([x.id for x in recent], [1, 2, 3])

#     def test_get_batch(self):
#         test_category = self.service.categories[0]
#         batch = self.service.get_batch(test_category)
#         self.assertIsNotNone(batch)

#     def test_get_complete_batch(self):
#         test_category = self.create_completed_category()
#         batch = self.service.get_batch(test_category)
#         self.assertIsNotNone(batch)
#         self.assertTrue(batch.completed)

#     def test_all_items(self):
#         items = self.service.get_all_items()
#         self.assertEqual(len(items), 17)

#     def test_update_batch(self):
#         test_category = self.service.categories[0]
#         batch = self.service.get_batch(test_category)
#         self.service.update_batch(batch)
#         self.assertEqual(test_category.items[0].views, 1)

#     def test_save_categories(self):
#         self.service.save_categories("./test/data/db_test2.json")
#         self.service.database = "./test/data/db_test.json"
#         self.service.load()

#     def create_completed_category(self):
#         """Get a category already viewed"""
#         test_category = self.service.categories[0]
#         self.service.batch_size = len(test_category.items)
#         for item in test_category.items:
#             item.views = self.service.max_views
#         return test_category
