""" Model """
import datetime
from dataclasses import dataclass, field
from typing import List
import inspect


@dataclass
class Item:
    """An element containing a text and optionally the location of an image."""

    Text: str
    Image: str = None
    Views: int = 0
    LastUse: datetime.date = None
    Id: int = 0


@dataclass
class Category:
    """Container for a group of related items."""

    Name: str = field()
    Items: List = field(default_factory=list)
    LastUse: datetime.datetime = field(default=None)
    Completed: bool = False
    Type: int = 0
    Id: int = field(default=0)


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


def from_dict(cls, data):
    return cls(
        **{
            key: (data[key] if val.default == val.empty else data.get(key, val.default))
            for key, val in inspect.signature(cls).parameters.items()
        }
    )
