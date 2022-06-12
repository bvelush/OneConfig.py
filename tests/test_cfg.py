# pylint: disable=redundant-unittest-assert
# pylint: disable=protected-access

from pathlib import Path
from context import Cfg
from context import Errors
from context import IStore
from context import JsonFileStore

import unittest
from unittest.mock import patch

class TestCfg(unittest.TestCase):

    test_cases = [
        ['$sec.dbuser.detected.?:deploy.specified', 'Explicit Sensor notation is working', 'Explicitly specified sensor "some.key?:sensor.value" expected to work'], 
        # ['$sec.dbuser.recursive_key1', 'the_actual_value="Running NOT under VSCode debugger"', 'sensor is resolved and inner_key rendered'],
        ['$sec.dbuser.recursive_key2', 'the_actual_value="Running NOT under VSCode debugger"&pwd="My Precious App: Enjoy!"', 'sensor is resolved and inner_key rendered']
    ]

    def test_inner_get_cases(self):
        cfg = Cfg()
        for test_case in self.test_cases:
            result = cfg._inner_get(test_case[0], 0)
            expected = test_case[1]
            message = test_case[2]
            self.assertEqual(result, expected, message)
        


    def test_inner_get_fails_when_debugged_specially(self):
        cfg = Cfg()
        result = cfg._inner_get('$sec.dbuser.recursive_key1', 0)
        self.assertEqual(result, 'the_actual_value="Running NOT under VSCode debugger"')
        
        # attention: this will be true in case of debug:
        # self.assertEqual(result, 'the_actual_value="Sensor feeling the ENVVAR"')

        # with patch('glob.glob') as mock_glob:
        #     with patch('pathlib.Path.cwd') as mock_cwd:
        #         root = Path('/dir/app')
        #         mock_cwd.return_value = root
        
        #         # case of no stores found
        #         mock_glob.return_value = []
        #         try:
        #             Cfg()
        #             self.assertTrue(False, 'Should raise StoreNotFound error')
        #         except Errors.StoreNotFound:
        #             self.assertTrue(True)

        #         # case of more than one found
        #         with self.assertLogs() as logs:
        #             mock_glob.return_value = ['aa', 'bb']
        #             Cfg()
        #             self.assertEqual(len(logs.records), 3)
        #             self.assertIn('')

        #         # case of one store found
        #         with self.assertLogs() as logs:
        #             mock_glob.return_value = ['aa']
        #             Cfg()
        #             self.assertEqual(len(logs.records), 2)
        #             self.assertEqual(logs.records[0].levelname, 'INFO')
                