"""
    Material model
"""
import datetime
from json import JSONEncoder


class Category(object):
    """A collection of information items"""

    def __init__(self, adict: dict):
        if not "name" in adict:
            raise Exception("Category name required")

        self.__dict__.update(adict)

        if not "id" in adict:
            self.id = 0

        lastseen_value = adict.get("lastseen", None)
        if lastseen_value is not None:
            if not isinstance(lastseen_value, datetime.date):
                try:
                    self.lastseen = datetime.datetime.strptime(
                        adict["lastseen"], "%Y/%m/%d"
                    ).date()
                except ValueError:
                    self.lastseen = None
        else:
            self.lastseen = None

        if not hasattr(self, "items"):
            self.items = []
        else:
            self.items = [Item(itemDict) for itemDict in self.items]
        # for item in enumerate(self.items):
        #     if not hasattr(item[1], 'views'):
        #         item[1].update({'views': 0})

    def __setattr__(self, name, value):
        if name == "lastseen":
            if value is not None and not isinstance(value, datetime.date):
                raise TypeError("Expected datetime instance")
        return super().__setattr__(name, value)

    def add_item(self, item):
        self.items.append(item)


class Item(object):
    """Element of information"""

    def __init__(self, adict):
        self.views = 0
        self.__dict__.update(adict)


class Batch(Category):
    """Subset of a Category"""

    def __init__(self, adict: dict):
        super().__init__(dict)
        self.completed = adict["completed"] if hasattr(adict, "completed") else False


class CategoryEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Category):
            return obj.__dict__
        if isinstance(obj, Item):
            return obj.__dict__
        if isinstance(obj, datetime.date):
            return obj.__str__()
        else:
            return ""
        return JSONEncoder.default(self, obj)


class Bit:
    """A bit represents an image file"""

    def __init__(self, title, imagefilepath, id_=0):
        self.id = id_
        self.title = title
        self.imagefilepath = imagefilepath


class Group(Category):
    """A group is a collection of related items, belonging to one or more categories."""

    def __init__(self, name, id_=0, items=None, lastseen=None):
        adict = dict({"name": name, "id": id_, "lastseen": lastseen, "items": items})
        super().__init__(adict)


def category_encoder(obj):
    if isinstance(obj, Group):
        return group_encoder(obj)
    elif isinstance(obj, Category):
        return {
            "id": obj.id,
            "name": obj.name,
            "items": [bit_encoder(img) for img in obj.items],
        }
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def bit_encoder(obj):
    if isinstance(obj, Bit):
        return {"id": obj.id, "title": obj.title, "imagefilepath": obj.imagefilepath}
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def group_encoder(obj):
    if isinstance(obj, Group):
        return {
            "id": obj.id,
            "name": obj.name,
            "lastseen": datetime_encoder(obj.lastseen),
            "items": [bit_encoder(img) for img in obj.items],
        }
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")


def datetime_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    else:
        return ""


def category_decoder(dct):
    if "title" in dct:
        return bit_decoder(dct)
    category = Category(dct)
    if "items" in dct:
        for bit in dct["items"]:
            category.add_item(bit)
    return category


def group_decoder(dct):
    if "title" in dct:
        return bit_decoder(dct)
    if "id" in dct:
        group = Group(dct["name"], dct["id"], [])
    else:
        group = Group(dct["name"])
    if "items" in dct:
        for bit in dct["items"]:
            if isinstance(bit, dict):
                group.add_item(bit_decoder(bit))
            else:
                group.add_item(bit)
    if "lastseen" in dct:
        try:
            strdate = datetime.datetime.strptime(dct["lastseen"], "%Y/%m/%d")
            group.lastseen = strdate
        except ValueError:
            group.lastseen = None
    return group


def bit_decoder(dct):
    return Bit(dct["title"], dct["imagefilepath"], id_=dct["id"])
