# -*- coding: utf-8 -*-
from .instance import BlockchainInstance
from graphenecommon.blockchainobject import BlockchainObject as GrapheneBlockchainObject


@BlockchainInstance.inject
class BlockchainObject(GrapheneBlockchainObject):
    pass
