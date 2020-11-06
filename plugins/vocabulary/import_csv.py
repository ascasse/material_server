"""
    Load data from csv

    Usage: import_csv <database file> <csv_file>

"""
import sys
from plugins.vocabulary.db_words import DBWords

CSV_FILE = "./test/data/vocabulary/vocabulary.csv"


def load(database, csv_file):
    connection = DBWords(database)
    categories = connection.load_csv(csv_file)
    print(categories)

    word_count = sum(len(c["words"]) for c in categories)
    print(f"{word_count} words in {len(categories)} categories.")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
    else:
        load(sys.argv[1], sys.argv[2])
