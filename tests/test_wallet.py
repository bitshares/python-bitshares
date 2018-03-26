import unittest
import mock
from pprint import pprint
from transnet import Transnet
from transnet.account import Account
from transnet.amount import Amount
from transnet.asset import Asset
from transnet.instance import set_shared_transnet_instance
from transnetbase.operationids import getOperationNameForId

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = Transnet(
            nobroadcast=True,
            # We want to bundle many operations into a single transaction
            bundle=True,
            # Overwrite wallet to use this list of wifs only
            wif=[wif]
        )
        self.bts.set_default_account("init0")
        set_shared_transnet_instance(self.bts)
