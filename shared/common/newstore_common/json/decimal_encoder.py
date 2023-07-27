import decimal
import json


class DecimalToStringEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


class DecimalToValueEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            if abs(obj) % 1 == 0:
                return int(obj)
            else:
                return round(float(obj), 5)
        return json.JSONEncoder.default(self, obj)