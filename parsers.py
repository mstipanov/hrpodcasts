# -*- coding: utf-8 -*-
import json
import re

from article import Article
from channel import Channel
from urllib.request import urlopen
from urllib.parse import urlencode


class Parser:
    def read_url(self, url):
        data = urlopen(url)
        return data.read().decode('utf-8')

    def parse(self, showName):
        channel = self.parse_channel(showName)
        if not channel:
            return None

        return channel

    def parse_channel(self, showName):
        data = self.read_url("https://radio.hrt.hr/api/getListeningRoomFilteredData?category=sve-kategorije&channel=svi-kanali&sort=AZ&" + urlencode({'keyword': showName.encode('utf-8')}) + "&offset=0")

        channel = None
        shows = json.loads(data)
        for show in shows:
            showUrl = show.get("url")
            imageUrl = None
            if show.get("mediaImage"):
                imageUrl = show.get("mediaImage").get("path")
            title = show.get("displayText")
            channel = self.try_parse_channel(showUrl, imageUrl, title)
            if len(channel.articles) > 0:
                break

        return channel

    def try_parse_channel(self, showLink, image, title):
        data = self.read_url(showLink)
        searchItemsData = re.findall(
            r'<script id="__NEXT_DATA__" type="application/json">(.+?)</script>',
            data, re.DOTALL + re.IGNORECASE)
        searchItemsJson = searchItemsData[0]
        searchItems = json.loads(searchItemsJson)
        description = searchItems.get("props").get("pageProps").get("cycle").get("data").get("radioCycle")[0].get("intro")
        channel = Channel()
        channel.link = showLink.strip()
        channel.title = title.strip()
        channel.description = description.strip()
        channel.image = image.strip()
        # channel.lastBuildDate = lastBuildDate.strip()
        channel.articles = self.parse_articles(searchItems.get("props").get("pageProps").get("episodes"))
        return channel

    def parse_articles(self, episodees):
        articles = []
        for episode in episodees.get("data").get("lastAvailableEpisodes"):
            article = self.parse_article(episode)
            if article:
                articles.append(article)

        return articles

    def parse_article(self, episode):
        article = Article()
        article.pubDate = episode.get("bag").get("contentItems")[0].get("broadcastStart")
        article.title = episode.get("caption")  + " " + article.pubDate.split("T")[0]
        article.link = episode.get("audio").get("metadata")[0].get("path")
        article.description = episode.get("intro")

        return article
