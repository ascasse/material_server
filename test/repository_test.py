import datetime as dt
import unittest
from model import Category, Item

from sqlite_repository import Repository


class RepositoryTest(unittest.TestCase):
    def setUp(self):
        self.repository = Repository(":memory:")
        self.repository.run_script("Material_database.sql")

    def test_all_categories(self):
        category = Category(name="Banderas", last_view=dt.date.today())
        self.repository.save_category(category)

        categories = self.repository.all_categories()
        self.assertIsNotNone(categories)
        self.assertEqual(1, len(categories))

        categ = categories[0]
        self.assertEqual("Banderas", categ["name"])
        self.assertEqual(
            dt.date.today(),
            dt.datetime.strptime(categ["lastuse"], "%Y-%m-%d").date(),
        )

    def test_all_items(self):
        items = [
            ("item1", 1, dt.datetime.today(), "image1", 1),
            ("item2", 2, dt.datetime.today() - dt.timedelta(days=1), "image2", 1),
            ("item3", 3, dt.datetime.today() - dt.timedelta(days=2), "image3", 1),
        ]
        self.repository.cur.executemany(
            "insert into Items (Text, Views, LastUse, Image, CategoryId) values (?, ?, ?, ?, ?)",
            items,
        )

        found = self.repository.all_items()
        self.assertIsNotNone(found)
        self.assertEqual(3, len(found))

    def test_save_category(self):

        items = [
            Item(text="item1", views=1, last_view=dt.datetime.today()),
            Item(text="item2", views=2, last_view=dt.datetime.today()),
        ]
        category = Category(name="Banderas", items=items, last_view=dt.date.today())
        self.repository.save_category(category)

        categories = self.repository.all_categories()
        categ = categories[0]

        self.assertEqual("Banderas", categories[0]["name"])
        self.assertEqual(
            dt.date.today(),
            dt.datetime.strptime(categories[0]["lastuse"], "%Y-%m-%d").date(),
        )

        rows = self.repository.all_items()

        category_id = categ["id"]
        items = [it for it in rows if it["CategoryId"] == category_id]
        self.assertEqual("item1", items[0]["text"])
