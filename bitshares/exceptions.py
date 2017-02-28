class NoWallet(Exception):
    pass


class WalletExists(Exception):
    pass


class AccountExistsException(Exception):
    pass


class AccountDoesNotExistsException(Exception):
    pass


class AssetDoesNotExistsException(Exception):
    pass


class InsufficientAuthorityError(Exception):
    pass


class MissingKeyError(Exception):
    pass


class InvalidWifError(Exception):
    pass


class BlockDoesNotExistsException(Exception):
    pass


class NoWalletException(Exception):
    pass


class InvalidWifKey(Exception):
    pass


class WifNotActive(Exception):
    pass


class WitnessDoesNotExistsException(Exception):
    pass


class WrongMasterPasswordException(Exception):
    pass
