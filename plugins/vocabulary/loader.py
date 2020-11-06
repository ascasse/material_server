"""
    Loader class for voacbulary learning material
"""

import os
import logging
import json
import re
from pathlib import Path

LOGGER = logging.getLogger(__name__)


class Loader:
    """
        Load vocabulary data from a location
    """

    def __init__(self, counter, location):
        super().__init__()
        self.counter = counter
        self.word_categories = []
        self.location = Path(location)
        self.pattern = re.compile(r"([\w]+)(?=,|\))|([\w]+)")
        # self.pattern = re.compile(r"([a-zA-Záéíóú]+)(?=,|\))|([a-zA-Záéíóú]+)")

    def load_from_location(self, location):
        """
            Load all the vocabulary files under the given location
            Parameters:
                location: Path to look for files
        """
        voc = []
        for root, _, filenames in os.walk(location):
            for name in filenames:
                loaded = []
                if name.endswith(".json"):
                    loaded = self.load_json(os.path.join(root, name))
                if name.endswith(".txt"):
                    loaded = self.load_text(Path.joinpath(Path(root), name))
                for item in loaded:
                    voc.append(item)
        return voc

    def load_text(self, filepath):
        """ Load data from plain text file
            Expects lines of the form
            category: word1, word2, ..., word
        """
        voc = []
        lines = read_lines(filepath)
        for line in lines:
            parts = line.split(":")
            if len(parts) != 2:
                return []
            words = parts[1].replace(" ", "")
            if not re.match(self.pattern, words):
                return []
            voc.append({"category": parts[0].strip(), "words": words})
        return voc

    def load_json(self, filepath):
        """ Load data from json file """
        voc = []
        try:
            LOGGER.debug(filepath)
            voc_dict = json.loads(read_all(filepath))
            if "Vocabulary" in voc_dict:
                for item in voc_dict["Vocabulary"]:
                    for key in item.keys():
                        voc.append({"category": key, "words": item[key]})
            return voc
            # return voc_dict["Vocabulary"]
        except OSError as os_error:
            print(os_error)
        except TypeError as type_error:
            LOGGER.error(f"{type_error}")
        except json.decoder.JSONDecodeError as json_error:
            print(f"{filepath} {json_error}")
        return {}

    # def process_line(self, line, category, element_id):
    #     return {"id": element_id, "cat": category, "words": line}


def read_lines(filename):
    """ Read data file as lines"""
    try:
        with open(filename, "r", encoding="utf-8") as input_file:
            return input_file.readlines()
    except FileNotFoundError:
        LOGGER.error(f"{filename} does not exist.")


def read_all(filename):
    """ Read all file content """
    try:
        with open(filename, "r", encoding="utf-8") as input_file:
            return input_file.read()
    except FileNotFoundError:
        LOGGER.error(f"{filename} does not exist.")
