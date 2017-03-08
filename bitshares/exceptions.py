class WalletExists(Exception):
    """ A wallet has already been created and requires a password to be
        unlocked by means of :func:`bitshares.wallet.unlock`.
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


class InsufficientAuthorityError(Exception):
    """ The transaction requires signature of a higher authority
    """
    pass


class MissingKeyError(Exception):
    """ A required key couldn't be found in the wallet
    """
    pass


class InvalidWifError(Exception):
    """ The provided private Key has an invalid format
    """
    pass


class BlockDoesNotExistsException(Exception):
    """ The block does not exist
    """
    pass


class NoWalletException(Exception):
    """ No Wallet could be found, please use :func:`bitshares.wallet.create` to
        create a new wallet
    """
    pass


class WitnessDoesNotExistsException(Exception):
    """ The witness does not exist
    """
    pass


class WrongMasterPasswordException(Exception):
    """ The password provided could not properly unlock the wallet
    """
    pass
