# pylint: disable=redundant-unittest-assert
# pylint: disable=protected-access

from unittest import TestCase, mock
import json
import os

from context import ISensor
from context import EnvSensor


class Test_EnvSensor(TestCase):

    sensor_definition = json.loads('''
        {
            "sensor_env_exists": {
                "type": "OneConfig.Sensors.EnvSensor.EnvSensor",
                "params": {
                    "envvar": "DEF"
                }
            },

            "sensor_no_env": {
                "type": "OneConfig.Sensors.EnvSensor.EnvSensor",
                "params": {
                    "envvar": "abc"
                }
            }
        }
    ''')

    @mock.patch.dict(os.environ, {'def': 'test_value'})
    def test_get(self):
        sensor_name = '?:test_sensor1'
        sensor = ISensor.load_sensor_dynamically(sensor_name, self.sensor_definition['sensor_env_exists'])
        self.assertEqual(sensor.name, sensor_name)
        result = sensor.get()
        self.assertEqual(result, 'test_value'.upper()) # EnvSensor always returns capitalized results

        sensor_name = '?:test_sensor2'
        sensor = ISensor.load_sensor_dynamically(sensor_name, self.sensor_definition['sensor_no_env'])
        self.assertEqual(sensor.name, sensor_name)
        result = sensor.get()
        self.assertEqual(result, 'DEFAULT')

