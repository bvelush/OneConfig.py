from enum import Enum
import json

from .. import Const


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

        # choises are sorted by likelihood of appearence, for efficiency
        if isinstance(val, str):
            self._type = StoreResult.ResultTypes.VAL_STRING

        # int type    
        elif isinstance(val, int):
            self._type = StoreResult.ResultTypes.VAL_INT

        # condition for a value being a sensor record:
        # 1. type is dictionaly (more strict, a OneConfig.Util.CaseInsensitiveDict.CaseInsensitiveDict)
        # 2. there is only one record in this dicionary
        # 3. and it starts with sensor prfix syntax
        elif isinstance(val, dict):
            keys = list(val.keys())
            if len(keys) == 1 and keys[0].startswith(Const.SENSOR_PREFIX):
                self._value = {
                    Const.SENSOR_RESULT_NAME: keys[0][2:].upper(),
                    Const.SENSOR_RESULT_VALUES: val[keys[0]]
                }
                self._type = StoreResult.ResultTypes.VAL_SENSOR
            
        elif isinstance(val, list):
            self._type = StoreResult.ResultTypes.VAL_LIST

    def get(self):
        return self._value

    @property
    def type(self):
        return self._type
