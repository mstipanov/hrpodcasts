from parsers import Parser

__author__ = 'mstipanov'

channel = Parser().parse("andromeda")

print channel.to_JSON()