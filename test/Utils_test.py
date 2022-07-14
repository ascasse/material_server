import unittest
import json
import logging
import os

from pathlib import Path
from json.decoder import JSONDecodeError
from generator import merge
from model_old import category_decoder

logger = logging.getLogger(__name__)


class UtilsTest(unittest.TestCase):
    def test_merge_add_bits(self):
        current_data = """
            [
                { "id": 1, "name": "Cat1", "images" : [
                    { "id": 1, "title": "tit1", "imagefilepath": "path1"},
                    { "id": 3, "title": "tit3", "imagefilepath": "path3"}, 
                    { "id": 0, "title": "tit2", "imagefilepath": "path2"}]
                }
            ]
        """
        old_data = """
            [
                { "id": 1, "name": "Cat1", "images" : [
                    { "id": 1, "title": "tit1", "imagefilepath": "path1"},
                    { "id": 3, "title": "tit3", "imagefilepath": "path3"}]
                }
            ]        
        """

        current = json.loads(current_data, object_hook=category_decoder)
        old = json.loads(old_data, object_hook=category_decoder)
        categories = merge(old, current)
        self.assertTrue(len(categories) == 1)
        newbit = [bit for bit in categories[0].images if bit.id == 2][0]
        self.assertIsNotNone(newbit)
        self.assertTrue(newbit.id == 2)

    def test_merge_add_category(self):
        current_data = """
            [
                { "id": 1, "name": "Cat1", "images" : [ { "id": 1, "title": "tit1", "imagefilepath": "path1"}] },                
                { "id": 3, "name": "Cat3", "images" : [ { "id": 3, "title": "tit3", "imagefilepath": "path3"}] },
                { "id": 0, "name": "Cat2", "images" : [ { "id": 0, "title": "tit2", "imagefilepath": "path2"}] }
            ]            
        """
        old_data = """
            [
                { "id": 1, "name": "Cat1", "images" : [ { "id": 1, "title": "tit1", "imagefilepath": "path1"}] },
                { "id": 3, "name": "Cat3", "images" : [ { "id": 3, "title": "tit3", "imagefilepath": "path3"}] }
            ]        
        """

        current = json.loads(current_data, object_hook=category_decoder)
        old = json.loads(old_data, object_hook=category_decoder)
        categories = merge(old, current)
        self.assertTrue(len(categories) == 3)
        newcat = [category for category in categories if category.id == 2][0]
        self.assertTrue(newcat)
        self.assertTrue(newcat.images[0].id == 2)
