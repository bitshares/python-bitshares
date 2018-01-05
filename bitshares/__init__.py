from .bitshares import BitShares

__all__ = [
    "bitshares"
    "aes",
    "account",
    "amount",
    "asset",
    "block",
    "blockchain",
    "dex",
    "market",
    "storage",
    "price",
    "utils",
    "wallet",
    "committee",
    "vesting",
    "proposal"
]

SIGNED_MESSAGE_META = """{message}
account={meta[account]}
memokey={meta[memokey]}
block={meta[block]}
timestamp={meta[timestamp]}"""

SIGNED_MESSAGE_ENCAPSULATED = """
-----BEGIN BITSHARES SIGNED MESSAGE-----
{message}
-----BEGIN META-----
account={meta[account]}
memokey={meta[memokey]}
block={meta[block]}
timestamp={meta[timestamp]}
-----BEGIN SIGNATURE-----
{signature}
-----END BITSHARES SIGNED MESSAGE-----"""
