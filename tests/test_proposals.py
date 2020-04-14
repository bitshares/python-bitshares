# -*- coding: utf-8 -*-
import unittest
from pprint import pprint
from bitshares import BitShares
from bitsharesbase.operationids import getOperationNameForId
from bitshares.instance import set_shared_bitshares_instance
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_finalizeOps_proposal(self):
        # proposal = bitshares.new_proposal(bitshares.tx())
        proposal = bitshares.proposal()
        bitshares.transfer("init1", 1, "BTS", append_to=proposal)
        tx = bitshares.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_proposal2(self):
        proposal = bitshares.new_proposal()
        # proposal = bitshares.proposal()
        bitshares.transfer("init1", 1, "BTS", append_to=proposal)
        tx = bitshares.tx().json()  # default tx buffer
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_combined_proposal(self):
        parent = bitshares.new_tx()
        proposal = bitshares.new_proposal(parent)
        bitshares.transfer("init1", 1, "BTS", append_to=proposal)
        bitshares.transfer("init1", 1, "BTS", append_to=parent)
        tx = parent.json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 2)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        self.assertEqual(getOperationNameForId(ops[1][0]), "transfer")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    def test_finalizeOps_changeproposer_new(self):
        proposal = bitshares.proposal(proposer="init5")
        bitshares.transfer("init1", 1, "BTS", append_to=proposal)
        tx = bitshares.tx().json()
        ops = tx["operations"]
        self.assertEqual(len(ops), 1)
        self.assertEqual(getOperationNameForId(ops[0][0]), "proposal_create")
        prop = ops[0][1]
        self.assertEqual(len(prop["proposed_ops"]), 1)
        self.assertEqual(prop["fee_paying_account"], "1.2.90747")
        self.assertEqual(
            getOperationNameForId(prop["proposed_ops"][0]["op"][0]), "transfer"
        )

    """
    def test_finalizeOps_changeproposer_legacy(self):
        bitshares.proposer = "init5"
        tx = bitshares.transfer("init1", 1, "BTS")
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
        p1 = bitshares.new_proposal()
        p2 = bitshares.new_proposal()
        self.assertIsNotNone(id(p1), id(p2))

    def test_new_txs(self):
        p1 = bitshares.new_tx()
        p2 = bitshares.new_tx()
        self.assertIsNotNone(id(p1), id(p2))
