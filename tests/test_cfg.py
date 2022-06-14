# pylint: disable=redundant-unittest-assert
# pylint: disable=protected-access
import os
from unittest import TestCase, mock

from context import Cfg


class TestCfg(TestCase):

    test_cases = [
        ['$sec.dbuser.detected.?:deploy.specified', 'Explicit Sensor notation is working', 'Explicitly specified sensor "some.key?:sensor.value" expected to work'], 
        ['$sec.dbuser.recursive_key1', 'the_actual_value="Running NOT under VSCode debugger"', 'sensor is resolved and inner_key rendered'],
        ['$sec.dbuser.recursive_key2', 'the_actual_value="Running NOT under VSCode debugger"&pwd="My Precious App: Enjoy!"', 'sensor is resolved and inner_key rendered']
    ]

    @mock.patch.dict(os.environ, {'ABC': 'PROD'})
    def test_inner_get_cases(self):
        cfg = Cfg('%APP_ROOT%/OneConfig')
        for test_case in self.test_cases:
            result = cfg.get(test_case[0])
            expected = test_case[1]
            message = test_case[2]
            self.assertEqual(result, expected, message)

    def test_inner_get_fails_when_debugged_specially(self):
        cfg = Cfg('%APP_ROOT%/OneConfig'
        )
        result = cfg.get('$sec.dbuser.recursive_key1')
        self.assertEqual(result, 'the_actual_value="Running NOT under VSCode debugger"')
        
