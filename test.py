from parsers import Parser

__author__ = 'mstipanov'

channel = Parser().parse("inventura")

print channel.to_JSON()