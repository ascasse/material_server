import unittest
from pathlib import Path
from material_loader import MaterialLoader


class LoaderTest(unittest.TestCase):

    def setUp(self):
        self.test_group = {'id': 1, 'name': 'TestGroup', 'images': []}
        self.test_image = {'id': 1, 'title': 'Title1',
                           'imagefilepath': 'path1'}
        self.test_group['images'].append(self.test_image)

    def test_save_groups(self):
        loader = MaterialLoader(Path('./test'))
        loader.groups = [self.test_group]
        self.assertIsNotNone(loader)

        loader.save_groups()
        groups = loader.load_groups()

        self.assertEqual(len(groups), 1)
        self.assertTrue(groups[0]['id'] == 1)
        self.assertEqual(groups[0]['name'], 'TestGroup')
        self.assertTrue(len(groups[0]['images']) == 1)

        image = groups[0]['images'][0]
        self.assertEqual(image['id'], 1)
        self.assertEqual(image['title'], 'Title1')
        self.assertEqual(image['imagefilepath'], 'path1')

    def test_update_group(self):
        loader = MaterialLoader(Path('./test'))
        loader.groups = [self.test_group]
        self.assertIsNotNone(loader)

        self.test_group['name'] = 'new_name'

        loader.update_group(self.test_group)
        group = loader.find_group(self.test_group['id'])
        self.assertIsNotNone(group)
        self.assertEqual(group['name'], 'new_name')

    def test_load_from_dir_mixed_book_types(self):
        loader = MaterialLoader(Path('./test/data'))
        loader.load()
        self.assertEqual(len(loader.categories), 1)
        self.assertEqual(len(loader.categories[0]['books']), 4)
        self.assertEqual(len(loader.categories[0]['images']), 1)


if __name__ == "__main__":
    unittest.main()
