"""
    Model tests
"""
import unittest
from datetime import datetime
from model_old import Category


class ModelTest(unittest.TestCase):
    """Model tests"""

    def test_create_category_no_date(self):
        category = Category(dict(id="1", name="test"))
        self.assertIsNone(category.lastseen)
        self.assertEqual(len(category.items), 0)

    def test_create_category_invalid_date(self):
        category = Category(dict(id="1", name="test", lastseen="112abc"))
        self.assertIsNone(category.lastseen)
        self.assertEqual(len(category.items), 0)

    def test_create_category_string_date(self):
        category = Category({"id": "1", "name": "test", "lastseen": "2020/10/05"})
        lastseen = category.lastseen
        self.assertEqual(lastseen.year, 2020)
        self.assertEqual(lastseen.month, 10)
        self.assertEqual(lastseen.day, 5)
        self.assertEqual(len(category.items), 0)

    def test_create_category(self):
        category = Category(
            {"id": "1", "name": "test", "lastseen": datetime(2020, 10, 5)}
        )
        self.assertIsNotNone(category.lastseen)
        self.assertEqual(len(category.items), 0)

    # def test_group_decoder(self):
    #     json_data = '{ "id": 1, "name": "test_group" }'
    #     group = json.loads(json_data, object_hook=group_decoder)
    #     self.assertIsNotNone(group)
    #     self.assertEqual(group.id, 1)
    #     self.assertEqual(group.name, 'test_group')

    # def test_group_decoder_date(self):
    #     json_data = '{ "id": 1, "name": "test_group", "lastseen": "2019/12/10" }'
    #     group = json.loads(json_data, object_hook=group_decoder)
    #     self.assertIsNotNone(group.lastseen)
    #     self.assertEqual(datetime.datetime(2019, 12, 10), group.lastseen)

    # def test_group_decoder_date_invalid_date(self):
    #     json_data = {"id": 1, "name": "test_group", "lastseen": "2019/14/14"}
    #     category = Category(json_data)
    #     group = json.loads(json_data, object_hook=group_decoder)
    #     self.assertIsNone(group.lastseen)

    # def test_group_decoder_images(self):
    #     json_data = '''
    #         {
    #             "id": 1,
    #             "name": "test_group",
    #             "images": [
    #                 { "id": 1, "title": "Title 1", "imagefilepath": "/path1" },
    #                 { "id": 2, "title": "Title 2", "imagefilepath": "/path2" },
    #                 { "id": 3, "title": "Title 3", "imagefilepath": "/path3" }
    #             ]
    #         }'''
    #     group = json.loads(json_data, object_hook=group_decoder)
    #     self.assertIsNotNone(group)
    #     self.assertTrue(len(group.images), 3)
    #     self.assertIsInstance(group.images[1], Bit)
    #     self.assertTrue(group.images[2].id == 3)

    # def test_category_decoder_array(self):
    #     categorylist = load_model(
    #         Path('./test/data/current.json'), category_decoder)
    #     self.assertIsNotNone(categorylist)
    #     self.assertTrue(len(categorylist) == 2)
    #     self.assertTrue(len(categorylist[0].images) == 1)
    #     self.assertTrue(len(categorylist[1].images) == 1)

    # def test_group_decoder_array(self):
    #     grouplist = load_model(
    #         Path('./test/data/groups.json'), category_decoder)
    #     self.assertIsNotNone(grouplist)
    #     self.assertTrue(len(grouplist) == 2)
    #     self.assertTrue(len(grouplist[0].images) == 1)
    #     self.assertTrue(len(grouplist[1].images) == 1)
