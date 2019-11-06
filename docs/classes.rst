*****************************
BitShares classes inheritance
*****************************

This document briefly describes how bitshares.xxx classes are inherited


AbstractBlockchainInstanceProvider (graphenelib) role
-----------------------------------------------------

Typical class inheritance is `Foo(GrapheneFoo)` ->
`GrapheneFoo(AbstractBlockchainInstanceProvider)` ->
`AbstractBlockchainInstanceProvider`

This class provides access to RPC via `self.blockchain` property, which is set
to `blockchain_instance` kwarg or `shared_blockchain_instance` as a fallback.
`shared_blockchain_instance` in turn gets proper blockchain instance class
calling `self.get_instance_class()`. `get_instance_class()` is overwritten in
`bitshares.instance.BlockchainInstance`

`inject` method (used as `@BlockchainInstance.inject` decorator) is needed to
provide blockchain instance class in common manner.

In short, `Foo` + `@BlockchainInstance.inject` init calls
`AbstractBlockchainInstanceProvider.__init__` and `Foo.__init__`.

`AbstractBlockchainInstanceProvider.__init__` sets `self._blockchain` from kwarg
or via calling `self.shared_blockchain_instance()`, which leads to initizlizing
`bitshares.Bitshares` (`bitshares.Bitshares` is inherited from
`AbstractGrapheneChain`.

Asyncio versions
----------------

Typical async class inherited from corresponding async class from graphenelib,
and from synchronous class, like `class Asset(GrapheneAsset, SyncAsset)`. So,
async version needs to redefine only needed methods.

Most of async classes needs async `__init__` because they're loading some
objects from the blockchain, which requires an API call performed via async RPC.
To achieve this, async `AbstractBlockchainInstanceProvider` has different
`inject()` method.
