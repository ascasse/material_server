"""
    Material service
"""
from datetime import datetime as dt, timedelta
from os import environ
from dotenv.main import load_dotenv
from pathlib import Path
from model import Category, Item
import material_db as db


class MaterialDbService:
    """Material service based on database."""

    def __init__(self, database=None):

        self.recent_count = 5  # Max number of recently viewed categories to return.
        self.recent_days = 7  # Date range to look for recently viewed items, in days.
        self.batch_size = 10  # Max number of elements returned in a batch.
        self.max_views = 5  # Max times a given element is included in a batch.
        self.refresh_rate = 3  # Number of elements replaced when a batch is updated.
        self.same_day_count = (
            True  # Set whether should update views counter for the same day.
        )
        if database is not None:
            self.database = database  # database
        else:
            load_dotenv()
            self.database = Path(
                environ.get("database_path", "./"), environ.get("database", None)
            )

        self.categories = []

        # # Load categories
        # with open(database, "r") as db:
        #     data = json.load(db)
        #     self.categories = [Category(dct) for dct in data]

    # def load(self):
    #     with open(self.database, "r") as db:
    #         data = json.load(db)
    #         self.categories = []
    #         for dct in data:
    #             self.categories.add(Category(dct["id"]))
    #         self.categories = [Category(dct) for dct in data]

    def get_info(self) -> tuple:
        return db.get_info(self.database)

    def get_all_items(self):
        """Retrieves all items in the database."""
        return db.all_items(self.database)

    def get_item(self, id: int):
        """Retrieves the item with the given id."""
        items = db.get_item(self.database, id)
        return items[0] if len(items) > 0 else None

    def get_recent(self):
        """Get recently viewed categories"""
        recent = db.get_recent(self.database, self.recent_days, self.recent_count)
        ids = [x["Id"] for x in recent]
        recent_items = db.get_recent_items(self.database, ids)
        for category in recent:
            category["Items"] = [
                item for item in recent_items if item["CategoryId"] == category["Id"]
            ]
        return recent

    def get_batch(self, category: Category):
        """Build a new batch from the given category"""
        batch = Category(category.name, category.items)

        # Look for elements that have not reached max_views
        to_view = [item for item in category.items if item.views < self.max_views]
        # All elements have reached max_views. Mark as completed and terminate
        if not to_view:
            batch.completed = True
            return batch

        # Category has less or equal number of elements than batch size. The batch will be
        # the category itself. Nothing to do.
        if len(category.items) <= self.batch_size:
            batch.items = category.items
            return batch

        sorted_items = sorted(category.items, key=lambda item: item.views, reverse=True)

        # If no element has reached max_views, take the first batch_size elements
        # When batch_size is greater or equal than the number of elements in the category,
        # it will return all the words in the category.
        if sorted_items[0].views < self.max_views:
            batch.items = sorted_items[: self.batch_size]
            return batch

        # Position of the first element with views below max_views
        pos = next(
            (i for i, item in enumerate(sorted_items) if item.views < self.max_views),
            None,
        )
        if pos > self.refresh_rate:
            pos = pos - pos % self.refresh_rate
        if len(sorted_items) - (pos + 1) >= self.batch_size:
            batch.items = sorted_items[pos : pos + self.batch_size]
        else:
            batch.items = sorted_items[len(sorted_items) - self.batch_size :]
        return batch

    def update_batch(self, batch):
        """Increases by one the count of views of every item in the batch"""
        try:
            sql_update_category_use = f"UPDATE Categories SET LastUse = '{dt.now().strftime('%Y/%m/%d')}' WHERE Id = {batch['id']}"
            db.run_sql(self.database, sql_update_category_use)
            item_ids = [item["Id"] for item in batch["Items"]]
            items = db.all_items(self.database)
            views = []
            for id in item_ids:
                found = next((x for x in items if x["Id"] == id), None)
                if found is not None:
                    views.append(found["Views"] + 1)
            updated_values = zip(views, item_ids)
            db.update_views(self.database, updated_values)
            return True
        except Exception as exception:
            print(f"Error: {exception.args}")
            return False

    def create_database(self, database: str) -> None:
        # db.run_script(database, "material_database.sql")
        db.run_script(self.database, "material_database.sql")

    def add_category(self, category: Category) -> None:
        db.create_category(self.database, category)

    # def save_categories(self, dbjson):
    #     with open(dbjson, "w") as db:
    #         json.dump(self.categories, db, cls=CategoryEncoder)
