from qtpy.QtCore import QObject, Signal

from tomobase.globals import logger, Item, ItemDict


class VariablesDict(ItemDict, QObject):
    refreshed = Signal()

    def __init__(self, **kwargs):
        ItemDict.__init__(self, **kwargs)
        QObject.__init__(self)

    def save():
        pass

    def delete(self, key):
        if key in self:
            del self[key]
        else:
            logger.error(f"Key {key} not found in VariablesDict.")

    def rename(self, key, new_name):
        self[key].name = new_name

    def refresh(self):
        self.refreshed.emit()

TDTOMONAPARI_VARIABLES = VariablesDict() 

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
                logger.error("tomobase module not found.")
            except Exception as e:
                self._tomobase_available = False
                logger.error(e)
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
                logger.error(e)
        self._tomoacquire_checked = True
        return self._tomoacquire_available
            
TDTOMO_NAPARI_MODULE_REGISTRATION = ModuleRegistration()