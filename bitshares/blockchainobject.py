# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.blockchainobject import (
    BlockchainObject as GrapheneBlockchainObject,
    ObjectCache,
)


@BlockchainInstance.inject
class BlockchainObject(GrapheneBlockchainObject):
    pass
