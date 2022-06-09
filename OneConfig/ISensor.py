# pylint: disable=invalid-name

import json
from pydoc import locate

from OneConfig import Errors
from OneConfig import Const

class ISensor:
    
    def __init__(self):
        pass
    
    @classmethod
    def from_json_params(cls, name: str, params: json) -> 'ISensor':
        raise NotImplementedError('this method has to be overloaded in subclasses')

    @classmethod
    def load_sensor_dynamically(cls, sensor_config: json) -> 'ISensor':
        sensor_name = list(sensor_config.keys())[0]
        if not sensor_name.startswith(Const.SENSOR_PREFIX):
            raise Errors.SensorInitError(f'Sensor Name "{sensor_name} is expected to start with "{Const.SENSOR_PREFIX}"')
        
        sensor_type = sensor_config[sensor_name][Const.SENSOR_TYPE_ATTR]
        sensor_class = locate(sensor_type)
        if not issubclass(sensor_class, ISensor):
            raise Errors.SensorInitError(f'Class "{sensor_class}" defined by "{Const.STORE_TYPE_ATTR}" in configuration, is expected to be an "ISensor" instance ')
        sensor = sensor_class.from_json_params(sensor_name, sensor_config[sensor_name][Const.SENSOR_PARAMS_ATTR])
        return sensor

    @property
    def name(self) -> str:
        '''
        ***OVERRIDE IT***
        Returns the ID of the store
        '''
        raise NotImplementedError('this method has to be overloaded in subclasses')

    def get(self) -> str:
        raise NotImplementedError('this method has to be overloaded in subclasses')
