from bitshares.utils import assets_from_string


def test_assets_from_string():
    assert assets_from_string('USD:BTS') == ['USD', 'BTS']
    assert assets_from_string('BTSBOTS.S1:BTS') == ['BTSBOTS.S1', 'BTS']
