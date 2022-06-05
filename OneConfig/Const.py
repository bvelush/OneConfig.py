CFG_INIT_ATTR = 'ONECONFIG'
CFG_STORES_ATTR = "STORES"
CFG_SENSORS_ATTR = "SENSORS"

KEY_MAX_LEVELS = 15 # max keys nesting: k1.k2.k3...k15 max
KEY_MAX_LEN = 32 # max length of the subkey: any of k1.k2... should be less or equal to MAX_SUBKEY_LEN

STORE_DEFAULT_PARAMS = '''
{
    "default": {
            "path": "./oneconfig.json"
        }
}
'''
STORE_PATH_ATTR = 'path'
STORE_APPROOT_TEMPLATE = '%APP_ROOT%'
STORE_NAME_TEMPLATE = '*.cfg.json'

SENSOR_DELIMITER = '?'
SENSOR_PREFIX = '?:'
SENSOR_RESULT_NAME = 'sensor'
SENSOR_RESULT_VALUES = 'values'
SENSOR_DEFAULT = 'DEFAULT'
