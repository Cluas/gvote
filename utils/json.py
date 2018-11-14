from datetime import datetime, date


def json_serializer(obj):
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError("Type {}s not serializable".format(type(obj)))
