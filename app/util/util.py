import typing
from sqlalchemy import inspect
import os


def get(_dict:dict, key: typing.Any, default: typing.Any = None) -> typing.Any:
    if key in _dict:
        return _dict[key]
    return default

def object_as_dict(obj):
    return {c.key: getattr(obj, c.key)
            for c in inspect(obj).mapper.column_attrs}
    
    
def is_prod():
    ENVIRONMENT = os.environ.get('PRODUCTION')
    
    if ENVIRONMENT.find('prod') >= 0:
        return True
    
    return False