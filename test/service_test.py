"""
    Service test
"""

import unittest
from datetime import datetime, timedelta
from plugins.vocabulary.service import Service
import plugins.vocabulary.vocabulary_db as db


class ServiceTest(unittest.TestCase):
    """ Service tester """

    def setUp(self):
        """ Initialize service and create in-memory database."""
        self.service = Service(":memory:")
        db.run_script(self.service.db_words.connection, "test/data/test_database.sql")
        db.run_script(self.service.db_words.connection, "test/data/test_data.sql")
        # Configure service
        self.service.batch_size = 5
        self.service.max_views = 3
        self.service.refresh_rate = 3
        self.service.recent_count = 3
        # Test category
        self.category = {
            "name": "test_category",
            "lastUse": None,
            "words": [
                {"word": "word01", "views": 0},
                {"word": "word02", "views": 0},
                {"word": "word03", "views": 0},
                {"word": "word04", "views": 0},
                {"word": "word05", "views": 0},
                {"word": "word06", "views": 0},
                {"word": "word07", "views": 0},
                {"word": "word08", "views": 0},
                {"word": "word09", "views": 0},
                {"word": "word10", "views": 0},
            ],
        }

    def test_get_category(self):
        """ Expect to get one category """
        category = self.service.get_category(1)
        self.assertIsNotNone(category)
        self.assertIsNone(category["lastUse"])
        self.assertTrue(category["words"])

    def test_get_categories(self):
        """ Expect to get all categories in database """
        categories = self.service.get_categories()
        self.assertTrue(categories)
        self.assertEqual(3, len(categories))

    def test_create_category(self):
        """ Create a new category """
        category = self.service.create_category(self.category)
        self.assertEqual(4, category["id"])

    def test_update_category(self):
        category = self.service.create_category(self.category)
        category["words"].append({"word": "new_word", "lastUse": None, "views": 0})
        category["words"].pop(2)
        category["words"].pop(2)
        self.service.update_category(category)
        category = self.service.get_category(category["id"])
        self.assertTrue(len(category["words"]) == 9)

    def test_update_category_word_properties(self):
        category = self.service.create_category(self.category)
        category["words"][0]["views"] = 13
        category["words"][1]["lastUse"] = datetime.today()
        self.service.update_category(category)
        category = self.service.get_category(category["id"])
        self.assertEqual(13, category["words"][0]["views"])
        self.assertEqual(
            datetime.today().strftime("%Y-%m-%d"),
            category["words"][1]["lastUse"].strftime("%Y-%m-%d"),
        )

    def test_delete_category(self):
        pass

    def test_update_views(self):
        recent = self.service.get_recent()
        batch = recent[0]
        batch = self.service.update_views(batch)
        views = [w["views"] for w in batch["words"]]
        uses = [w["lastUse"] for w in batch["words"]]
        self.assertEqual(views[1:], views[:-1])
        self.assertEqual(uses[1:], uses[:-1])
        self.assertEqual(
            batch["lastUse"].split()[0], datetime.today().strftime("%Y-%m-%d")
        )

    def test_get_recent(self):
        """Expect two batches with batch_size elements."""
        recent = self.service.get_recent()
        self.assertEqual(2, len(recent))

    def test_build_batch_small_category(self):
        """ Expect to return all the words in the category """
        self.category["id"] = 7
        del self.category["words"][self.service.batch_size - 1 :]
        batch = self.service.build_batch_from_category(self.category)
        self.assertEqual(len(batch["words"]), len(self.category["words"]))

    def test_build_batch_views_below_limit(self):
        """ Expect to return batch_size words from the category.
            First word in the batch is the first word in the sorted category
        """
        self.category["id"] = 7
        for i in range(10):
            self.category["words"][i]["id"] = i
        batch = self.service.build_batch_from_category(self.category)
        self.assertEqual(len(batch["words"]), self.service.batch_size)
        self.assertEqual(batch["words"][0]["id"], self.category["words"][0]["id"])

    def test_build_batch_iterations(self):
        """ Expect to build 4 batches before completed.
        """

        # Create and initialize category for test
        for i in range(4):
            self.category["words"][i]["views"] = self.service.max_views
        for i in range(4, 7):
            self.category["words"][i]["views"] = self.service.max_views - 1
        category = self.service.create_category(self.category)

        # Batch 1
        batch = self.service.build_batch_from_category(category)
        self.assertEqual(len(batch["words"]), self.service.batch_size)
        self.assertEqual(batch["words"][0]["id"], category["words"][3]["id"])
        self.assertEqual([3, 2, 2, 2, 0], [w["views"] for w in batch["words"]])

        updated = self.service.update_views(batch)
        self.assertEqual([4, 3, 3, 3, 1], [w["views"] for w in updated["words"]])

        # Batch 2
        batch = self.service.build_batch_from_category_id(category["id"])
        self.assertEqual(len(batch["words"]), self.service.batch_size)
        self.assertEqual([3, 3, 1, 0, 0], [w["views"] for w in batch["words"]])

        updated = self.service.update_views(batch)
        self.assertEqual([4, 4, 2, 1, 1], [w["views"] for w in updated["words"]])

        # Batch 3
        batch = self.service.build_batch_from_category_id(category["id"])
        self.assertEqual(len(batch["words"]), self.service.batch_size)
        self.assertEqual([3, 3, 2, 1, 1], [w["views"] for w in batch["words"]])

        updated = self.service.update_views(batch)
        self.assertEqual([4, 4, 3, 2, 2], [w["views"] for w in updated["words"]])

        # Batch 4
        batch = self.service.build_batch_from_category_id(category["id"])
        self.assertEqual(len(batch["words"]), self.service.batch_size)
        self.assertEqual([3, 3, 3, 2, 2], [w["views"] for w in batch["words"]])

        updated = self.service.update_views(batch)
        self.assertEqual([4, 4, 4, 3, 3], [w["views"] for w in updated["words"]])

        # Batch 5
        batch = self.service.build_batch_from_category_id(category["id"])
        self.assertTrue(batch["completed"])

    def test_datetime(self):
        """ Verify type of datetime type values is preserved """
        self.category["lastUse"] = datetime.now()
        self.category["words"][0]["lastUse"] = datetime.now()
        self.assertEqual(type(self.category["lastUse"]), datetime)
        self.assertEqual(type(self.category["words"][0]["lastUse"]), datetime)
        category = self.service.create_category(self.category)
        self.assertEqual(type(category["lastUse"]), datetime)
        self.assertEqual(type(category["words"][0]["lastUse"]), datetime)


def days_old(days):
    """ Return a date a given number of days before today."""
    return datetime.today() - timedelta(days=-days)
