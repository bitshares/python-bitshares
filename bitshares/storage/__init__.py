from .sqlite import Key, Configuration as C, MasterPassword

from .base import BaseConfiguration as Configuration




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
