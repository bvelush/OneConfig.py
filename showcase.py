
from OneConfig.Cfg import Cfg

cfg = Cfg()
cfg2 = Cfg()

cfg.add_store('aa', 'bb')

cfg.print_stores()
cfg2.print_stores()

