"""
    Material service
"""
from copy import deepcopy
from dataclasses import fields
from datetime import datetime as dt

from typing import List

from model import Category, Item
from repository import Repository


class MaterialService:
    def __init__(self, repository: Repository):

        self.repository = repository
        self.recent_count = 5  # Max number of recently viewed categories to return.
        self.recent_days = 7  # Date range to look for recently viewed items, in days.
        self.batch_size = 5  # Max number of elements returned in a batch.
        self.max_views = 5  # Max times a given element is included in a batch.
        self.refresh_rate = 3  # Number of elements replaced when a batch is updated.
        self.same_day_count = (
            True  # Set whether should update views counter for the same day.
        )
        self.categories = []

    def get_info(self) -> tuple:
        return self.repository.get_info()

    def get_all_items(self) -> List[Item]:
        """Retrieve all items in the database."""
        return self.repository.all_items()

    def get_item(self, item_id: int) -> Item:
        """Retrieve the item with the given id."""
        items = self.repository.get_item(item_id)
        return items[0] if len(items) > 0 else None

    def get_category(self, category_id: int) -> Category:
        """Retrieve the category with the given id."""
        rows = self.repository.get_category(category_id)
        category = Category(
            id=category_id, name=rows[0]["Name"], last_view=rows[0]["c_LastUse"]
        )
        category.items = [
            Item(
                id=r["it_id"],
                image=r["Image"],
                last_view=r["LastUse"],
                text=r["Text"],
                views=r["Views"],
                type=r
            )
            for r in rows
        ]
        return category

    def get_recent(self):
        """Get recently viewed categories"""
        recent_dict = self.repository.get_recent(self.recent_count)
        recent = [self.map_to_category(rec) for rec in recent_dict]

        # Load items for selected categories
        ids = [x.id for x in recent]
        recent_items = self.repository.get_recent_items(ids)
        for category in recent:
            category.items = [
                self.map_to_item(item)
                for item in recent_items
                if item["CategoryId"] == category.id
            ]

        batches = [self.get_batch(category) for category in recent]
        return batches

        # return recent

    def get_batch(self, category: Category):
        """Build a new batch from the given category"""

        batch = deepcopy(category)
        # batch = Category(
        #     id=category.id,
        #     name=category.name,
        #     items=category.items,
        #     last_view=category.last_view,
        # )

        # Look for elements that have not reached max_views
        to_view = self.to_view_items(batch)
        # All elements have reached max_views. Mark as completed and terminate
        if not to_view:
            batch.completed = True
            self.repository.mark_category_completed(category.id)
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
            last_use = dt.now()
            sql_update_category_use = (
                f"UPDATE Categories SET LastUse = '{last_use}' WHERE Id = {batch.id}"
            )
            self.repository.execute_statement(sql_update_category_use)

            item_ids = [item.id for item in batch.items]
            views = [item.views + 1 for item in batch.items]
            updated_values = list(zip(views, item_ids))

            sql = f"UPDATE Items SET LastUse = '{last_use}', Views = ? WHERE Id = ?"
            self.repository.execute_many(sql, updated_values)
            self.repository.commit()
            return True
        except AttributeError as attr_error:
            print(f"Attribute error: {attr_error.name}")
            return False
        except Exception as exception:
            print(f"Error: {exception.args}")
            return False

    def to_view_items(self, category: Category) -> List[Item]:
        """Return items in the category that have not yet reached max_views"""
        return [item for item in category.items if item.views < self.max_views]

    def create_database(self) -> None:
        # db.run_script(database, "material_database.sql")
        self.repository.run_script("material_database.sql")

    def add_category(self, category: Category) -> int:
        return self.repository.save_category(category)

    def map_from_dictionary(self, class_name, dictionary):
        class_fields = {f.name for f in fields(class_name) if f.init}
        args = {k: v for k, v in dictionary.items() if k in class_fields}
        return class_name(**args)

    def map_to_category(self, dct: dict) -> Category:
        return Category(name=dct["Name"], last_view=dct["LastUse"], id=dct["Id"])

    def map_to_item(self, dct: dict) -> Item:
        return Item(
            text=dct["Text"],
            last_view=dct["LastUse"],
            views=dct["Views"],
            image=dct["Image"],
            id=dct["Id"],
        )
