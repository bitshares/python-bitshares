from bitshares.instance import shared_bitshares_instance
from datetime import datetime, timedelta


class ObjectCache(dict):

    max_cache_objects = 1000

    def __init__(self, initial_data={}, max_cache_objects=1000):
        super().__init__(initial_data)
        ObjectCache.max_cache_objects = max_cache_objects

    def __setitem__(self, key, value):
        if key in self:
            del self[key]
        data = {
            "expires": datetime.utcnow() + timedelta(seconds=10),
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
        return "ObjectCache(n={}, max_cache_objects={})".format(len(self.keys()), self.max_cache_objects)


class BlockchainObject(dict):

    space_id = 1
    type_id = None
    type_ids = []

    _cache = ObjectCache()

    def __init__(
        self,
        data,
        *args,
        klass=None,
        space_id=1,
        object_id=None,
        lazy=False,
        use_cache=True,
        bitshares_instance=None,
        **kwargs
    ):
        self.bitshares = bitshares_instance or shared_bitshares_instance()
        self.cached = False
        self.identifier = None

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
            parts = self.identifier.split(".")
            if len(parts) == 3:
                valid_objectid = False
                try:
                    [int(x) for x in parts]
                    valid_objectid = True
                except:
                    pass
                if valid_objectid:
                    # Here we assume we deal with an id
                    self.testid(self.identifier)
            if self.iscached(data):
                super().__init__(self.getcache(data))
            elif not lazy and not self.cached:
                self.refresh()

        if use_cache and not lazy:
            self.cache()
            self.cached = True

    def testid(self, id):
        parts = id.split(".")
        if not self.type_id:
            return

        if not self.type_ids:
            self.type_ids = [self.type_id]

        assert int(parts[0]) == self.space_id,\
            "Valid id's for {} are {}.{}.x".format(self.__class__.__name__, self.space_id, self.type_ida)
        assert int(parts[1]) in self.type_ids,\
            "Valid id's for {} are {}.{}.x".format(self.__class__.__name__, self.space_id, self.type_ids)

    def cache(self):
        # store in cache
        if dict.__contains__(self, "id"):
            BlockchainObject._cache[self.get("id")] = self

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
        return "<%s %s>" % (self.__class__.__name__, str(self.identifier))
