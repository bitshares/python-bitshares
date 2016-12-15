from graphenebase.memo import (
    encode_memo as GPHencode_memo,
    decode_memo as GPHdecode_memo
)


def encode_memo(priv, pub, nonce, message):
    """ Encode a message with a shared secret between Alice and Bob

        :param PrivateKey priv: Private Key (of Alice)
        :param PublicKey pub: Public Key (of Bob)
        :param int nonce: Random nonce
        :param str message: Memo message
        :return: Encrypted message
        :rtype: hex

    """
    return GPHencode_memo(priv, pub, nonce, message)


def decode_memo(priv, pub, nonce, message):
    """ Decode a message with a shared secret between Alice and Bob

        :param PrivateKey priv: Private Key (of Bob)
        :param PublicKey pub: Public Key (of Alice)
        :param int nonce: Nonce used for Encryption
        :param bytes message: Encrypted Memo message
        :return: Decrypted message
        :rtype: str
        :raise ValueError: if message cannot be decoded as valid UTF-8
               string

    """
    return GPHdecode_memo(priv, pub, nonce, message)
