from enum import Enum, auto
import json

from .. import Const


class StoreResult:

    class ResultTypes(Enum):
        VAL_UNDEFINED = auto()
        VAL_INT = auto()
        VAL_STRING = auto()
        VAL_LIST = auto()
        # VAL_SENSOR = auto()
        VAL_SENSOR_KEYS = auto() # keys are CAPITALIZED for better comparison
        VAL_OBJECT_KEYS = auto() # keys are CAPITALIZED for better comparison

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
        # 3. and it starts with sensor prefix syntax
        elif isinstance(val, dict):
            keys = list(val.keys())
            if len(keys) == 1 and keys[0].startswith(Const.SENSOR_PREFIX):
                self._value = {
                    Const.SENSOR_RESULT_NAME: 
                        keys[0][len(Const.SENSOR_PREFIX):].upper(), # cutting off the sensor preffix
                    Const.SENSOR_RESULT_KEYS: 
                        list([key.upper() for key in val[keys[0]].keys()])
                }
                self._type = StoreResult.ResultTypes.VAL_SENSOR_KEYS
            
            else: # value is an object, but not a sensor
                self._type = StoreResult.ResultTypes.VAL_OBJECT_KEYS
                self._value = list([key.upper() for key in val.keys()])
            
        elif isinstance(val, list):
            self._type = StoreResult.ResultTypes.VAL_LIST

    @property
    def value(self):
        return self._value

    @property
    def type(self):
        return self._type
