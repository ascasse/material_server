from datetime import date
from json import JSONEncoder
import model


class ModelEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, model.Category):
            return o.__dict__
        if isinstance(o, model.Item):
            return o.__dict__

        return super().default(o)
