from .base import (
    InRamConfigurationStore,
    InRamPlainKeyStore,
    InRamEncryptedKeyStore,
    SqliteConfigurationStore,
    SqlitePlainKeyStore,
    SqliteEncryptedKeyStore
)

__all__ = [
    "base",
    "sqlite",
    "ram"
]


def get_default_config_store():
    return SqliteConfigurationStore()
