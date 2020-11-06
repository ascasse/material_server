"""
    Teaching vocabulary module
"""
import logging
from os import environ
from pathlib import Path
import json
from flask import Blueprint, jsonify, make_response, abort, request

from material_plugin import MaterialPlugin
from plugins.vocabulary.loader import Loader
from plugins.vocabulary.service import Service

logger = logging.getLogger(__name__)


class Vocabulary(MaterialPlugin):
    """ Lists of words for vocabulary learning """

    def __init__(self):
        super().__init__()
        database = environ.get("DATABASE", "vocabulary.db")
        self.counter = 0
        self.categories = []
        self.service = Service(database)

    def load(self, data):
        """ Loads vocabulary """
        location = Path(data).joinpath("Vocabulary")
        logger.info(f"Loading vocabulary from {location}")

        vocabulary_loader = Loader(0, location)
        self.categories = vocabulary_loader.load_from_location(location)

        vocabulary = Blueprint("vocabulary_api", __name__)

        @vocabulary.route("/vocabulary")
        def get_vocabulary():
            """ Get the list of vocabulary categories """
            categories = self.service.get_categories()
            return jsonify(categories)

        @vocabulary.route("/vocabulary/<int:category_id>")
        def get_category(category_id):
            category = self.service.get_category(category_id)
            if category is None:
                abort(404, "Category not found.")
            return jsonify(category)

        @vocabulary.route("/vocabulary", methods=["POST"])
        def post_category():
            data = request.json
            category_id = self.service.create_category(data)
            return jsonify(category_id)

        @vocabulary.route("/vocabulary", methods=["PUT"])
        def put_category():
            data = request.json
            category_id = self.service.update_category(data)
            return jsonify(category_id)

        @vocabulary.route("/vocabulary/<int:category_id>", methods=["DELETE"])
        def delete_category(category_id):
            self.service.delete_category(category_id)
            return jsonify({"result": True})

        @vocabulary.route("/vocabulary/recent")
        def get_recent():
            recent = self.service.get_recent()
            return jsonify(recent)

        @vocabulary.route("/vocabulary/batch", methods=["PUT"])
        def update_batch():
            data = request.json
            updated = self.service.update_views(data)
            return jsonify(updated)

        return vocabulary
