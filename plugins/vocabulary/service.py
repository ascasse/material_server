"""
    Vocabulary service
"""

from loginit import logger
from plugins.vocabulary.db_words import DBWords


class Service:
    """ Vocabulary service"""

    def __init__(self, database=None):
        super().__init__()

        self.db_words = DBWords(database)

        # Max number of recently viewed categories to return.
        self.recent_count = 5
        # Date range to look for recently viewed categories or words, in days.
        self.recent_days = 7
        # Max number of elements returned in a batch.
        self.batch_size = 10
        # Max times a given element is included in a batch.
        self.max_views = 5
        # Number of elements replaced when a batch is updated.
        self.refresh_rate = 3
        # Set whether should update views counter for the same day.
        self.same_day_count = True

    def get_categories(self):
        """ Retrieve all categories."""
        return self.db_words.select_categories()

    def get_category(self, category_id):
        """ Retrieve a category by id."""
        return self.db_words.select_category(category_id)

    def create_category(self, category):
        """ Create a new category."""
        try:
            return self.db_words.create_category(category)
        except Exception as exc:
            logger.error(exc.args[0])
            raise Exception(exc.args[0])

    def delete_category(self, category_id):
        """ Remove a category from the database."""
        return self.db_words.delete_category(category_id)

    def update_category(self, category):
        """ Update a category

            Allowed changes:
            - name and lastUse
            - add or remove words
            - lastUse and views for words
        """

        try:
            current = self.db_words.select_category(category["id"])
            if (category["name"] != current["name"]) or (
                    category["lastUse"] != current["lastUse"]
            ):
                self.db_words.update_category(current)

            to_keep, to_delete, to_add = merge_words(
                current["words"], category["words"]
            )
            to_update = []
            for keep_word in to_keep:
                current_word = next(
                    (x for x in current["words"]
                     if x["id"] == keep_word["id"]), None
                )
                if current_word is None:
                    continue
                different_values = {
                    k: current_word[k]
                    for k in current_word
                    if k in keep_word and current_word[k] != keep_word[k]
                }
                if different_values:
                    to_update.append(keep_word)

            if to_update:
                self.db_words.update_words(to_update)
            if to_delete:
                self.db_words.delete_words(to_delete)
            if to_add:
                self.db_words.create_words(to_add, current["id"])

            return category["id"]
        except Exception as exc:
            logger.error(exc.args[0])
            raise Exception(exc.args[0]) from exc

    def update_views(self, batch):
        """ Updates view info of given words.

            For each word increases views by one and set lastUse date as today.
            Updates category lastUse to today.

            Parameters:

                category_id: int Category id
                words: string Comma separated list of words
        """

        updated = self.db_words.update_views(batch)
        return updated

    def get_recent(self):
        """Get recently used categories.

            Retrieve up to recent_count categories.

            The number of elements in each category does not exceed batch_size.

            In order to create the list of elements included:
            - Exclude elements that have reached the max number of uses.
            - If remaining elements do not add up to batch size, complete with elements
              excluded in the previous step, starting with the ones less viewed.

            Return:

                list(category). List of batches
        """

        categories = self.db_words.get_recent(
            self.recent_days, self.recent_count)
        recent = []
        for category_id in [c["id"] for c in categories]:
            recent.append(self.build_batch_from_category_id(category_id))
        return recent

    def build_batch_from_category_id(self, category_id):
        """ Build a new batch from a category."""
        category = self.db_words.select_category(category_id)
        return self.build_batch_from_category(category)

    def build_batch_from_category(self, category):
        """ Build a new batch from the given category."""
        batch = {"id": category["id"], "name": category["name"]}

        # All elements have reached max_views. Mark as completed and terminate
        to_view = [w for w in category["words"] if w["views"] < self.max_views]
        if not to_view:
            batch["completed"] = True
            return batch

        # Category has less or equal number of elements than batch size. The batch will be
        # the category itself. Nothing to do.
        if len(category["words"]) <= self.batch_size:
            batch["words"] = category["words"]
            return batch

        sorted_words = sorted(
            category["words"], key=lambda w: w["views"], reverse=True)

        # If no element has reached max_views, take the first batch_size elements
        # When batch_size is greater or equal than the number of elements in the category,
        # it will return all the words in the category.
        if sorted_words[0]["views"] < self.max_views:
            batch["words"] = sorted_words[: self.batch_size]
            return batch

        # Position of the first word with views below max_views
        pos = next(
            (i for i, w in enumerate(sorted_words)
             if w["views"] < self.max_views), None
        )
        if pos > self.refresh_rate:
            pos = pos - pos % self.refresh_rate
        if len(sorted_words) - (pos + 1) >= self.batch_size:
            batch["words"] = sorted_words[pos: pos + self.batch_size]
        else:
            batch["words"] = sorted_words[len(sorted_words) - self.batch_size:]
        return batch


def merge_words(current_words, new_words):
    """ Determine words to add and delete for words update.

        Parameters:

            list(dict). Currently existing words
            list(dict). Words after update

        Return:

            list(dict). Words to keep
            list(dict). Words to remove
            list(dict). Words to add
    """
    to_keep = []
    to_delete = []
    for word in current_words:
        found = next(
            (item for item in new_words if item["word"] == word["word"]), None)
        if found:
            to_keep.append(found)
        else:
            to_delete.append(word)

    curr = [item["word"] for item in current_words]
    to_add = [item for item in new_words if item["word"] not in curr]
    return to_keep, to_delete, to_add


def update_words_nodict(current_words, new_words):
    """ Determine words to add and delete for words update.

        Parameters:

            list(string). Currently existing words
            list(string). Words after update

        Return:

            list(string). Words to keep
            list(string). Words to remove
            list(string). Words to add
    """
    to_keep = [item for item in current_words for x in new_words if x in item]
    to_delete = [item for item in current_words if item[1] not in new_words]
    curr = [item[1] for item in current_words]
    to_add = [item for item in new_words if item not in curr]
    return to_keep, to_delete, to_add
