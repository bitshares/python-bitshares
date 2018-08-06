from graphenestorage import (
    InRamConfigurationStore,
    InRamPlainKeyStore,
    InRamEncryptedKeyStore,
    SqliteConfigurationStore,
    SqlitePlainKeyStore,
    SqliteEncryptedKeyStore,
    get_default_config_store,
    SQLiteFile
)


InRamConfigurationStore.defaults["node"] = "wss://node.bitshares.eu"
SqliteConfigurationStore.defaults["node"] = "wss://node.bitshares.eu"
SQLiteFile.appname = "bitshares"
