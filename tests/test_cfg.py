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

    def test_find_default_store_path(self):
        cfg = Cfg()

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
                