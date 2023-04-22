"""
    Repository

    sqlite based repository
"""

import sqlite3
from typing import List

from repository import Repository
from model import Category


class SQLiteRepository(Repository):
    """sqlite3 material database"""

    # Default database location
    __DB_LOCATION = "./repository.db3"

    # Select category
    __SELECT_CATEGORIES = (
        "SELECT c.Id AS c_Id, Name, c.LastUse AS c_LastUse, Type, it.Id, Text, Views, Image, it.LastUse "
        + "FROM Categories c join Items it on c.Id = it.CategoryId"
    )

    def __init__(self, db_location=None):
        """Initialize db class variables"""
        if db_location is not None:
            self.__db_connection = sqlite3.connect(
                db_location,
                check_same_thread=False,
                detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            )
        else:
            self.__db_connection = sqlite3.connect(
                self.__DB_LOCATION, check_same_thread=False
            )
        self.__db_connection.row_factory = sqlite3.Row
        self.cur = self.__db_connection.cursor()

    def close(self):
        """close sqlite3 connection"""
        self.__db_connection.close()

    def all_categories(self) -> List[dict]:
        """Retrieve all the categories."""
        self.__db_connection.row_factory = sqlite3.Row
        rows = self.__db_connection.execute("SELECT * FROM Categories")
        return rows

    def all_categories2(self) -> List[dict]:
        """Retrieve all the categories."""
        self.__db_connection.row_factory = sqlite3.Row
        rows = self.__db_connection.execute(
            "SELECT * FROM Categories c JOIN items it ON it.Id = c.Id"
        )
        return rows

    def all_items(self) -> List[dict]:
        """Retrieve all the items."""
        rows = self.__db_connection.execute("select * from Items")
        return [row for row in rows]

    def get_recent(self, count):
        sql = f"SELECT * FROM Categories ORDER BY LastUSE DESC LIMIT { count }"
        return self.execute_sql_select(sql)

    def get_recent_items(self, ids: List[int]):
        sql = f"SELECT * FROM Items WHERE CategoryId IN ({','.join([str(id) for id in ids])})"
        return self.execute_sql_select(sql)

    def get_items(self, ids: List[int]):
        sql = f"SELECT * FROM Items WHERE Id IN ({','.join([str(id) for id in ids])})"
        return self.execute_sql_select(sql)

    def get_item(self, item_id: int):
        sql = f"SELECT * FROM Items WHERE Id = {item_id}"
        return self.execute_sql_select(sql)

    def category(self, category_id: int):
        # sql = f"SELECT c.Id as c_id, Name, c.LastUse as c_LastUse, it.Id as it_id, * FROM Categories c JOIN items it ON it.CategoryId = c.id WHERE c.id = {category_id}"
        # sql = f"SELECT * FROM Categories c JOIN items it ON it.CategoryId = c.id WHERE c.id = {category_id}"
        sql = f"select c.Id as c_Id, Name, c.LastUse as c_LastUse, Type, it.Id, Text, Views, Image, it.LastUse from Categories c join Items it on c.Id = it.CategoryId Where c.Id = {category_id}"
        return self.execute_sql_select(sql)

    def save_category(self, category: Category) -> int:
        """Store a new category in the database"""
        self.__db_connection.row_factory = sqlite3.Row
        self.cur.execute(
            "INSERT INTO Categories (Name, LastUse) VALUES (?, ?)",
            (category.name, category.last_view),
        )
        category_id = self.cur.lastrowid
        new_items = [
            (it.text, it.image, it.views, it.last_view, category_id)
            for it in category.items
            if it.id == 0
        ]
        self.cur.executemany(
            "insert into Items (Text, Image, Views, LastUse, CategoryId) values (?, ?, ?, ?, ?)",
            new_items,
        )

        if len(new_items) < len(category.items):
            existing_items = [it.id for it in category.items if it.id != 0]
            to_update = ",".join(existing_items)
            update_cmd = (
                f"update Items set CategoryId = {category_id} where Id in ({to_update})",
            )
            self.cur.executemany(update_cmd)

        self.commit()
        return category_id

    def mark_category_completed(self, category_id):
        sql = f"UPDATE Categories SET Completed = 1 WHERE Id = {category_id}"
        self.cur.execute(sql)

    def execute(self, cmd, new_data):
        """execute a row of data to current cursor"""
        self.cur.execute(cmd, new_data)

    def execute_statement(self, cmd):
        self.cur.execute(cmd)

    def execute_sql_select(self, sql: str) -> dict:
        """Run a SELECT statement"""
        try:
            cur = self.__db_connection.cursor()
            rows = cur.execute(sql)
            rows = cur.fetchall()
            cur.close()
            # self.cur.execute(sql)
            # rows = self.cur.fetchall()
            return [dict(row) for row in rows]
        except sqlite3.Error as db_error:
            print(f"Error: {db_error.args[0]}")
            raise

    def execute_many(self, cmd, many_new_data):
        """update many data to database in one go"""
        self.cur.executemany(cmd, many_new_data)

    def all_table_content(self, table: str):
        """Retrieve the content of the given table"""
        self.__db_connection.row_factory = sqlite3.Row
        self.cur.execute(f"SELECT * FROM {table}")
        rows = self.cur.fetchall()
        return [dict(row) for row in rows]

    def run_script(self, script: str) -> None:
        """Run the given script file"""
        with open(script, "r", encoding="utf-8") as sqlite_file:
            sql_script = sqlite_file.read()
        self.cur.executescript(sql_script)

    def get_info(self):
        pass

    def commit(self):
        """commit changes to database"""
        self.__db_connection.commit()

    def __del__(self):
        self.__db_connection.close()

    # Implement __enter__ and __exit to allow expressions like
    #   with Repository() as db:
    #       ....
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.cur.close()
        if isinstance(exc_value, Exception):
            self.__db_connection.rollback()
        else:
            self.__db_connection.commit()
        self.__db_connection.close()
