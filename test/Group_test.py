import unittest
import datetime

from model_old import Group


class GroupTest(unittest.TestCase):
    def test_name(self):
        group = Group("Test_group")
        self.assertEqual(group.name, "Test_group")

    def test_id(self):
        group = Group("gtest", id=34)
        self.assertEqual(group.id, 34)

    def test_images(self):
        group = Group("gtest", images=["img1"])
        self.assertEqual(len(group.images), 1)
        self.assertEqual(group.images[0], "img1")

    def test_lastseen(self):
        group = Group("gtest", lastseen=datetime.datetime.now())
        self.assertIsNotNone(group.lastseen)
        self.assertEqual(datetime.datetime.now().date(), group.lastseen.date())

    def test_invalid_lastseen(self):
        group = Group("gtest")
        self.assertRaises(TypeError, Group.__setattr__, self, "lastseen", "2019/12/20")


if __name__ == "__main__":
    unittest.main()
