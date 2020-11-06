import logging
from os import environ
from pathlib import Path

from flask import Blueprint, jsonify, abort, request
from dotenv import load_dotenv

from material_loader import MaterialLoader
from util import make_image_response

logger = logging.getLogger(__name__)

qa_api = Blueprint('questions_api', __name__)

load_dotenv()

MATERIAL = environ.get('MATERIAL', '.')
qa_location = Path(MATERIAL).joinpath('qa')
logger.info(f'Loading q&a from {str(qa_location)}')

loader = MaterialLoader(qa_location)
loader.load()
loader.load_groups()


@qa_api.route('/qa')
def get_qa():
    return jsonify(loader.categories)


@qa_api.route('/qa/category/<int:category_id>')
def get_category(category_id):
    category = loader.find_category(category_id)
    return jsonify(category)


@qa_api.route('/qa/image/<int:qa_id>')
def get_image(qa_id):
    found = loader.find_image(qa_id)
    if found is None:
        abort(404)
    return make_image_response(found['imagefilepath'])


@qa_api.route('/qa/groups')
def get_groups():
    groups = loader.load_groups()
    return jsonify(groups)


@qa_api.route('/qa/groups/<int:group_id>', methods=['GET'])
def get_group(group_id):
    found = loader.find_group(group_id)
    if found is None:
        abort(404)
    return jsonify(found)


@qa_api.route('/qa/groups/new', methods=['POST'])
def save_group():
    logger.debug(f'new group')
    logger.debug(request.json)
    group = loader.create_group(request.json)
    return jsonify(group)


@qa_api.route('/qa/groups/<int:group_id>', methods=['PUT'])
def update_group(group_id):
    logger.debug(f'update group. id = {group_id}')
    logger.debug(request.json)
    group = loader.update_group(request.json)
    return jsonify(group)
