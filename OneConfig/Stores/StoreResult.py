from enum import Enum
import json


class StoreResult:

    class ResultTypes(Enum):
        VAL_UNDEFINED = 0,
        VAL_INT = 1,
        VAL_STRING = 2,
        VAL_LIST = 3,
        VAL_SENSOR = 4,
        VAL_SENSOR_KEYS = 5

    '''
        syntax:

        {
            "key": { # get("key")
                "?:SENSOR_NAME": {
                    "S_VAL1": "val1",
                    "S_VAL2": "val2", # get("key.?:SENSOR_NAME.S_VAL2")
                    "S_VAL3": "val3"
                }
            }
        }

        types:
            VAL_INT
            VAL_STRING
            * VAL_ARRAY
            * VAL_OBJECT
            VAL_SENSOR (sensor_name and all KVs)
            VAL_SENSOR_KEYS (sensor_name and keys only; need to resolve sensor and then re-query with direct sensor syntax)
    '''




    def __init__(self, val):
        self._type = StoreResult.ResultTypes.VAL_UNDEFINED
        self._value = val
        if isinstance(val, int):
            self._type = StoreResult.ResultTypes.VAL_INT
        elif isinstance(val, str):
            self._type = StoreResult.ResultTypes.VAL_STRING
        elif isinstance(val, list):
            self._type = StoreResult.ResultTypes.VAL_LIST

    def get(self):
        return self._value

    @property
    def type(self):
        return self._type
