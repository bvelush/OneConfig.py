# pylint: disable=invalid-name
from .Errors import SensorNotImplemented

class ISensor:
    def get(self) -> str:
        raise SensorNotImplemented()