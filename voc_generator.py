from pathlib import Path
from typing import List
from repository import Repository


class VocabularyGenerator:
    """Fills repository from vocabulary files"""

    def __init__(self, base_path: str, repository: Repository):
        self.path = Path(base_path)
        self.repository = repository

    def load_categories(self) -> List:
        return self.process_dir(self.path)
