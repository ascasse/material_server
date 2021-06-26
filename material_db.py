import sys
import sqlite3
from datetime import datetime, timedelta
from os import environ
from dotenv import load_dotenv
from typing import List
from pathlib import Path
from model import Category, Item, ItemDb


# PATH = "C:/develop/material_Raquel/learning/ConsoleVocabulary/LearningAPI/"
# DATABASE = "Vocabulary.db3"


def all_categories(database) -> List[dict]:
    """Retrieves all the categories."""
    return all_table_content(database, "categories")


def all_items(database) -> List[dict]:
    """Retrieves all the items."""
    return all_table_content(database, "items")


def create_category(database, category: Category):
    """
    Creates a new category.
    """
    try:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            last_use = "NULL"
            if category.last_view is not None:
                last_use = f"'{category.last_view.strftime('%Y/%m/%d')}'"
            sql = f"INSERT INTO Categories ('Name', 'LastUse') VALUES ('{category.name}', {last_use})"
            cursor.execute(sql)
            cursor.execute("commit")

            category_id = cursor.lastrowid

            items = [ItemDb(item) for item in category.items]
            # items_data = [
            #     (
            #         i.text,
            #         i.last_view,
            #         i.views,
            #         i.image,
            #         category_id,
            #     )
            #     for i in items
            # ]
            # cmd = "INSERT INTO Items ('Text', 'LastUse', 'Views', Image', 'CategoryId') VALUES (?, ?, ?, ?, ?)"
            # cursor.executemany(cmd, items_data)
            for it in items:
                cursor.execute(
                    "INSERT INTO Items (Text, LastUse, Views, Image, CategoryId) VALUES (?, ?, ?, ?, ?)",
                    (it.text, it.last_view, it.views, it.image, category_id),
                )
            print(f"Created category {category.name}")
            cursor.execute("commit")

    except sqlite3.Error as db_error:
        print(f"Error: {db_error.args[0]}")
        print(f"Error creating category {category.name}")
        raise


def get_recent(database: str, days: int, count: int):
    recent_day = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
    sql = f"SELECT * FROM Categories WHERE LastUse > '{ recent_day }' OR lastUse IS NULL ORDER BY LastUSE DESC LIMIT { count }"
    return execute_sql_select(database, sql)
    # try:
    #     connection = open_connection(database)
    #     connection.row_factory = sqlite3.Row
    #     cursor = connection.cursor()
    #     cursor.execute(sql)
    #     rows = cursor.fetchall()
    #     return [dict(row) for row in rows]
    # except sqlite3.Error as db_error:
    #     print(f"Error: {db_error.args[0]}")
    #     raise
    # finally:
    #     if connection is not None:
    #         connection.close()


def get_recent_items(database: str, ids: List[int]):
    sql = (
        f"SELECT * FROM Items WHERE CategoryId IN ({','.join([str(id) for id in ids])})"
    )
    return execute_sql_select(database, sql)


def get_item(database: str, item_id: int):
    sql = f"SELECT * FROM Items WHERE Id = {item_id}"
    return execute_sql_select(database, sql)


def get_info(database: str) -> tuple:
    sql = "SELECT (SELECT COUNT(*) FROM Categories) AS cat_count, (SELECT COUNT(*) FROM Items) AS item_count"
    info = execute_sql_select(database, sql)
    return info[0] if info is not None and len(info) > 0 else None


def execute_sql_select(database: str, sql: str) -> dict:
    try:
        connection = open_connection(database)
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_error:
        print(f"Error: {db_error.args[0]}")
        raise
    finally:
        if connection is not None:
            connection.close()


def all_table_content(database: str, table: str) -> List[dict]:
    """Retrieves the content of the given table"""
    connection = open_connection(database)
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        cursor.execute(f"SELECT * FROM {table}")
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as db_error:
        print(f"Error: {db_error.args[0]}")
        raise
    finally:
        connection.close()


def open_connection(database):
    """Get a connection to the given database."""
    try:
        return sqlite3.connect(database)
    except sqlite3.Error as db_error:
        print(f"Error: {db_error.args[0]}")
        raise


def update_views(database, updated_views):
    try:
        with sqlite3.connect(database) as connection:
            cursor = connection.cursor()
            # cmd = "UPDATE Items SET views = ? WHERE id = ?"
            # cursor.executemany(
            #     cmd, [[x[0], x[1]] for x in [tp for tp in iter(updated_views)]]
            # )
            # cursor.executemany(cmd, [tp for tp in iter(updated_views)])
            # cursor.execute("commit")

            for tp in iter(updated_views):
                cmd = f"UPDATE Items SET LastUse = '{datetime.now().strftime('%Y/%m/%d')}', Views = {tp[0]} WHERE id = {tp[1]}"
                cursor.execute(cmd)

            cursor.execute("commit")

    except sqlite3.Error as db_error:
        print(f"Error: {db_error.args[0]}")
        raise


def run_script(database: str, script_file: str) -> None:
    try:
        connection = open_connection(database)
        cursor = connection.cursor()
        print("Successfully Connected to SQLite")

        with open(script_file, "r") as sqlite_file:
            sql_script = sqlite_file.read()

        cursor.executescript(sql_script)
        print("SQLite script executed successfully")
        cursor.close()

    except sqlite3.Error as error:
        print(f"Error while executing script {error}")
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed")


def run_sql(database: str, sql: str) -> None:
    try:
        connection = open_connection(database)
        cursor = connection.cursor()
        print("Successfully Connected to SQLite")

        cursor.executescript(sql)
        print("SQLite script executed successfully")
        cursor.close()

    except sqlite3.Error as error:
        print(f"Error while executing script {error}")
    finally:
        if connection:
            connection.close()
            print("SQLite connection closed")


if __name__ == "__main__":

    load_dotenv()
    PATH = environ.get("database_path", ".")
    DATABASE = environ.get("database", "Vocabulary.db3")

    database_path = Path(PATH, DATABASE)
    if not database_path.exists():
        print(f"{DATABASE} does not exist.")
        sys.exit(1)

    categories = all_categories(database_path)
    print(f"Reading database {database_path}")
    print(categories)

    # test_category = Category("test", [Item("test_item", "test_image")])
    # create_category(database_path, test_category)
