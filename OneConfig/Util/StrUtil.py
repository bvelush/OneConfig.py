# pylint: disable=invalid-name
from typing import Tuple
from .. import Const

def split_key(key: str) -> Tuple[str, str]:
    '''
    Returns head and tail of the string key.
    Head and tail are defined as <head>.<tail>
    .tail is optional; in this case the entire key is returned
    '''
    pos = key.find('.')
    if pos < 0: # subkeys separator is not found
        return (key, '')

    return key[:pos], key[pos+1:]

def find_sensor_in_key(key: str) -> Tuple[str, str]:
    '''
    ### Separates the store key to the config and sensor parts
    In OneConfig, the full key consists of:
    - [optional] store_key: $store_key.
    - config_key: subkey1.subkey2
    - [optional] sensor_key: ?sensor_key

    ### input: config_key?sensor_key
    ### output: (config_key, sensor_key). Sensor key length will be 0 if sensor is not present
    Example:
    - for 'some.config.key?DEV' return will be ('some.config.key', 'DEV')
    - for 'some.other.key' will return ('some.other.key', '')
    '''
    sensor_position = key.find(Const.SENSOR_DELIMITER)
    sensor_present = sensor_position >= 0
    if sensor_present:
        return key[:sensor_position], key[sensor_position+1:]
    return key, ''

