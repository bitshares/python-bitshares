from . import bitshares as bts
from .exceptions import AssetDoesNotExistsException


class Asset(dict):

    assets_cache = dict()

    def __init__(
        self,
        asset,
        bitshares_instance=None,
        lazy=False
    ):
        self.cached = False
        self.asset = asset

        if not bitshares_instance:
            bitshares_instance = bts.BitShares()
        self.bitshares = bitshares_instance

        if isinstance(asset, Asset) or isinstance(asset, dict):
            self.asset = asset.get("symbol")
            super(Asset, self).__init__(asset)
            self.cached = True

        if self.asset in Asset.assets_cache:
            super(Asset, self).__init__(Asset.assets_cache[self.asset])
            self.cached = True
        elif not lazy and not self.cached:
            self.refresh()

    def refresh(self):
        asset = self.bitshares.rpc.get_asset(self.asset)
        if not asset:
            raise AssetDoesNotExistsException
        super(Asset, self).__init__(asset)
        if self.is_bitasset:
            self["bitasset_data"] = self.bitshares.rpc.get_object(asset["bitasset_data_id"])
        self.cached = True

        # store in cache
        Asset.assets_cache[asset["symbol"]] = asset

    @property
    def is_bitasset(self):
        return ("bitasset_data_id" in self)

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super(Asset, self).__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super(Asset, self).items()
