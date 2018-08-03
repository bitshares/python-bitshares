#from .sqlite import SqliteKey as K, SqliteConfiguration as C

from .base import DefaultConfigurationStore as Configuration
from .base import DefaultEncryptedKeyStore as EncryptedKey
from .base import MasterPassword
from .base import InRamKeyStore as Key

# Create keyStorage
configStorage = Configuration()

masterPassword = MasterPassword(
    storage=configStorage
)

keyStorage = Key(
    storage=configStorage
)

# TODO
"""
# Create Tables if database is brand new
if not configStorage.exists():
    configStorage.create()

newKeyStorage = False
if not keyStorage.exists():
    newKeyStorage = True
    keyStorage.create()
"""
