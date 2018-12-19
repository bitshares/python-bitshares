from graphenestorage import (
    InRamConfigurationStore,
    InRamEncryptedKeyStore,
    InRamPlainKeyStore,
    SqliteConfigurationStore,
    SqliteEncryptedKeyStore,
    SQLiteFile,
    SqlitePlainKeyStore,
)


url = "wss://node.bitshares.eu"
InRamConfigurationStore.setdefault("node", url)
SqliteConfigurationStore.setdefault("node", url)


def get_default_config_store(*args, **kwargs):
    if "appname" not in kwargs:
        kwargs["appname"] = "bitshares"
    return SqliteConfigurationStore(*args, **kwargs)


def get_default_key_store(config, *args, **kwargs):
    if "appname" not in kwargs:
        kwargs["appname"] = "bitshares"
    return SqliteEncryptedKeyStore(config=config, **kwargs)
