# -*- coding: utf-8 -*-
import time

from parsers import Parser

__author__ = 'mstipanov'

# channel = Parser().parse(u"inventura")
# channel = Parser().parse(u"povijest četvrtkom")
channel = Parser().parse("explora")

# time.strptime(channel.articles[0].pubDate, "%d.%m.%Y %H:%M")
print channel.articles[0].pubDate
print time.strptime(channel.articles[0].pubDate, "%Y-%m-%dT%H:%M:%SZ")

print channel.to_JSON()
