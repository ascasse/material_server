""" Abstract class for repositories """
from abc import ABC, abstractmethod
from typing import List
from model import Category, Item


class Repository(ABC):
    @abstractmethod
    def all_categories(self) -> List[dict]:
        pass

    @abstractmethod
    def all_categories2(self) -> List[dict]:
        pass

    @abstractmethod
    def category(self, category_id: int) -> List[dict]:
        pass

    @abstractmethod
    def all_items(self) -> List[dict]:
        pass

    @abstractmethod
    def save_category(self, category: Category) -> int:
        pass

    @abstractmethod
    def run_script(self, script: str):
        pass

    @abstractmethod
    def get_info(self):
        pass

    @abstractmethod
    def get_recent(self, count):
        pass

    @abstractmethod
    def get_recent_items(self, ids: List[int]):
        pass

    # @abstractmethod
    # def get_category(self, category_id: int) -> Category:
    #     pass

    @abstractmethod
    def get_item(self, item_id: int) -> Item:
        pass
