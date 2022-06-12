CFG_INIT_ATTR = 'ONECONFIG'
CFG_STORES_ATTR = "STORES"
CFG_SENSORS_ATTR = "SENSORS"
CFG_MAX_RECURSION = 5

KEY_MAX_LEVELS = 15 # max keys nesting: k1.k2.k3...k15 max
KEY_MAX_LEN = 32 # max length of the subkey: any of k1.k2... should be less or equal to MAX_SUBKEY_LEN

STORE_PREFIX = '$'  # also this one is the name of the default store: it's a store without a name, only with the prefix
STORE_DEFAULT_CONFIG = '''
{
    "type": "OneConfig.Stores.JsonFileStore.JsonFileStore",
    "params": {
        "path": "%s"
    }
}
'''
STORE_TYPE_ATTR = 'type'
STORE_PARAMS_ATTR = 'params'
STORE_PATH_ATTR = 'path'
STORE_APPROOT_TEMPLATE = '%APP_ROOT%'
STORE_NAME_TEMPLATE = '*.cfg.json'

SENSOR_PREFIX = '?:'
SENSOR_TYPE_ATTR = 'type'
SENSOR_PARAMS_ATTR = 'params'
SENSOR_RESULT_NAME = 'SENSOR'
SENSOR_RESULT_KEYS = 'KEYS'
SENSOR_DEFAULT = 'DEFAULT'

ENV_SENSOR_VAR_ATTR = 'envvar' # What environment variable should EnvSensor resolve 
