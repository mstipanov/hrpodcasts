# -*- coding: utf-8 -*-

import re
import urllib
import urllib2

from article import Article
from channel import Channel


class Parser():
    def readUrl(self, url):
        data = urllib2.urlopen(url)
        return data.read()

    def parse(self, showName):
        channel = self.parseChannel(showName)
        if not channel:
            return None

        return channel

    def parseChannel(self, showName):
        baseUrl = 'http://radio.hrt.hr'
        data = self.readUrl(baseUrl + '/emisije/?' + urllib.urlencode({'q': showName.encode('utf-8')}))

        urls = re.findall(
            r'<div class="col-md-4 col-sm-6 item split">.*?<div class="thumbnail thumbnail-shows">.*?<a href="(.+?)">.*?<img src="(.+?)" alt=".*?" title="(.+?)" class="normal_size">.*?</a>.*?<div class="caption">.*?<h4><a href=".*?">.*?</a></h4>.*?<p>.*?</p>.*?<p>.*?</p>.*?</div>.*?</div>.*?</div>',
            data, re.DOTALL)

        if not urls:
            return None

        showLink = baseUrl + urls[0][0]
        image = baseUrl + urls[0][1]
        title = urls[0][2]

        data = self.readUrl(showLink)

        searchItems = re.findall(
            r'<meta name="description" content="(.+)" />',
            data, re.DOTALL)

        description = searchItems[0]

        channel = Channel()
        channel.link = showLink.strip()
        channel.title = title.strip()
        channel.description = description.strip()
        channel.image = image.strip()
        # channel.lastBuildDate = lastBuildDate.strip()
        channel.articles = self.parseArticles(baseUrl, showLink)
        return channel

    def parseArticles(self, baseUrl, showLink):
        data = self.readUrl(showLink)

        searchItems = re.findall(
            r'<div class="row">.*?<div class="col-md-12 split tema1">.*?<div class="media">.*?<div class="media-left">.*?<a href="(.+?)">.*?</a>.*?</div>.*?<div class="media-body">.*?</div>.*?</div>.*?</div>.*?</div>',
            data, re.DOTALL)

        articles = []
        for searchItem in searchItems:
            article = self.parseArticle(baseUrl, baseUrl + searchItem)
            if article:
                articles.append(article)

        return articles

    def parseArticle(self, baseUrl, link):
        data = self.readUrl(link)

        searchItems = re.findall(
            r'<article class="news-article">.*?<div class="article-info">.*?<div class="col-sm-3 col-xs-6">.*?<strong>EMITIRANO</strong>:<br>(.+?)</div>.*?</div>.*?<div id="jplayer_container" class="audio-player  played repeat-on">.*?<div class="track-info">.*?<p class="track-title">(.+?)</p>.*?<div class="download-section">.*?<h4>Preuzmite datoteku</h4>.*?<a href="(.+?)" class="attachment-file">.*?<span class="file-size pull-right">(.+?)</span>.*?</a>.*?</div>.*?<blockquote>.*?<h3>.*?</h3>.*?<p>(.+?)</p>.*?</blockquote>.*?</article>',
            data, re.DOTALL)

        if not searchItems:
            return None

        article = Article()
        article.pubDate = searchItems[0][0].strip()
        article.title = searchItems[0][1].strip()
        article.link = baseUrl + searchItems[0][2].strip()
        # article.size = searchItems[0][3].strip()
        article.description = searchItems[0][4].strip()

        return article
