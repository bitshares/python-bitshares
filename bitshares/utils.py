# -*- coding: utf-8 -*-
from .exceptions import ObjectNotInProposalBuffer
from .instance import BlockchainInstance

# Load methods from graphene and provide them to bitshares
from graphenecommon.utils import (
    formatTime,
    timeFormat,
    formatTimeString,
    formatTimeFromNow,
    parse_time,
    assets_from_string,
)


def injectClass(inj):
    def param(cls):
        class NewClass(inj, cls):
            def __init__(self, *args, **kwargs):
                inj.__init__(self, *args, **kwargs)
                cls.__init__(self, *args, **kwargs)

        return NewClass

    return param
