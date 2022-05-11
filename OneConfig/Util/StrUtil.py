from typing import Tuple

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