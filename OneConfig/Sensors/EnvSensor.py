# pylint: disable=invalid-name
import json
import logging
import os

# pylint: disable=relative-beyond-top-level
from .. import Const
from ..ISensor import ISensor 

class EnvSensor(ISensor):
    _logger = logging.getLogger(__name__)

    def __init__(self, sensor_name: str, envvar_name: str):
        super().__init__(sensor_name)
        
        self._envvar_name = envvar_name

    @classmethod
    def from_json_params(cls, sensor_name: str, params: json) -> 'EnvSensor':
        envvar_name = params[Const.ENV_SENSOR_VAR_ATTR]
        return EnvSensor(sensor_name, envvar_name)


    def get(self) -> str:
        envvar_value = os.getenv(self._envvar_name)
        if envvar_value is None:
            self._logger.warning(f'Environment variable "{self._envvar_name}" the sensor definition "{self.name}" is not found')
            return Const.SENSOR_DEFAULT.upper()
        
        ret_val = envvar_value.upper()
        self._logger.debug(f'EnvSensor "{self.name}" for envvar "{self._envvar_name}" is resolved as "{ret_val}"')
        return ret_val
