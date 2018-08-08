from graphenestorage import (
    InRamConfigurationStore,
    InRamPlainKeyStore,
    InRamEncryptedKeyStore,
    SqliteConfigurationStore,
    SqlitePlainKeyStore,
    SqliteEncryptedKeyStore,
    SQLiteFile
)


InRamConfigurationStore.setdefault("node", "wss://node.bitshares.eu")
SqliteConfigurationStore.setdefault("node", "wss://node.bitshares.eu")


def get_default_config_store(*args, **kwargs):
    if not "appname" in kwargs:
        kwargs["appname"] = "bitshares"
    return SqliteConfigurationStore(*args, **kwargs)


def get_default_key_store(*args, config, **kwargs):
    if not "appname" in kwargs:
        kwargs["appname"] = "bitshares"
    return SqliteEncryptedKeyStore(
        config=config, **kwargs
    )
