# -*- coding: utf-8 -*-
from graphenestorage.exceptions import WrongMasterPasswordException
from graphenecommon.exceptions import (
    AccountDoesNotExistsException,
    AssetDoesNotExistsException,
    BlockDoesNotExistsException,
    CommitteeMemberDoesNotExistsException,
    InvalidAssetException,
    InvalidMemoKeyException,
    InvalidMessageSignature,
    InvalidWifError,
    KeyAlreadyInStoreException,
    KeyNotFound,
    MissingKeyError,
    NoWalletException,
    OfflineHasNoRPCException,
    ProposalDoesNotExistException,
    VestingBalanceDoesNotExistsException,
    WalletExists,
    WalletLocked,
    WitnessDoesNotExistsException,
    WorkerDoesNotExistsException,
    WrongMemoKey,
    GenesisBalanceDoesNotExistsException,
)


class RPCConnectionRequired(Exception):
    """ An RPC connection is required
    """

    pass


class AccountExistsException(Exception):
    """ The requested account already exists
    """

    pass


class ObjectNotInProposalBuffer(Exception):
    """ Object was not found in proposal
    """

    pass


class HtlcDoesNotExistException(Exception):
    """ HTLC object does not exist
    """

    pass
