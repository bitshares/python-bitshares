from . import bitshares as bts
from .exceptions import AssetDoesNotExistsException


class Asset(dict):
    def __init__(self, asset, bitshares_instance=None):
        self.asset = asset

        if not isinstance(asset, Asset):
            if not bitshares_instance:
                bitshares_instance = bts.BitShares()
            self.bitshares = bitshares_instance
            asset = self.bitshares.rpc.get_asset(asset)
            if not asset:
                raise AssetDoesNotExistsException
        super(Asset, self).__init__(asset)
