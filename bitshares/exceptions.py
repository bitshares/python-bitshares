# -*- coding: utf-8 -*-
from graphenestorage.exceptions import WrongMasterPasswordException
from graphenecommon.exceptions import (
    InvalidWifError,
    KeyAlreadyInStoreException,
    KeyNotFound,
    NoWalletException,
    OfflineHasNoRPCException,
    WalletExists,
    WalletLocked,
)


class RPCConnectionRequired(Exception):
    """ An RPC connection is required
    """

    pass


class AccountExistsException(Exception):
    """ The requested account already exists
    """

    pass


class AccountDoesNotExistsException(Exception):
    """ The account does not exist
    """

    pass


class AssetDoesNotExistsException(Exception):
    """ The asset does not exist
    """

    pass


class InvalidAssetException(Exception):
    """ An invalid asset has been provided
    """

    pass


class InsufficientAuthorityError(Exception):
    """ The transaction requires signature of a higher authority
    """

    pass


class MissingKeyError(Exception):
    """ A required key couldn't be found in the wallet
    """

    pass


class ProposalDoesNotExistException(Exception):
    """ The proposal does not exist
    """

    pass


class BlockDoesNotExistsException(Exception):
    """ The block does not exist
    """

    pass


class WitnessDoesNotExistsException(Exception):
    """ The witness does not exist
    """

    pass


class CommitteeMemberDoesNotExistsException(Exception):
    """ Committee Member does not exist
    """

    pass


class VestingBalanceDoesNotExistsException(Exception):
    """ Vesting Balance does not exist
    """

    pass


class WorkerDoesNotExistsException(Exception):
    """ Worker does not exist
    """

    pass


class ObjectNotInProposalBuffer(Exception):
    """ Object was not found in proposal
    """

    pass


class InvalidMessageSignature(Exception):
    """ The message signature does not fit the message
    """

    pass


class InvalidMemoKeyException(Exception):
    """ Memo key in message is invalid
    """

    pass


class WrongMemoKey(Exception):
    """ The memo provided is not equal the one on the blockchain
    """

    pass
