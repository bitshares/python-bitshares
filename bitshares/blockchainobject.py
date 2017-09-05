from bitshares.instance import shared_bitshares_instance


class BlockchainObject(dict):

    space_id = 1
    type_id = None
    type_ids = []

    _cache = dict()

    def __init__(
        self,
        data,
        *args,
        klass=None,
        space_id=1,
        object_id=None,
        lazy=True,
        use_cache=True,
        bitshares_instance=None,
        **kwargs,
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
        else:
            self.identifier = data
            parts = self.identifier.split(".")
            if len(parts) == 3:
                # Here we assume we deal with an id
                self.testid(self.identifier)
            if self.iscached(data):
                super().__init__(self.getcache(data))
            elif not lazy and not self.cached:
                self.refresh()

        if use_cache and not lazy:
            self.cache(self)
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

    def cache(self, data):
        # store in cache
        if "id" in data:
            BlockchainObject._cache[data.get("id")] = data

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

    def __repr__(self):
        return "<%s %s>" % (self.__class__.__name__, str(self.identifier))
