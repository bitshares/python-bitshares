import unittest
from pprint import pprint
from bitshares import BitShares
from bitsharesbase.operationids import getOperationNameForId
from bitshares.instance import set_shared_bitshares_instance

wif = "5KQwrPbwdL6PhXujxW37FSSQZ1JiwsST4cqQzDeyXtP79zkvFD3"


class Testcases(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.bts = BitShares(
            "wss://node.testnet.bitshares.eu",
            nobroadcast=True,
            keys={"active": wif},
        )
        # from getpass import getpass
        # self.bts.wallet.unlock(getpass())
        set_shared_bitshares_instance(self.bts)
        self.bts.set_default_account("init0")

    def test_finalizeOps_proposal(self):
        bts = self.bts
        # proposal = bts.new_proposal(bts.tx())
        proposal = bts.proposal()
        self.bts.transfer("init1", 1, "TEST", append_to=proposal)
        tx = bts.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")

    def test_finalizeOps_proposal2(self):
        bts = self.bts
        proposal = bts.new_proposal()
        # proposal = bts.proposal()
        self.bts.transfer("init1", 1, "TEST", append_to=proposal)
        tx = bts.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")

    def test_finalizeOps_combined_proposal(self):
        bts = self.bts
        parent = bts.new_tx()
        proposal = bts.new_proposal(parent)
        self.bts.transfer("init1", 1, "TEST", append_to=proposal)
        self.bts.transfer("init1", 1, "TEST", append_to=parent)
        tx = parent.json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 2)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        self.assertEqual(
            getOperationNameForId(ops[1][0]),
            "transfer")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")

    def test_finalizeOps_changeproposer_new(self):
        bts = self.bts
        proposal = bts.proposal(proposer="init5")
        bts.transfer("init1", 1, "TEST", append_to=proposal)
        tx = bts.tx().json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(prop["fee_paying_account"], "1.2.11")
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")

    """
    def test_finalizeOps_changeproposer_legacy(self):
        bts = self.bts
        bts.proposer = "init5"
        tx = bts.transfer("init1", 1, "TEST")
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(
            getOperationNameForId(ops[0][0]),
            "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(prop["fee_paying_account"], "1.2.11")
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]),
            "transfer")
    """

    def test_new_proposals(self):
        bts = self.bts
        p1 = bts.new_proposal()
        p2 = bts.new_proposal()
        self.assertIsNotNone(id(p1), id(p2))

    def test_new_txs(self):
        bts = self.bts
        p1 = bts.new_tx()
        p2 = bts.new_tx()
        self.assertIsNotNone(id(p1), id(p2))
