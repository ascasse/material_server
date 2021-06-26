from dataclasses import dataclass
from typing import ItemsView

import datetime
from dataclasses import dataclass
from model.item import Item


@dataclass
class Category:
    """A collection of items"""

    id: int
    name: str
    items: list
    last_seen: datetime.datetime

    def add_item(self, item: Item):
        """Adds a new item to the category"""
        self.items.add(item)
