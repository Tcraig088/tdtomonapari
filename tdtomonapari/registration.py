import logging
logger = logging.getLogger('tomobase_logger')

class ModuleRegistration():
    """
    Singleton class to check if submodules are available or not.

    Attributes:
    tomobase (bool): True if tomobase is available, False otherwise.
    tomoacquire (bool): True if tomoacquire is available, False otherwise.
    
    """
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ModuleRegistration, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        self._tomobase_checked = False
        self._tomobase_available = False
        self._tomoacquire_checked = False
        self._tomoacquire_available = False
    
    @property    
    def tomobase(self):
        if not self._tomobase_checked:
            try:
                import tomobase
                self._tomobase_available = True
            except ModuleNotFoundError:
                self._tomobase_available = False
                logging.error("tomobase module not found.")
            except Exception as e:
                self._tomobase_available = False
                logging.error(e)
        self._tomobase_checked = True
        return self._tomobase_available
    
    @property
    def tomoacquire(self):
        if not self._tomoacquire_checked:
            try:
                import tomoacquire
                self._tomoacquire_available = True
            except Exception as e:
                self._tomoacquire_available = False
                logging.error(e)
        self._tomoacquire_checked = True
        return self._tomoacquire_available
            
TDTOMO_NAPARI_MODULE_REGISTRATION = ModuleRegistration()