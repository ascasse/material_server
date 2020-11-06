import json
import datetime


class Category:
    ''' A collection of images '''
    def __init__(self, name, id = 0, images = []):
        self.id = id
        self.name = name
        self.images = images

    def add_image(self, image):
        self.images.append(image)


class Bit:
    ''' A bit represents an image file '''
    def __init__(self, title, imagefilepath, id = 0):
        self.title = title
        self.imagefilepath = imagefilepath
        self.id = id

class Group(Category):
    ''' A group is a collection of related images, belonging to one or more categories. '''
    def __init__(self, name, id=0, images=[], lastseen=None):
        super().__init__(name, id, images)
        self.lastseen = lastseen

    def __setattr__(self, name, value):
        if name == 'lastseen':
            if value is not None and not isinstance(value, datetime.datetime):
                raise TypeError('Expected datetime instance')
        return super().__setattr__(name, value)


def category_encoder(obj):
    if isinstance(obj, Group):
        return group_encoder(obj)
    elif isinstance(obj, Category):
        return {
            'id' : obj.id,
            'name' : obj.name,
            'images': [bit_encoder(img) for img in obj.images]
        }      
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

def bit_encoder(obj):
    if isinstance(obj, Bit):
        return {
            'id' : obj.id,
            'title' : obj.title,
            'imagefilepath' : obj.imagefilepath
        }
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

def group_encoder(obj):
    if isinstance(obj, Group):
        return {
            'id' : obj.id,
            'name' : obj.name,
            'lastseen' : datetime_encoder(obj.lastseen),
            'images': [bit_encoder(img) for img in obj.images]
        }
    else:
        type_name = obj.__class__.__name__
        raise TypeError(f"Object of type '{type_name}' is not JSON serializable")

def datetime_encoder(obj):
    if isinstance(obj, datetime.datetime):
        return obj.__str__()
    else:
        return ''

def category_decoder(dct):
    if 'title' in dct:
        return bit_decoder(dct)
    category = Category(dct['name'], dct['id'], [])
    if 'images' in dct:
        for bit in dct['images']:
            category.add_image(bit)
    return category

def group_decoder(dct):
    if 'title' in dct:
        return bit_decoder(dct)
    if 'id' in dct:
        group = Group(dct['name'], dct['id'], [])
    else:
        group = Group(dct['name'])
    if 'images' in dct:
        for bit in dct['images']:
            if isinstance(bit, dict):
                group.add_image(bit_decoder(bit))
            else:
                group.add_image(bit)
    if 'lastseen' in dct:
        try:
            s = datetime.datetime.strptime(dct['lastseen'], '%Y/%m/%d')
            group.lastseen = s
        except:
            group.lastseen = None
    return group

def bit_decoder(dct):
    return Bit(dct['title'], dct['imagefilepath'], id=dct['id'])


