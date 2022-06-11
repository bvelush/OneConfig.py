# pylint: disable=invalid-name
import json
import logging
import os

# pylint: disable=relative-beyond-top-level
from .. import Const
from ..ISensor import ISensor 

class EnvSensor(ISensor):
    _logger = logging.getLogger(__name__)

    @classmethod
    def from_json_params(cls, sensor_name: str, params: json) -> 'EnvSensor':
        envvar_name = params[Const.ENV_SENSOR_VAR_ATTR]
        return EnvSensor(sensor_name, envvar_name)

    def __init__(self, sensor_name: str, envvar_name: str):
        self._name = sensor_name
        self._envvar_name = envvar_name

    @property
    def name(self) -> str:
        return self._name

    def get(self) -> str:
        envvar_value = os.getenv(self._envvar_name)
        if envvar_value is None:
            self._logger.warning(f'Environment variable "{self._envvar_name}" the sensor definition "{self.name}" is not found')
            return Const.SENSOR_DEFAULT.upper()
        
        return envvar_value.upper()