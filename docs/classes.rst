*****************************
BitShares classes inheritance
*****************************

This document briefly describes how bitshares.xxx classes are inherited


AbstractBlockchainInstanceProvider (graphenelib) role
-----------------------------------------------------

Typical class inheritance is `Foo(GrapheneFoo)` -> `AbstractBlockchainInstanceProvider`

This class provides access to RPC via `self.blockchain` property, which is set to `blockchain_instance` kwarg or `shared_blockchain_instance` as a fallback. `shared_blockchain_instance` in turn gets proper blockchain instnce class calling `self.get_instance_class()`. `get_instance_class()` is overriden in `bitshares.instance.BlockchainInstance`

`inject method` (used as `@BlockchainInstance.inject` decorator) is needed to provide blockchain instance class in common manner.

In short, `Foo` + `@BlockchainInstance.inject` init -> `AbstractBlockchainInstanceProvider.__init__` + `Foo.__init__`.

`AbstractBlockchainInstanceProvider.__init__` -> `self._blockchain` from kwarg or -> `self.shared_blockchain_instance()` -> bitshares.Bitshares -> `AbstractGrapheneChain.__init__()`
