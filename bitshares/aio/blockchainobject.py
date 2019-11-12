# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.aio.blockchainobject import (
    BlockchainObject as GrapheneBlockchainObject,
    Object as GrapheneChainObject,
)


@BlockchainInstance.inject
class BlockchainObject(GrapheneBlockchainObject):
    pass


@BlockchainInstance.inject
class Object(GrapheneChainObject):
    perform_id_tests = False
