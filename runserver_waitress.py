"""
    Launch material server
"""
import io
import errno
import json
import logging
import logging.config
import pkgutil
import inspect
import ssl


from os import environ, strerror
from waitress import serve
from importlib import import_module
from pathlib import Path
from flask import Flask, jsonify, make_response, abort, request, Response
from flask.json import JSONEncoder
from werkzeug.exceptions import HTTPException
from flask_cors import CORS
from dotenv import load_dotenv
from material_service import MaterialService
from loginit import logger
from sqlite_repository import SQLiteRepository
from material_db_service import MaterialDbService
from material_plugin import MaterialPlugin
from plugin_loader import load_plugins
from api.books.books_api import books_api, loader
from api.questions.qa_api import qa_api


# logger = logging.getLogger(__name__)

verboseprint = lambda *args, **kargs: None
verboseprint = print


# def load_plugins(directory):
#     """
#         Finds and loads all the classes that extend MaterialPlugin in the
#         given directory
#     """
#     logger.debug("Loading plugins")
#     imported_package = import_module(directory)
#     found_plugins = []

#     for _, pluginname, ispkg in pkgutil.iter_modules(
#         imported_package.__path__, imported_package.__name__ + "."
#     ):
#         if not ispkg:
#             plugin_module = import_module(pluginname)
#             print(plugin_module)
#             clsmembers = inspect.getmembers(plugin_module, inspect.isclass)
#             for (_, clazz) in clsmembers:
#                 logger.debug()
#                 # Only add classes that are a sub class of Plugin, but NOT Plugin itself
#                 if issubclass(clazz, MaterialPlugin) & (clazz is not MaterialPlugin):
#                     print(f"Found plugin class: {clazz.__module__}.{clazz.__name__}")
#                     logger.debug(
#                         f"Found plugin class: {clazz.__module__}.{clazz.__name__}"
#                     )
#                     found_plugins.append(clazz())

#     logger.info(f"Found {len(found_plugins)} plugin(s).")
#     return found_plugins


load_dotenv(verbose=True)

MATERIAL = environ.get("MATERIAL", ".")
BITS_PATH = Path(environ.get("bits", "."))

logger.info(f"Reading material from {BITS_PATH}.")

# Initialize database
# try:
#     generator = Generator(BITS_PATH)
# except FileNotFoundError:
#     print(f"{strerror(errno.ENOENT)}: {BITS_PATH}")
#     exit("No data available")

database = Path(environ.get("database_path", "."), environ.get("database"))
logger.info(f"Database: {database}")
# service = MaterialDbService(database)

# repository = SQLiteRepository("test_db.db3")
repository = SQLiteRepository(database)
service = MaterialService(repository)

blueprints = []
plugins = load_plugins("plugins", MaterialPlugin)
for plugin in plugins:
    blueprints.append(plugin.load(MATERIAL))

app = Flask(__name__)
CORS(app)

app.register_blueprint(books_api)
app.register_blueprint(qa_api)

for blueprint in blueprints:
    app.register_blueprint(blueprint)


@app.route("/")
@app.route("/recent")
def get_recent_categories():
    """Recently used categories"""
    logger.info("get_recent_categories")
    categories = service.get_recent()
    json_string = json.dumps(categories).encode("utf-8")
    response = make_response(json_string.decode("utf-8"))
    response.content_type = "application/json"
    response.charset = "utf-8"
    return response


@app.route("/categories")
def all_categories():
    logger.info("all_categories")
    categories = service.get_all_complete_categories()
    json_string = json.dumps(categories, cls=JSONEncoder, ensure_ascii=False)
    response = make_response(json_string)
    response.content_type = "application/json"
    response.charset = "utf-8"
    return response


@app.route("/items")
def all_items():
    logger.info("all_items")
    items = service.get_all_items()
    json_string = json.dumps(items, cls=JSONEncoder, ensure_ascii=False)
    response = make_response(json_string)
    response.content_type = "application/json"
    response.charset = "utf-8"
    return response


@app.route("/categories/<int:category_id>")
def get_category(category_id):
    """Return category images"""
    category = service.get_category(category_id)
    if category is None:
        abort(404)
    response = make_response(json.dumps(category, cls=JSONEncoder, ensure_ascii=False))
    response.content_type = "application/json"
    return response


