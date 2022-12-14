import os
import logging
from OneConfig.Cfg import Cfg

logging.getLogger().setLevel(logging.DEBUG)

if __name__ == '__main__':


    cfg = Cfg('%APP_ROOT%/Demo/demo1.cfg.json')

    print('\n--- Simple things first ---')
    print(cfg.get("simple-string"))
    print(cfg.get("simpleint"), type(cfg.get("simpleint")))
    print(cfg.get("simple-Bool"), type(cfg.get("simple-bool")))
    print(cfg.get("Simple_Array"))

    print('\n--- Nesting -- up to 15 levels default ---')
    print(cfg.get("nesting.L2.L2value"))
    print(cfg.get("nesting.L2.L3.l3value"))
    
    print('\n--- References ---')
    print(cfg.get('References.SimpleReference'))
    print(cfg.get('References.EmbeddedReference'))

    print('\n--- Sensors. Things are getting a bit more interesting now ---')
    os.environ['DEMOVAR'] = 'Value1'
    print(cfg.get('Sensors.S1'))
    os.environ['DEMOVAR'] = 'Value2'
    print(cfg.get('Sensors.S1'))
    os.environ['DEMOVAR'] = 'kjkjk'
    print(cfg.get('Sensors.S1'))
    print(cfg.get('Sensors.S1.?:DEMOVAR.Value2'))

    print('--- Stores and cross-store references ---')
    print(cfg.get('$.SimpleInt'))
    print(cfg.get('$AnotherStore.same.features.work.here'))
    print(cfg.get('CrossStoreReference'))
    
    print('\n=== NOW we are aready for some fun ===\n')

    os.environ['DEPLOY'] = 'TEST'
    os.environ['LANG'] = 'EN'
    os.environ['USERDOMAIN'] = 'EMEA'

    print(cfg.get('UI.Name'))
    res = cfg.get('Db.connstring')
    print(res)

