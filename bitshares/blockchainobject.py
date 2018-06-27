from .instance import BlockchainInstance
from datetime import datetime, timedelta


class ObjectCache(dict):

    def __init__(
        self,
        initial_data={},
        default_expiration=10,
        no_overwrite=False,
    ):
        super().__init__(initial_data)

        # Expiration
        self.set_expiration(default_expiration)

        # This allows nicer testing
        self.no_overwrite = no_overwrite

    def __setitem__(self, key, value):
        if key in self and not self.no_overwrite:
            del self[key]
        elif key in self and self.no_overwrite:
            return
        data = {
            "expires": datetime.utcnow() + timedelta(
                seconds=self.default_expiration),
            "data": value
        }
        dict.__setitem__(self, key, data)

    def __getitem__(self, key):
        if key in self:
            value = dict.__getitem__(self, key)
            return value["data"]

    def get(self, key, default):
        if key in self:
            return self[key]
        else:
            return default

    def __contains__(self, key):
        if dict.__contains__(self, key):
            value = dict.__getitem__(self, key)
            if datetime.utcnow() < value["expires"]:
                return True
        return False

    def __str__(self):
        return "ObjectCache(n={}, default_expiration={})".format(
            len(self.keys()), self.default_expiration)

    def set_expiration(self, expiration):
        self.default_expiration = expiration


class BlockchainObject(dict, BlockchainInstance):

    space_id = 1
    type_id = None
    type_ids = []

    _cache = ObjectCache()

    def __init__(
        self,
        data,
        klass=None,
        space_id=1,
        object_id=None,
        lazy=False,
        use_cache=True,
        *args,
        **kwargs
    ):
        BlockchainInstance.__init__(self, *args, **kwargs)
        self.cached = False
        self.identifier = None

        if "_cache_expiration" in kwargs:
            BlockchainObject.set_expiration(kwargs["_cache_expiration"])

        # We don't read lists, sets, or tuples
        if isinstance(data, (list, set, tuple)):
            raise ValueError(
                "Cannot interpret lists! Please load elements individually!")

        if klass and isinstance(data, klass):
            self.identifier = data.get("id")
            super().__init__(data)
        elif isinstance(data, dict):
            self.identifier = data.get("id")
            super().__init__(data)
        elif isinstance(data, int):
            # This is only for block number bascially
            self.identifier = data
            if not lazy and not self.cached:
                self.refresh()
            # make sure to store the blocknumber for caching
            self["id"] = str(data)
            # Set identifier again as it is overwritten in super() in refresh()
            self.identifier = data
        else:
            self.identifier = data
            if self.test_valid_objectid(self.identifier):
                # Here we assume we deal with an id
                self.testid(self.identifier)
            if self.iscached(data):
                super().__init__(self.getcache(data))
            elif not lazy and not self.cached:
                self.refresh()

        if use_cache and not lazy:
            self.cache()
            self.cached = True

    @staticmethod
    def clear_cache():
        BlockchainObject._cache = ObjectCache()

    @staticmethod
    def objectid_valid(i):
        if "." not in i:
            return False
        parts = i.split(".")
        if len(parts) == 3:
            try:
                [int(x) for x in parts]
                return True
            except:
                pass
            return False

    def test_valid_objectid(self, i):
        return BlockchainObject.objectid_valid(i)

    def testid(self, id):
        parts = id.split(".")
        if not self.type_id:
            return

        if not self.type_ids:
            self.type_ids = [self.type_id]

        assert int(parts[0]) == self.space_id,\
            "Valid id's for {} are {}.{}.x".format(
                self.__class__.__name__, self.space_id, self.type_id)
        assert int(parts[1]) in self.type_ids,\
            "Valid id's for {} are {}.{}.x".format(
                self.__class__.__name__, self.space_id, self.type_ids)

    def cache(self, key=None):
        # store in cache
        if key is None and dict.__contains__(self, "id"):
            BlockchainObject._cache[self.get("id")] = self
        elif key:
            BlockchainObject._cache[key] = self

    def iscached(self, id):
        return id in BlockchainObject._cache

    def getcache(self, id):
        return BlockchainObject._cache.get(id, None)

    def __getitem__(self, key):
        if not self.cached:
            self.refresh()
        return super().__getitem__(key)

    def items(self):
        if not self.cached:
            self.refresh()
        return super().items()

    def __contains__(self, key):
        if not self.cached:
            self.refresh()
        return super().__contains__(key)

    def __repr__(self):
        return "<%s %s>" % (
            self.__class__.__name__, str(self.identifier))
