import os
from OneConfig.Cfg import Cfg

if __name__ == '__main__':
    os.environ['DEPLOY'] = 'DEV'
    os.environ['LANG'] = 'EN'
    os.environ['USERDOMAIN'] = 'EMEA'
    os.environ['PLATFORM'] = 'ARM'


    cfg = Cfg('%APP_ROOT%/Demo/demo1.cfg.json')
    res = cfg.get('Db.connstring')
    print(cfg)

