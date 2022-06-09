
class OneConfigError(Exception):
    pass

class TraverseProblem(OneConfigError):
    pass

class KeyProblem(OneConfigError):
    pass

class StoreNotFound(OneConfigError):
    pass

class StoreOpenError(OneConfigError):
    pass

class StoreInitError(OneConfigError):
    pass

class SensorInitError(OneConfigError):
    pass

class SensorNotFound(OneConfigError):
    pass

class ErrorConfigLookup(OneConfigError):
    pass

class KeyNestingLimit(OneConfigError):
    pass
