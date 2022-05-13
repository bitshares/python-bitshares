# Changelog
Note: version releases in the 0.x.y range may introduce breaking changes.

<!--next-version-placeholder-->

## v0.7.1 (2022-05-13)
### Fix
* Unitests now working ([`77716a6`](https://github.com/bitshares/python-bitshares/commit/77716a6dc7547a9e73577ce18b587388fd4e9ee5))
* Linting via black ([`6b4ac7f`](https://github.com/bitshares/python-bitshares/commit/6b4ac7f085466ed13a4e9dabfd77bf81b905a841))
* #303 ([`0eedb6d`](https://github.com/bitshares/python-bitshares/commit/0eedb6d2f42f78920eea1b4811d8bd12fb32e6bd))
* #307 ([`a72ceee`](https://github.com/bitshares/python-bitshares/commit/a72ceee11aedcbe0c800b5c76543f39219324d41))
* Fix #306 ([`3b38b99`](https://github.com/bitshares/python-bitshares/commit/3b38b9939175a3d67bad15091fa9c544ff9c4afc))

### Documentation
* Release flow and conventional commits ([`4958a6e`](https://github.com/bitshares/python-bitshares/commit/4958a6eab9cbf0ff930be7cb03545617e952ea29))

## 0.7.0

- minor: Add liquidity pool support

## 0.6.0

- minor: Add support for tickets

## 0.5.1

- patch: Add aio packages to setup.py

## 0.5.0

- minor: Add asyncio support
- minor: Fixes

## 0.4.0

- minor: Ensure we can invert Order and FilledOrder too
- patch: Make Notify terminate on CTRL-C

## 0.3.3

- patch: New docs
- patch: Released with semversioner
- patch: pyup updates

## 0.3.2

- patch: Status Quo

Release 0.3.0
=============

The major change of this release was to merge common code with other
graphene-based blockchains into python-graphene to reduce redunance and
simply code maintainability.

Features
--------
d1484a0 Fix issue with backend showing wrong percentage change after a while
ba23069 Allow to create an account that only references to another account
23b2c7a Implement issuing of shares as part of Asset()
ab40514 Simplify use of custom authorties
c349316 Merge pull request #179 from jhtitor/few_asset_ops
9c2c3bf Add test for Asset_claim_pool operation.
5ad23c4 Add asset_claim_pool operation.
42deeda Add tests for global_settle and claim_fees operations.
dd4cb96 Add asset_global_settle and asset_claim_fees operations.
0a25a4d New operation
1f1e355 Merge 'upstream/develop' into few_asset_ops
681b0fa Implement asset-settle
74fa037 Finish up unittests using new caching system
63a4030 Import Object from graphenecommon
43a2170 Simplify Key classes
acc54d5 move general stuff to graphene
2a0b813 Simplyify dealing with Prefixes
3a9f16d Migrate common stuff to python-graphene
9c9b15a Separation of wallet.py
f41bd77 Bid Collateral Operation
54dcfbf Bid Collateral Operation

Fixes
-----
436fb40 Fix Amount in Open Order and improve unittest (Fix #76)
acf9a29 Fix #180
b061399 Fix #185
b64f222 fix precommit to use python3
bf6a3dc Merge pull request #171 from bitfag/fix-order-rounding
6cc984a Fix Object() class and add unit test
abf4046 Fix incorrect initialization of FilledOrder and Order
d52f7da Fix price feeds
ac91f9e Fix buy/sell of near-precision amounts
2695525 Fix messages and account
055635f Fix unittesting
4b72616 Fix fox.ini with blake
3bb9b8b Fix __init__
bc73a8a #128 Proposal fix, now, at least method accountopenorders won't raise KeyError "limit_orders"
35a3aaf Fix #151
8d66b43 Fix getActiveKeyForAccount failing when multiple keys installed
61712db Ensure we do have a default expiration time for new orders
949850b Properly initialize blockchain instance
8f9bc23 Also import the exceptions
4d27455 Also import the exceptions
1e7d98c Merge branch 'feature/cleanup-txbuilder' into develop
cf8fafb Ensure we can verify messages on different networks too
e13f77f define required type_id
20258e2 Re-enable computation of mcr
5efb1d4 Merge pull request #162 from jhtitor/memo_pad
4a633ca Merge pull request #160 from Algruun/master
e2ef0a4 Verify memo checksum during decoding.
1c50b37 Always add final padding during memo encryption.
b3f1bda Make memo _pad work with bytes, instead of strings.
588b8e7 Add memo tests for padding edge cases.
0b2b137 Message, ensure we can sign on different blockchain too
9644bf5 Ensure we can deal with \r as well
cd91155 Also store plain message and meta separately
dae6918 After verification fill in class members
3aa81cc Makefile rename back temporary test
54600bb use twine for pypi upload


Testnet
-------
1ec6faa Add HTLC class
e4d743d HTLC implementation
13e0168 Switch tests back to main net (breaks HLTC unit tests since ops are not available on mainnet)
65c451b Implement HTLC base operations

Dependencies
------------
802d576 bump dependency for pygraphene
b67724c Bump requirement for pygraphene

Code Style and Cleanups
-----------------------
c95d093 linting
0e155e9 tox and requirements for black and flake8
2e48137 pre-commit installation
8b5294d testing pre-commit
80013b1 linting
c96dac6 Isort
812e6e3 Black reformatting
3a6c491 remove obsolete modules
3918218 cleanup
960f3aa Remove logging module
7e5d506 Cleanup base.memo
3e15f87 Improve class dealing and unittesting

Documentation
-------------
431582f Updates to documentation
1a06cfc Update documentation
ebb1f2d Add Hackthedex link in readme.md #153
70b8260 [message] Better exception message

Release 0.2.0rc0
================

Storage:
--------

* internal storage now makes use of pygraphene 1.0.0 framework
* `bitshares.storage` now comes with the prebuilt inRam and SQLite stores from pygraphene
* `BitShares()` can be provided with a custom config store using key word `config_store=` and `wallet=` (wallet instance)
* `Wallet()` (internally used by `BitShares()`) can be provided with a custom config store using key word `key_store=`
* Interfaces for stores are defined in pygraphene
* The Interface for the wallet is defined in `wallet.py`
* Instead of using

  ```
  from bitshares.storage import configStorage as config
  ```

  use

  ```
  BitShares().config
  ```

  or

  ```
  from bitshares.storage import get_default_config_store
  config = get_default_config_store()
  ```

Testing:
--------

* pybitshares now contains a framework (fixtures) to simplify access to data provided by the blockchain/database
* Major improvements to coverage

Features:
---------

* Add custom operation to bitsharesbase

Fixes:
------

* 357aa63 Adjust "for_sale" when invert()-ing an Order
* 5924ac1 Allow to read more trading data #111
* 26a72fc Commenting #132
* f1b27d1 Set default expiration to 30 seconds #132
* bd69b2c Fix bitshares->blockchain attrribute #132
* a19b9ed Fix #136
* f616874 Revert "fix Vesting"
* b430d3b Set default order expiration to 1yr
* a949570 fix Vesting
* f70f20f Ensure we don't through in case 'secs=None'
* 0dabd9a Use PublicKey's internal sorting algorithm
* 8b7b134 Fix incompatibility with new graphene framework
* 9ce8068 Fix init of FilledOrder from history op
* 51c2277 Fix unittests for pygraphene@develop
* 803f828 further improvements
* 305efe2 Raise Exception in case the key has been included already
* 5b2736a fix store to deal with proper sqlite file etc
* 7e5ff23 unit tests now with fixtures
