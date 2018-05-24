import json
import pandas as pd


class JSONEncoder(json.JSONEncoder):

    def encode_json(self, obj):
        if hasattr(obj, 'toJSON'):
            return obj.toJSON()
        elif isinstance(obj, pd.DataFrame):
            return obj.to_dict()
        elif isinstance(obj, dict):
            d = {}

            for k, v in obj.items():
                d[k] = self.encode_json(v)

            return d
        elif isinstance(obj, list):
            arr = []

            for x in obj:
                arr.append(self.encode_json(x))

            return arr
        else:
            return obj

    def default(self, obj):
        stringified = self.encode_json(obj)
        return json.dumps(stringified)
