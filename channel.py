import json as mod_json

__author__ = 'mstipanov'


class Channel:
    title = None
    link = None
    image = None
    description = None
    lastBuildDate = None
    articles = None

    def __init__(self):
        self.articles = []

    def __repr__(self):
        return mod_json.dumps(self.__dict__)

    def to_JSON(self):
        return mod_json.dumps(self, default=lambda o: o.__dict__, sort_keys=True, indent=4)
