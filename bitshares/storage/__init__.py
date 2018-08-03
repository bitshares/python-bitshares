from .sqlite import SqliteKey as K, SqliteConfiguration as C

from .base import BaseConfiguration as Configuration
from .base import BaseEncryptedKey as EncryptedKey
from .base import MasterPassword

from .base import BaseKey as Key

# Create keyStorage
configStorage = Configuration()

masterPassword = MasterPassword(
    storage=configStorage
)

keyStorage = Key(
    storage=configStorage
)


# Create Tables if database is brand new
if not configStorage.exists():
    configStorage.create()

newKeyStorage = False
if not keyStorage.exists():
    newKeyStorage = True
    keyStorage.create()