@app.route("/image/<int:img_id>")
def get_image(img_id):
    bit = service.get_item(img_id)
    if bit is None:
        abort(404)
    with io.FileIO(BITS_PATH.joinpath(bit["Image"])) as img:
        img_bytes = img.readall()
    response = make_response(img_bytes)
    response.headers.set("Content-Type", "image/jpeg")
    return response


@app.route("/updatebatch", methods=["POST"])
def update_batch():
    logger.debug(request.json)
    data = request.json
    result = service.update_batch(data)
    if not result:
        return json.dumps({"success": False}), 500, {"ContentType": "application/json"}

    return json.dumps({"success": True}), 200, {"ContentType": "application/json"}


# @app.route("/groups/")
# def get_groups():
#     json_string = json.dumps(
#         generator.groups, default=category_encoder, ensure_ascii=False
#     ).encode("utf-8")
#     response = make_response(json_string.decode("utf-8"))
#     response.content_type = "application/json"
#     response.charset = "utf-8"
#     return response


# @app.route("/groups/recent")
# def get_recent_groups():
#     json_string = json.dumps(
#         generator.get_recent_groups(), default=category_encoder, ensure_ascii=False
#     ).encode("utf-8")
#     response = make_response(json_string.decode("utf-8"))
#     response.content_type = "application/json"
#     response.charset = "utf-8"
#     return response


# @app.route("/groups/new", methods=["POST"])
# def create_group():
#     logger.debug(request.json)
#     data = request.json
#     group = generator.create_group(data)
#     json_string = json.dumps(
#         group, default=category_encoder, ensure_ascii=False
#     ).encode("utf-8")
#     return json_string, 201


# @app.route("/groups/edit", methods=["PUT"])
# def edit_group():
#     logger.debug(request.json)
#     group = generator.update_group(request.json)
#     json_string = json.dumps(
#         group, default=category_encoder, ensure_ascii=False
#     ).encode("utf-8")
#     return json_string, 201


# @app.route("/groups/<int:group_id>", methods=["PUT"])
# def save_group(group_id):
#     logger.debug(f"save group. id = {group_id}")
#     logger.debug(request.json)
#     group = generator.update_group(request.json)
#     json_string = json.dumps(
#         group, default=category_encoder, ensure_ascii=False
#     ).encode("utf-8")

#     return json_string.decode("utf-8"), {"Content-Type": "application/json"}


# @app.route("/groups/<int:group_id>")
# def get_group(group_id):
#     group = generator.get_group(group_id)
#     if group is None:
#         abort(404)
#     response = make_response(
#         json.dumps(group, default=category_encoder, ensure_ascii=False)
#     )
#     response.content_type = "application/json"
#     return response


# @app.route("/info")
# def get_info():
#     info = service.get_info()
#     info_data = {"categories": 0, "bits": 0}
#     if info is not None:
#         info_data = {
#             "categories": info["cat_count"],
#             "groups": 0,
#             "bits": info["item_count"],
#         }
#     # groups, books = loader.get_element_count("books")
#     # info_data["book_groups"] = groups
#     # info_data["books"] = books
#     return jsonify(info_data), 200


@app.route("/favicon.ico")
def favicon():
    return jsonify(success=True)


@app.errorhandler(404)
def not_found(error):
    logger.debug(request.url)
    logger.info(str(error))
    return make_response(jsonify({"error": "Not found"}))


@app.errorhandler(HTTPException)
def handle_exception(exception):
    """Return JSON instead of HTML for HTTP errors."""
    # start with the correct headers and status code from the error
    response = exception.get_response()
    # replace the body with JSON
    response.data = json.dumps(
        {
            "code": exception.code,
            "name": exception.name,
            "description": exception.description,
            "exception": exception.original_exception.args[0],
        }
    )
    response.content_type = "application/json"
    return response


if __name__ == "__main__":

    ## contexto para https. No admitido por Maui
    # context = ("cert.pem", "key.pem")
    # app.run(host="0.0.0.0", port=5050, ssl_context=context, threaded=True, debug=True)

    # app.run(host="192.168.1.57", port=5050)
    # serve(app, host="192.168.1.57", port=5000)

    waitress_log = logging.getLogger("waitress")
    waitress_log.setLevel(logging.DEBUG)
    serve(app, host="0.0.0.0", port=5050)
    # serve(app, port=5000)
