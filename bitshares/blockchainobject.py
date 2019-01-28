# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.blockchainobject import (
    BlockchainObject as GrapheneBlockchainObject,
    Object as GrapheneChainObject,
    ObjectCache,
)


@BlockchainInstance.inject
class BlockchainObject(GrapheneBlockchainObject):
    pass


@BlockchainInstance.inject
class Object(GrapheneChainObject):
    perform_id_tests = False
