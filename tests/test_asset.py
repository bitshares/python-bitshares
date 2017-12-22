from bitshares.asset import Asset
from bitshares import BitShares


def test_calls(mocker):
    asset = Asset("USD", lazy=True, bitshares_instance=BitShares(offline=True))
    method = mocker.patch.object(Asset, 'get_call_orders')
    asset.calls
    method.assert_called_with(10)
