"""
   CRUD operations for sqlite database.
"""
import logging
import csv
from datetime import datetime, timedelta
import sqlite3


logger = logging.getLogger(__name__)


class DBWords:
    """ CRUD operations for sqlite database. """

    def __init__(self, database):
        self.database = database
        self.__connection = None

    @property
    def connection(self):
        """ Get database connection """
        if self.__connection is None:
            self.__connection = self.open_connection()
            self.check_database(self.__connection)
        return self.__connection

    def select_category(self, category_id):
        self.connection.row_factory = sqlite3.Row
        cursor = self.connection.cursor()
        sql = f"SELECT C.id as c_id, name as c_name, C.lastUse as c_lastUse, \
                        W.id as w_id, word as w_word, W.lastUse as w_lastUse, views as w_views \
                    FROM Categories C \
                    INNER JOIN Words W ON C.id = W.categoryId \
                    WHERE C.id = {category_id}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        cursor.close()
        ddata = [dict(row) for row in rows]
        if not ddata:
            return None
        # TODO: Move this code to a custom row factory
        for data in ddata:
            if data["c_lastUse"] is not None:
                data["c_lastUse"] = datetime.strptime(
                    data["c_lastUse"], "%Y-%m-%d %H:%M:%S.%f"
                )
            if data["w_lastUse"] is not None:
                data["w_lastUse"] = datetime.strptime(
                    data["w_lastUse"], "%Y-%m-%d %H:%M:%S.%f"
                )
        category = {k[2:]: ddata[0][k]
                    for k in ddata[0].keys() if k.startswith("c_")}
        words = []
        for data in ddata:
            words.append({k[2:]: data[k]
                         for k in data.keys() if k.startswith("w_")})
        category["words"] = words
        return category

    def select_categories(self):
        """ Retrieve all categories """
        try:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            cursor.execute("SELECT * FROM Categories")
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def create_category(self, category):
        try:
            cursor = self.connection.cursor()
            sql = f"INSERT INTO Categories('name', 'lastUse') VALUES (?,?)"
            cursor.execute(
                sql, (category["name"], category.get("lastUse", None)))
            cursor.execute("SELECT last_insert_rowid()")
            row = cursor.fetchone()
            category_id = row[0]

            input_words = [
                (w["word"], w.get("views", 0), w.get(
                    "lastUse", None), category_id)
                for w in category["words"]
            ]
            if input_words:
                cursor.executemany(
                    f"INSERT INTO Words('word', 'views', 'lastUse', 'categoryId') VALUES (?,?,?,?)",
                    input_words,
                )
            self.connection.commit()
            return self.select_category(category_id)
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def update_category(self, category):
        try:
            cursor = self.connection.cursor()
            sql = f'UPDATE Categories \
                    SET name = {category["name"]}, SET lastUsed = {category["lastUse"]} \
                    WHERE id = category["id"]'
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def delete_category(self, category_id):
        try:
            cursor = self.connection.cursor()
            sql = f"DELETE FROM Categories WHERE id = {category_id}"
            cursor.execute(sql)
            sql = f"DELETE FROM Words WHERE categoryId = {category_id}"
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def update_words(self, words):
        try:
            cursor = self.connection.cursor()
            for word in words:
                wdata = (word["lastUse"], word["views"], word["id"])
                cursor.execute(
                    "UPDATE Words SET lastUse = ?, views = ? WHERE id = ?", wdata
                )
            self.connection.commit()
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def delete_words(self, words):
        try:
            cursor = self.connection.cursor()
            ids = str([item["id"] for item in words]).replace(
                "[", "").replace("]", "")
            sql = f"DELETE FROM Words WHERE id IN ({ids})"
            cursor.execute(sql)
            self.connection.commit()
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def create_words(self, words, category_id):
        try:
            cursor = self.connection.cursor()
            new_words = [
                (w["word"], w.get("views", 0), w.get(
                    "lastUse", None), category_id)
                for w in words
            ]
            if new_words:
                cursor.executemany(
                    f"INSERT INTO Words('word', 'views', 'lastUse', 'categoryId') VALUES (?,?,?,?)",
                    new_words,
                )
            self.connection.commit()
            return True
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def get_recent(self, days, count):
        """ Return categories used recently.

            Look for categories with lastUse in the last days. The number
            of categories returned is limited.

            Parameters:
                days: integer. Range of days backward from today to look into
                count: integer. Maximum number of categories returned
        """

        try:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            recent_day = (datetime.today() + timedelta(days=-days)
                          ).strftime("%Y-%m-%d")
            sql = f"SELECT * FROM Categories \
                WHERE lastUse > '{recent_day}' OR lastUse IS Null\
                ORDER BY lastUSE DESC LIMIT {count}"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            logger.error(error.args[0])

    def update_views(self, batch):
        try:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            today = datetime.today()
            ids = ",".join(map(str, [w["id"] for w in batch["words"]]))
            sql = f"UPDATE words SET views = views + 1, lastUse = '{today}' WHERE id IN ({ids})"
            cursor.execute(sql)
            sql = f"UPDATE categories SET lastUse = '{today}' WHERE id = {batch['id']}"
            cursor.execute(sql)
            self.connection.commit()

            sql = f"SELECT * FROM Words WHERE id IN ({ids})"
            cursor.execute(sql)
            rows = cursor.fetchall()
            words = [dict(row) for row in rows]
            sql = f"SELECT * FROM Categories WHERE id = {batch['id']}"
            cursor.execute(sql)
            row = cursor.fetchone()
            cursor.close()

            updated_batch = dict(row)
            updated_batch["words"] = words
            return updated_batch
        except sqlite3.Error as error:
            logger.error(error.args[0])

    def get_words_for_categories(self, ids):
        try:
            self.connection.row_factory = sqlite3.Row
            cursor = self.connection.cursor()
            sql = f"SELECT * FROM Words \
                    WHERE categoryId in ({ids}) \
                    ORDER BY lastUse DESC"
            cursor.execute(sql)
            rows = cursor.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as error:
            logger.error(error.args[0])

    def open_connection(self):
        try:
            return sqlite3.connect(self.database, check_same_thread=False)
        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def check_database(self, connection):
        """ Create tables in the database if they do not exist.
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
                self.create_categories_table(connection)

            sql = """
                SELECT name FROM sqlite_master
                WHERE type='table' AND name='Words';
            """
            cursor.execute(sql)
            row = cursor.fetchone()
            if row is None:
                self.create_words_table(connection)

        except sqlite3.Error as db_error:
            logger.error(db_error.args[0])
            raise Exception(db_error.args[0])

    def create_categories_table(self, connection):
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

    def create_words_table(self, connection):
        """ Create words table """
        sql = """
            CREATE TABLE Words(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                word TEXT NOT NULL UNIQUE,
                categoryId INTEGER,
                lastUse datetime,
                views INTEGER DEFAULT 0           
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

    def load_csv(self, csv_file):
        """ Load data from a csv file."""
        rows = []
        with open(csv_file, "r", encoding="utf-8") as fcsv:
            reader = csv.DictReader(
                fcsv, fieldnames=("category", "words"), restkey="words"
            )
            rows = [i for i in reader]

        # categories = []
        # for row in rows:
        #     category = {}
        #     category["name"] = row["category"]
        #     category["lastUse"] = None
        #     category["words"] = [
        #         {"word": w, "lastUse": None, "views": 0} for w in row["words"]
        #     ]
        #     categories.append(category)

        categories = [
            {
                "name": row["category"],
                "lastUse": None,
                "words": [
                    {"word": w, "lastUse": None, "views": 0} for w in row["words"]
                ],
            }
            for row in rows
        ]

        for category in categories:
            self.create_category(category)

        return categories


def dict_factory(cursor, row):
    word = {}
    for idx, col in enumerate(cursor.description):
        word[col[0]] = row[idx]
    return word
