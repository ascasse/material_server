"""
    Material service
"""
import json
from datetime import datetime as dt, timedelta

# from model import Category, CategoryEncoder

from model import Category, Item


class MaterialJsonService:
    """Material service based on json data"""

    def __init__(self, database=None):

        self.recent_count = 5  # Max number of recently viewed categories to return.
        self.recent_days = 7  # Date range to look for recently viewed items, in days.
        self.batch_size = 10  # Max number of elements returned in a batch.
        self.max_views = 5  # Max times a given element is included in a batch.
        self.refresh_rate = 3  # Number of elements replaced when a batch is updated.
        self.same_day_count = (
            True  # Set whether should update views counter for the same day.
        )
        self.database = database  # database

        # # Load categories
        # with open(database, "r") as db:
        #     data = json.load(db)
        #     self.categories = [Category(dct) for dct in data]

    def load(self):
        with open(self.database, "r") as db:
            data = json.load(db)
            self.categories = []
            for dct in data:
                self.categories.add(Category(dct["id"]))
            self.categories = [Category(dct) for dct in data]

    def get_all_items(self):
        return [item for cat in self.categories for item in cat.items]

    def get_recent(self):
        """Get recently viewed categories"""
        recent = [
            x
            for x in self.categories
            if x.lastseen is not None
            and x.lastseen >= dt.today().date() - timedelta(days=self.recent_days)
        ]
        return recent

    def get_batch(self, category: Category):
        """Build a new batch from the given category"""
        batch = Category({"id": category.id, "name": category.name})

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
        item_ids = [item.id for item in batch.items]
        items = self.get_all_items()
        for id in item_ids:
            found = next((x for x in items if x.id == id), None)
            if found is not None:
                found.views += 1
        self.save_categories(self.database)

    def save_categories(self, dbjson):
        with open(dbjson, "w") as db:
            json.dump(self.categories, db, cls=CategoryEncoder)
