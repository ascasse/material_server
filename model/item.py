import datetime
from dataclasses import dataclass


@dataclass
class Item:
    id: int
    title: str
    image: str
    last_seen: datetime
