""" Test program to verify batch updates"""

from material_service import MaterialService
from sqlite_repository import SQLiteRepository
from model import Category, Item


def print_batch_info(current_batch: Category):
    print("-------------------------------")
    print(f"{current_batch.id} {current_batch.name} {current_batch.last_view}")
    for item in current_batch.items:
        print(f"{item.id}, {item.text} {item.last_view}, {item.views}")
    print("-------------------------------")


repository = SQLiteRepository(db_location=":memory:")
service = MaterialService(repository)

# Populate database with test data
repository.run_script("./Material_database.sql")
test_categories = [
    Category(
        name=f"category{m:02}",
        items=[Item(text=f"item{n:02}") for n in range(10 * (m - 1) + 1, 10 * m + 1)],
    )
    for m in range(1, 11)
]
for category in test_categories:
    repository.save_category(category)

# Get batch
category = service.get_category(1)
batch = service.get_batch(category)
print_batch_info(batch)

for view in range(15):
    service.update_batch(batch)
    category = service.get_category(1)
    batch = service.get_batch(category)
    if batch.completed:
        print("Completed")
        break
    print(f"View: {view + 1}")
    print_batch_info(batch)
