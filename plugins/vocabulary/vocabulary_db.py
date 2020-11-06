"""
    vocabulary_db

    Operations in vocabulary database
"""
import logging
import sqlite3

logger = logging.getLogger(__name__)

DATABASE_NAME = "vocabulary.db"
LOT_SIZE = 6
RECENT = 7


def set_database(database):
    """ Set default database file"""
    global DATABASE_NAME
    DATABASE_NAME = database


def create_category(category, connection=None):
    """ Insert a new category into the database.

        Parameters:

            category: dict. Category to insert

        Returns

            id:  int New category id
    """
    if connection is None:
        default_connection = open_connection()
        connection = default_connection
        check_database(connection)
    else:
        default_connection = None

    # Set default values
    category.setdefault("lastUse", None)
    category.setdefault("views", 0)
    category.setdefault("words", [])

    try:
        cursor = connection.cursor()
        sql = f"INSERT INTO Categories('name', 'lastUse') VALUES (?,?)"
        cursor.execute(sql, (category["name"], category["lastUse"]))
        cursor.execute("SELECT last_insert_rowid()")  # Get inserted category id
        row = cursor.fetchone()
        category_id = row[0]
        for word in category["words"]:
            word.setdefault("lastUse", None)
            word.setdefault("views", 0)
            word["categoryId"] = category_id

        input_words = [
            (c["word"], c["views"], c["lastUse"], c["categoryId"])
            for c in category["words"]
        ]
        if input_words:
            cursor.executemany(
                f"INSERT INTO Words('word', 'views', 'lastUse', 'categoryId') VALUES (?,?,?,?)",
                input_words,
            )
        connection.commit()
        return category_id
    except sqlite3.IntegrityError as integrity_error:
        logger.error(integrity_error.args[0])
        raise Exception(integrity_error.args[0])
    except sqlite3.Error as error:
        logger.error(error.args[0])
        raise Exception(error.args[0])
    finally:
        if default_connection:
            default_connection.close()


def select_categories():
    """ Retrieve all categories """
    connection = open_connection()
    check_database(connection)
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Categories")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])
    finally:
        connection.close()


def select_categories_2(connection):
    """ Retrieve all categories """
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Categories")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def select_category(category_id, connection=None):
    """ Retrieve the category with the given id                     \\
        Arguments                                                   \\
        --- connection: Connection                                  \\
        --- id: Category id to look for                             \\
        Returns                                                     \\
        --- category: Found category, None if it does not exist.    \\
    """
    if connection is None:
        default_connection = open_connection()
        connection = default_connection
        check_database(connection)
    else:
        default_connection = None

    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Categories WHERE id = {category_id};")
        row = cursor.fetchone()
        cursor.close()
        return dict(row) if row is not None else None
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])
    finally:
        if default_connection:
            connection.close()


# def select_category(connection, category_id):
#     try:
#         connection.row_factory = sqlite3.Row
#         cursor = connection.cursor()
#         cursor.execute(f"SELECT * FROM Categories WHERE id = {category_id};")
#         row = cursor.fetchone()
#         cursor.close()
#         return dict(row) if row is not None else None
#     except sqlite3.Error as db_error:
#         logger.error(db_error.args[0])
#         raise Exception(db_error.args[0])


def update_category(connection, category):
    """ Update a row in the categories table            \\
        Arguments:                                      \\
            connection: connection to database          \\
            category: dictionary - category to update   \\
        Return:                                         \\
            category: dictionary - updated category
    """
    connection = open_connection()
    check_database(connection)
    try:
        cursor = connection.cursor()
        sql = f"UPDATE Categories SET name = '{category['name']}' WHERE id = {category['id']};"
        cursor.execute(sql)
        connection.commit()
        return select_category(category["id"])
    except sqlite3.Error as error:
        raise Exception(error.args[0])
    finally:
        connection.close()


def delete_category(category_id):
    """ Delete category with the given id \\
        Parameters                        \\
            category_id -- integer
    """
    connection = open_connection()
    check_database(connection)
    try:
        cursor = connection.cursor()
        cursor.execute(f"DELETE FROM Categories WHERE id = {category_id}")
        connection.commit()
    except sqlite3.Error as error:
        raise Exception(error.args[0])
    finally:
        connection.close()


def add_words(category_id, words, connection=None):
    """ Add words to a category.

        Parameters: \\
            category_id: integer. Destination category id \\
            words: list of strings. Words to add
    """

    if connection is None:
        default_connection = open_connection()
        connection = default_connection
        check_database(connection)
    else:
        default_connection = None

    category = select_category(category_id, connection)
    if category is None:
        return [], f"Category with id = {category_id} does not exist."
    try:
        cursor = connection.cursor()
        word_list = [(word, None, 0, category_id) for word in words]
        cursor.executemany(
            "INSERT INTO Words('word', 'lastUse', 'views', 'categoryId') VALUES (?,?,?,?)",
            word_list,
        )
        connection.commit()
    except sqlite3.IntegrityError as integrity_error:
        logger.error(integrity_error.args[0])
        raise Exception(integrity_error.args[0])
    except sqlite3.Error as error:
        logger.error(error.args[0])
        raise Exception(error.args[0])
    finally:
        if default_connection is not None:
            connection.close()


