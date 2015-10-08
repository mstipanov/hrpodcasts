# -*- coding: utf-8 -*-

from parsers import Parser

__author__ = 'mstipanov'

channel = Parser().parse("povijest četvrtkom")

print channel.to_JSON()