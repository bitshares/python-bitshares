from . import bitshares as bts
from .exceptions import AssetDoesNotExistsException


class Asset(dict):
    def __init__(self, asset, bitshares_instance=None):
        self.cached = False
        self.asset = asset

        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if isinstance(asset, Asset):
            super(Asset, self).__init__(asset)
            self.cached = True

    def refresh(self):
        asset = self.bitshares.rpc.get_asset(self.asset)
        if not asset:
            raise AssetDoesNotExistsException
        super(Asset, self).__init__(asset)
        self.cached = True

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Asset, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Asset, self).items()
