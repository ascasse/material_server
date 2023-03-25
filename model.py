""" Model """
import datetime
from dataclasses import dataclass, field
from typing import List


@dataclass
class Item:
    """An element containing a text and optionally the location of an image."""

    text: str
    image: str = None
    views: int = 0
    last_view: datetime.date = None
    id: int = 0


@dataclass
class Category:
    """Container for a group of related items."""

    name: str = field()
    items: List = field(default_factory=list)
    last_view: datetime.datetime = field(default=None)
    completed: bool = False
    type: int = 0
    id: int = field(default=0)


@dataclass
class ItemDb:
    text: str
    image: str = None
    views: int = 0
    last_view: str = None
    id: int = 0

    def __init__(self, item: Item):
        self.text = item.text
        self.image = item.image
        self.views = item.views
        self.last_view = (
            None if item.last_view is None else item.last_view.strftime("%Y/%m/%d")
        )
        self.id = item.id
