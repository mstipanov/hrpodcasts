# -*- coding: utf-8 -*-

import json as mod_json

__author__ = 'mstipanov'


class Article:
    title = None
    link = None
    description = None
    pubDate = None

    def __repr__(self):
        return mod_json.dumps(self.__dict__)

    def to_JSON(self):
        return mod_json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
