#from .sqlite import SqliteKey as K, SqliteConfiguration as C
from .base import DefaultConfigurationStore
from .base import DefaultEncryptedKeyStore
from .base import MasterPassword
from .base import InRamKeyStore
from . import sqlite

__all__ = [
    "base",
    "sqlite"
]
Configuration = DefaultConfigurationStore
EncryptedKey = DefaultEncryptedKeyStore
Key = InRamKeyStore

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
