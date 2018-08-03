from .sqlite import Key as K, Configuration as C, MasterPassword

from .base import BaseConfiguration as Configuration
from .base import BaseKey as Key




# Create keyStorage
keyStorage = Key()
configStorage = Configuration()

# Create Tables if database is brand new
if not configStorage.exists():
    configStorage.create()

newKeyStorage = False
if not keyStorage.exists():
    newKeyStorage = True
    keyStorage.create()
