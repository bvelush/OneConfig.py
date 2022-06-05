from importlib.resources import path
from context import Cfg
from context import Errors
from context import IStore
from context import JsonFileStore

import unittest
from unittest.mock import patch

class TestCfg(unittest.TestCase):

    # def test_get(self):
    #     # glob.glob(pathname)  glob.glob('**/*.cfg.json', root_dir=os.getcwd(), recursive=True)
    #     cfg = Cfg()
    #     # cfg.get('aa')
    #     # cfg.get('aa.bb')
    #     # cfg.get('$aa.bb')

    def test_find_default_store(self):
        with patch('glob.glob') as mock_glob:
        
            # case of no stores found
            mock_glob.return_value = []
            try:
                Cfg()
                self.assertTrue(False, 'Should raise StoreNotFound error')
            except Errors.StoreNotFound:
                self.assertTrue(True)

            # case of more than one found
            with self.assertLogs() as logs:
                mock_glob.return_value = ['aa', 'bb']
                Cfg()
                self.assertEqual(len(logs.records), 2)
                self.assertEqual(logs.records[0].levelname, 'WARNING')

            # case of one store found
            with self.assertLogs() as logs:
                mock_glob.return_value = ['aa']
                Cfg()
                self.assertEqual(len(logs.records), 1)
                self.assertEqual(logs.records[0].levelname, 'INFO')
                