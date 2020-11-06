""" vocabulary_db test module
"""

import unittest
from datetime import datetime, timedelta
import plugins.vocabulary.vocabulary_db as voc
import plugins.vocabulary.process_db as dbproc


class VocabularyDbTest(unittest.TestCase):
    def setUp(self):
        voc.set_database("test.db")
        connection = voc.open_connection()
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS Categories")
        cursor.execute("DROP TABLE IF EXISTS Words")
        connection.commit()
        connection.close()

    def test_select_categories_empty_table(self):
        """ Expected empty result """
        categories = voc.select_categories()
        self.assertFalse(categories)

    def test_select_categories(self):
        """ Expected 1 category found """
        voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        categories = voc.select_categories()
        self.assertEqual(len(categories), 1)

    def test_select_category(self):
        """ Expected 1 row found """
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertEqual(category_id, 1)

        found_category = voc.select_category(category_id)
        self.assertIsNotNone(found_category)
        self.assertEqual(found_category["name"], "Test")

    def test_select_category_non_existing(self):
        found_category = voc.select_category(1)
        self.assertIsNone(found_category)

    def test_create_category(self):
        category_id = voc.create_category(
            {
                "name": "Test",
                "lastUse": datetime.today().strftime("%Y-%m-%d"),
                "words": [{"word": "abcd"}, {"word": "efgh"}],
            }
        )
        self.assertIsNotNone(category_id)
        self.assertEqual(category_id, 1)
        category = voc.select_category(1)
        self.assertEqual(datetime.today().strftime("%Y-%m-%d"), category["lastUse"])

    def test_create_category_default(self):
        """ Test category creation with default values. """
        category_id = voc.create_category({"name": "Test"})

        category = voc.select_category(category_id)
        self.assertEqual(category["id"], 1)
        self.assertEqual(category["name"], "Test")
        self.assertEqual(category["lastUse"], None)

    def test_duplicated_category(self):
        """ Insert duplicated category. Expected exception """
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertTrue(category_id is not None)

        category = {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        expected_message = "UNIQUE constraint failed: Categories.name"
        with self.assertRaises(Exception, msg=expected_message) as error:
            voc.create_category(category)

        self.assertEqual(error.exception.args[0], expected_message)

    def test_delete_category(self):
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertTrue(category_id is not None)
        voc.delete_category(category_id)
        category = voc.select_category(category_id)
        self.assertIsNone(category)

    def test_words_for_category_no_words(self):
        """ Words for empty category. Expected empty array """
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        words = voc.get_words_for_category(category_id)
        self.assertIsNotNone(words)
        self.assertFalse(words)

    def test_add_words(self):
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        self.assertTrue(category_id is not None)
        words = ("word1", "word2", "word3", "word4", "word5")
        voc.add_words(1, words)

        found_words = voc.get_words_for_category(category_id)
        self.assertTrue(found_words)

    def test_merge_words(self):
        actual_data = [(1, "entrada"), (2, "viajero"), (3, "mosca"), (4, "merced")]
        new_words = ["viajero", "tranvía", "solapa"]

        actual_words = [x[1] for x in actual_data]
        merged_words = voc.merge_words(actual_words, new_words)

        merged_data = [item for item in actual_data for x in merged_words if x in item]
        print(merged_data)

        self.assertTrue(len(merged_words) == 3)
        self.assertIn("viajero", merged_words)
        self.assertIn("tranvía", merged_words)
        self.assertIn("solapa", merged_words)

    def test_update_words(self):
        actual_data = [(1, "entrada"), (2, "viajero"), (3, "mosca"), (4, "merced")]
        new_words = ["viajero", "tranvía", "solapa"]

        to_keep, to_delete, to_add = voc.update_words(actual_data, new_words)
        print()
        print(f"to keep:   {to_keep}")
        print(f"to delete: {to_delete}")
        print(f"to add: {to_add}")
        self.assertEqual(len(to_keep), 1)
        self.assertEqual(to_keep[0][1], "viajero")
        self.assertEqual(len(to_delete), 3)
        self.assertEqual(len(to_add), 2)

    def test_update_words_views(self):
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime.today().strftime("%Y-%m-%d")}
        )
        voc.add_words(category_id, ("a", "b", "c", "d"))
        words = voc.get_words_for_category(category_id)
        self.assertTrue(words)
        dbproc.update_words_view((2, 4))
        words = voc.get_words_for_category(category_id)
        self.assertEqual(1, words[1]["views"])

    def test_update_category_batch(self):
        # category_id = voc.create_category({"name": "Test", "lastUse": "2020-01-01"})
        category_id = voc.create_category(
            {"name": "Test", "lastUse": datetime(2020, 1, 1)}
        )
        voc.add_words(category_id, ("a", "b", "c", "d"))
        words = voc.get_words_for_category(category_id)
        self.assertTrue(words)

        dbproc.update_category_batch(1, (2, 4))
        words = voc.get_words_for_category(category_id)
        self.assertEqual(1, words[1]["views"])
        self.assertEqual(datetime.today().strftime("%Y-%m-%d"), words[1]["lastUse"])

    def test_dates(self):
        """ Verify datetime usage """
        now = datetime.today()
        category_id = voc.create_category({"name": "Test", "lastUse": now})
        self.assertIsNotNone(category_id)

        category = voc.select_category(category_id)
        print(str(category["lastUse"]))
        self.assertEqual(str(now), category["lastUse"])

    # def test_get_recent(self):
    #     voc.create_category({"name": "Test1", "lastUse": datetime.now()})
    #     voc.create_category(
    #         {"name": "Test2", "lastUse": datetime.now() + timedelta(days=-2)}
    #     )
    #     voc.create_category(
    #         {"name": "Test3", "lastUse": datetime.now() + timedelta(days=-4)}
    #     )
    #     voc.create_category(
    #         {"name": "Test4", "lastUse": datetime.now() + timedelta(days=-6)}
    #     )
    #     voc.create_category(
    #         {"name": "Test5", "lastUse": datetime.now() + timedelta(days=-8)}
    #     )

    #     categories = dbproc.get_recent()
    #     self.assertTrue(categories)

