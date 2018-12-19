from graphenebase.bip38 import decrypt as GPHdecrypt
from graphenebase.bip38 import encrypt as GPHencrypt


def encrypt(privkey, passphrase):
    """ BIP0038 non-ec-multiply encryption. Returns BIP0038 encrypted privkey.

    :param privkey: Private key
    :type privkey: Base58
    :param str passphrase: UTF-8 encoded passphrase for encryption
    :return: BIP0038 non-ec-multiply encrypted wif key
    :rtype: Base58

    """
    return GPHencrypt(privkey, passphrase)


def decrypt(encrypted_privkey, passphrase):
    """BIP0038 non-ec-multiply decryption. Returns WIF privkey.

    :param Base58 encrypted_privkey: Private key
    :param str passphrase: UTF-8 encoded passphrase for decryption
    :return: BIP0038 non-ec-multiply decrypted key
    :rtype: Base58
    :raises SaltException: if checksum verification failed (e.g. wrong password)

    """
    return GPHdecrypt(encrypted_privkey, passphrase)
