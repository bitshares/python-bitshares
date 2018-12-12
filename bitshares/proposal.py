# -*- coding: utf-8 -*-
from .account import Account
from .instance import BlockchainInstance
from graphenecommon.proposal import (
    Proposal as GrapheneProposal,
    Proposals as GrapheneProposals,
)


@BlockchainInstance.inject
class Proposal(GrapheneProposal):
    """ Read data about a Proposal Balance in the chain

        :param str id: Id of the proposal
        :param bitshares blockchain_instance: BitShares() instance to use when accesing a RPC

    """

    def define_classes(self):
        self.type_id = 10
        self.account_class = Account


@BlockchainInstance.inject
class Proposals(GrapheneProposals):
    """ Obtain a list of pending proposals for an account

        :param str account: Account name
        :param bitshares blockchain_instance: BitShares() instance to use when accesing a RPC
    """

    def define_classes(self):
        self.account_class = Account
        self.proposal_class = Proposal
