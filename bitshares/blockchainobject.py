# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.blockchainobject import (
    BlockchainObject as GrapheneBlockchainObject,
    Object as GrapheneObject,
    ObjectCache,
)


@BlockchainInstance.inject
class BlockchainObject(GrapheneBlockchainObject):
    pass


@BlockchainInstance.inject
class Object(GrapheneObject):
    pass