def add_words_2(connection, category_id, words):
    """ Add words to a category

        Skip duplicates

        Parameters:

            connection: object Database connection
            category_id: integer. Target category id
            words: list(dict). Words to add
    """
    category = select_category(category_id, connection)
    if category is None:
        return [], f"Category with id = {category_id} does not exist."
    try:
        cursor = connection.cursor()
        word_list = [(word, None, 0, category_id) for word in words]
        cursor.executemany(
            "INSERT INTO Words('word', 'lastUse', 'views', 'categoryId') VALUES (?,?,?,?)",
            word_list,
        )
        connection.commit()
    except sqlite3.IntegrityError as integrity_error:
        logger.error(integrity_error.args[0])
        raise Exception(integrity_error.args[0])
    except sqlite3.Error as error:
        logger.error(error.args[0])
        raise Exception(error.args[0])


def get_words_for_category(category_id, connection=None):
    """ Retrieve words in a category

        Parameters:

            int. Category id

        Returns:

            list[dict]. List of words
    """
    if connection is None:
        default_connection = open_connection()
        connection = default_connection
        check_database(connection)
    else:
        default_connection = None

    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM Words WHERE categoryId = {category_id};")
        rows = cursor.fetchall()
        cursor.close()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])
    finally:
        if default_connection:
            default_connection.close()


# def get_words_for_category(category_id, connection):
#     try:
#         connection.row_factory = sqlite3.Row
#         cursor = connection.cursor()
#         cursor.execute(f"SELECT * FROM Words WHERE categoryId = {category_id};")
#         rows = cursor.fetchall()
#         cursor.close()
#         return [dict(row) for row in rows]
#     except sqlite3.Error as db_error:
#         logger.error(db_error.args[0])
#         raise Exception(db_error.args[0])


def merge_words(current_words, new_words):
    # Create sets to compare collections
    set_current_words = set(word for word in current_words)
    set_new_words = set(word for word in new_words)

    words_to_delete = set_current_words - set_new_words
    words_to_keep = set_current_words - words_to_delete
    really_new = set_new_words - words_to_keep
    return list(words_to_keep) + list(really_new)


def update_words(current_words, new_words):
    """ Determine words to add and delete for words update.

        Parameters:

            list. Currently existing words
            list. Words after update

        Return:

            list. Words to keep
            list. Words to remove
            list. Words to add
    """
    to_keep = [item for item in current_words for x in new_words if x in item]
    to_delete = [item for item in current_words if item[1] not in new_words]
    curr = [item[1] for item in current_words]
    to_add = [item for item in new_words if item not in curr]
    # Alternative method using a dictionary
    # to_add2 = [item for item in new_words if item not in dict(current_words).values()]
    return to_keep, to_delete, to_add


def create_categories_table(connection):
    sql = """
        CREATE TABLE Categories(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE,
            lastUse datetime
        );
        """
    try:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS Categories;")

        cursor.execute(sql)
        connection.commit()
        cursor.close()
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def create_words_table(connection):
    """ Create words table """
    sql = """
        CREATE TABLE Words(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL UNIQUE,
            categoryId INTEGER,
            lastUse datetime,
            views INTEGER            
        );
        """
    try:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS Words;")

        cursor.execute(sql)
        connection.commit()
        cursor.close()
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def drop_tables():
    try:
        connection = open_connection()
        cursor = connection.cursor()
        sql = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Categories';
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is not None:
            cursor.execute("DROP TABLE Categories")

        sql = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Words';
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is not None:
            cursor.execute("DROP TABLE Words")

    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def drop_tables_2(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("DROP TABLE IF EXISTS Categories")
        cursor.execute("DROP TABLE IF EXISTS Words")
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def check_database(connection):
    """ Verify that Categories and Words tables exist in the database.  \\
        Create tables in the database if they do not exist.             \\
    """
    try:
        cursor = connection.cursor()
        sql = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Categories';
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            create_categories_table(connection)

        sql = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='Words';
        """
        cursor.execute(sql)
        row = cursor.fetchone()
        if row is None:
            create_words_table(connection)

    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def open_connection(db=None):
    """ Get a connection to the default database           \\
        Parameters:                                         \\
            database -- path to database file               \\
        Return:                                             \\
            connection -- connection instance on success
    """
    if db is None:
        db = DATABASE_NAME
    try:
        # db = sqlite3.connect(database)
        return sqlite3.connect(db)
        # return sqlite3.connect(DATABASE_NAME)
    except sqlite3.Error as db_error:
        logger.error(db_error.args[0])
        raise Exception(db_error.args[0])


def run_script(connection, sql_script):
    """ Execute given script.

        Parameters:

            sql_script: string. Path to script file
    """
    with open(sql_script, "r", encoding="utf-8") as sql_file:
        sql = sql_file.read()
    cursor = connection.cursor()
    cursor.executescript(sql)
    connection.commit()
