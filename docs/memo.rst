****
Memo
****

Memo Keys
#########

In Transnet, memos are AES-256 encrypted with a shared secret between sender and
receiver. It is derived from the memo private key of the sender and the memo
publick key of the receiver. 

In order for the receiver to decode the memo, the shared secret has to be
derived from the receiver's private key and the senders public key.

The memo public key is part of the account and can be retreived with the
`get_account` call:

.. code-block:: js

    get_account <accountname>
    {
      [...]
      "options": {
        "memo_key": "GPH5TPTziKkLexhVKsQKtSpo4bAv5RnB8oXcG4sMHEwCcTf3r7dqE",
        [...]
      },
      [...]
    }

while the memo private key can be dumped with `dump_private_keys`

Memo Message
############

The take the following form:

.. code-block:: js

        {
          "from": "GPH5mgup8evDqMnT86L7scVebRYDC2fwAWmygPEUL43LjstQegYCC",
          "to": "GPH5Ar4j53kFWuEZQ9XhxbAja4YXMPJ2EnUg5QcrdeMFYUNMMNJbe",
          "nonce": "13043867485137706821",
          "message": "d55524c37320920844ca83bb20c8d008"
        }

The fields `from` and `to` contain the memo public key of sender and receiver.
The `nonce` is a random integer that is used for the seed of the AES encryption
of the message.

Example
#######

Encrypting a memo
~~~~~~~~~~~~~~~~~

The high level memo class makes use of the pybitshares wallet to obtain keys
for the corresponding accounts.

.. code-block:: python

    from bitshares.memo import Memo
    from bitshares.account import Account

    memoObj = Memo(
        from_account=Account(from_account),
        to_account=Account(to_account)
    )
    encrypted_memo = memoObj.encrypt(memo)

Decoding of a received memo
~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

     from getpass import getpass
     from bitshares.block import Block
     from bitshares.memo import Memo

     # Obtain a transfer from the blockchain
     block = Block(23755086)                   # block
     transaction = block["transactions"][3]    # transactions
     op = transaction["operations"][0]         # operation
     op_id = op[0]                             # operation type
     op_data = op[1]                           # operation payload

     # Instantiate Memo for decoding
     memo = Memo()

     # Unlock wallet
     memo.unlock_wallet(getpass())

     # Decode memo
     # Raises exception if required keys not available in the wallet
     print(memo.decrypt(op_data["memo"]))

API
###

.. automodule:: bitsharesbase.memo
    :members:
