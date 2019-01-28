# -*- coding: utf-8 -*-
import unittest
from bitshares.blockchainobject import Object
from .fixtures import fixture_data, bitshares


class Testcases(unittest.TestCase):
    def setUp(self):
        fixture_data()

    def test_object(self):
        Object("2.1.0")
