import unittest
from channel import Channel

__author__ = 'mstipanov'

class Nesto(unittest.TestCase):
    def test(self):
        channel = Channel()
        print channel
