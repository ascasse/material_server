"""
    process_db.py

    Processes on execution
"""

import logging
from datetime import datetime, timedelta
import sqlite3
import plugins.vocabulary.vocabulary_db as voc

logger = logging.getLogger(__name__)


def update_category_batch(category_id, words):
    """ Updates a batch of words in a category.

        Set lastUse column to current date for category and words
        Increases views counter for every word

        Parameters:

        category_id : int. The category id

            words: list(int). Ids of the words in the lot
    """

    connection = voc.open_connection()
    voc.check_database(connection)
    try:
        connection = voc.open_connection()
        voc.check_database(connection)
        cursor = connection.cursor()
        today = datetime.today().strftime("%Y-%m-%d")
        sql = f"UPDATE words \
            SET views = views + 1, lastUse = '{today}' \
            WHERE id IN ({','.join(map(str, words))})"
        cursor.execute(sql)
        sql = f"UPDATE categories SET lastUse = {today} WHERE id = {category_id}"
        cursor.execute(sql)
        connection.commit()
    except sqlite3.Error as error:
        logger.error(error.args[0])
    finally:
        connection.close()


def update_batch(batch, connection):
    try:

        cursor = connection.cursor()
        today = datetime.today()
        ids = ",".join(map(str, [w["id"] for w in batch["words"]]))
        sql = f"UPDATE words SET views = views + 1, lastUse = '{today}' WHERE id IN ({ids})"
        cursor.execute(sql)
        sql = f"UPDATE categories SET lastUse = '{today}' WHERE id = {batch['id']}"
        cursor.execute(sql)
        connection.commit()

        connection.row_factory = sqlite3.Row
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


def get_recent(connection, days, count):
    """ Return categories used recently.

        Look for categories with lastUse in the last days. The number
        of categories returned is limited.

        Parameters:

            days: integer. Range of days backward from today to look into

            count: integer. Maximum number of categories returned
    """

    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        recent_day = (datetime.today() + timedelta(days=-days)).strftime("%Y-%m-%d")
        sql = f"SELECT * FROM Categories \
            WHERE lastUse > '{recent_day}' \
            ORDER BY lastUSE DESC LIMIT {count}"
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as error:
        logger.error(error.args[0])


def get_recent_words(connection, ids):
    try:
        connection.row_factory = sqlite3.Row
        cursor = connection.cursor()
        sql = f"SELECT * FROM Words \
                WHERE categoryId in ({ids}) \
                ORDER BY lastUse DESC"
        cursor.execute(sql)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    except sqlite3.Error as error:
        logger.error(error.args[0])


def update_words_view(words):
    """ Increases views counter for every word.

        Parameters:

            words: list(int) List of word ids
    """

    connection = voc.open_connection()
    voc.check_database(connection)
    try:
        cursor = connection.cursor()
        sql = f'UPDATE words \
            SET views = views + 1, lastUse = {datetime.today().strftime("%Y-%m-%d")} \
            WHERE id IN ({",".join(map(str, words))})'
        cursor.execute(sql)
        row = cursor.fetchone()
        connection.commit()
        return row
    except sqlite3.Error as error:
        logger.error(error.args[0])
    finally:
        connection.close()
