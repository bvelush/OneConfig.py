# pylint: disable=redundant-unittest-assert
# pylint: disable=protected-access

from unittest import TestCase, mock
import json
import os

from context import ISensor
from context import DomainSensor


class Test_DomainSensor(TestCase):

    sensor_definition = json.loads('''
        {
            "domain_sensor": {
                "type": "OneConfig.Sensors.DomainSensor.DomainSensor",
                "params": {
                }
            }
        }
    ''')

    @mock.patch.dict(os.environ, {'USERDOMAIN': 'test_domain'})
    def test_get_env_exists(self):
        sensor_name = '?:test_domain_sensor'
        sensor = ISensor.load_sensor_dynamically(sensor_name, self.sensor_definition['domain_sensor'])
        self.assertEqual(sensor.name, sensor_name)
        result = sensor.get()
        self.assertEqual(result, 'test_domain'.upper()) # EnvSensor always returns capitalized results

    @mock.patch('os.getenv', lambda x: None)
    def test_get_env_not_exists(self):
        sensor_name = '?:test_domain_sensor'
        sensor = ISensor.load_sensor_dynamically(sensor_name, self.sensor_definition['domain_sensor'])
        self.assertEqual(sensor.name, sensor_name)
        result = sensor.get()
        self.assertEqual(result, 'DEFAULT') # EnvSensor always returns capitalized results
