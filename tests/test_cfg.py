from context import Cfg
from context import IStore
from context import JsonStore

import unittest

class TestCfg(unittest.TestCase):

    def test_get(self):
        cfg = Cfg()
        cfg.get('aa')
        cfg.get('aa.bb')
        cfg.get('$aa.bb')