import json
from .EnvSensor import EnvSensor

class DomainSensor(EnvSensor):
    def __init__(self, sensor_name: str):
        super().__init__(sensor_name, 'USERDOMAIN') # TODO remove after the demo =DESKTOP-MH2AMRE for demo

    @classmethod
    # pylint disable=unused-argument
    def from_json_params(cls, sensor_name: str, params: json) -> 'EnvSensor':
        return DomainSensor(sensor_name)
