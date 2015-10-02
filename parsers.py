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
        data = self.readUrl(baseUrl + '/slusaonica/?' + urllib.urlencode({'q': showName.encode('utf-8')}))

        urls = re.findall(
            # r'<div class="caption">.*?<h4>.*?<a href="(.+?)">.*?</a>.*?</h4>.*?</div>',
            r'<div class="thumbnail thumbnail-shows">.*?<a href="(.+?)">.*?<img src="(.+?)" alt=".*?" title=".*?" class="normal_size">.*?</a>.*?<div class="caption">.*?<h4>.*?</h4>.*?</div>.*?</div>',
            data, re.DOTALL)

        if not urls:
            return None

        image = baseUrl + urls[0][1]
        link = baseUrl + urls[0][0]

        data = self.readUrl(link)

        searchItems = re.findall(
            r'<div class="widget">.*?<div class="schedule-heading">(.+?)</div>.*?<div class="about-show">.*?<a href="(.+?)">.+?</a>.*?<p>.*?</p>.*?<p>(.+?)</p>.*?</div>.*?</div>',
            data, re.DOTALL)

        title = searchItems[0][0]
        showLink = baseUrl + searchItems[0][1]
        description = searchItems[0][2]

        searchItems = re.findall(
            r'<div class="col-sm-3 col-xs-6">.*?<strong>EMITIRANO</strong>:<br>(.+?)</div>',
            data, re.DOTALL)

        lastBuildDate = searchItems[0].strip()

        channel = Channel()
        channel.link = showLink.strip()
        channel.title = title.strip()
        channel.description = description.strip()
        channel.image = image.strip()
        channel.lastBuildDate = lastBuildDate.strip()
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
            r'<article class="news-article">.*?<div class="article-info">.*?<div class="col-sm-3 col-xs-6">.*?<strong>EMITIRANO</strong>:<br>(.+?)</div>.*?<div class="col-sm-3 col-xs-6">.*?</div>.*?<div class="col-sm-3 col-xs-6">.*?</div>.*?<div class="col-sm-3">.*?<div class="social_buttons">.*?</div>.*?</div>.*?</div>.*?<div class="content">.*?</div>.*?<div id="jplayer" class="jp-jplayer"></div>.*?<div id="jplayer_container" class="audio-player  played repeat-on">.*?<div class="audio-control-wrapper jp-gui jp-interface">.*?<div class="controls jp-controls">.*?<div class="play-button jp-play">play_circle_filled</div>.*?<div class="pause-button jp-pause">pause_circle_filled</div>.*?</div>.*?<div class="time jp-progress">.*?<div class="time-bg jp-seek-bar">.*?<div class="jp-play-bar time-current"></div>.*?</div>.*?<div class="current-time jp-current-time"></div>.*?<div class="full-time jp-duration"></div>.*?</div>.*?<div class="volume">.*?<div class="volume-button">volume_up</div>.*?<div class="volume-bg jp-volume-bar">.*?<div class="volume-level jp-volume-bar-value"></div>.*?</div>.*?</div>.*?<div class="clearfix"></div>.*?</div>.*?<div class="track-info">.*?<p>(.+?)</p>.*?</div>.*?</div>.*?<div class="download-section">.*?<h4>Preuzmite datoteku</h4>.*?<a href="(.+?)" class="attachment-file">.*?<span class="file-size pull-right">(.+?)</span>.*?</a>.*?</div>.*?<blockquote>.*?<h3>.*?</h3>.*?<p>(.+?)</p>.*?<p class="text-right">.*?</p>.*?<div class="clearfix"></div>.*?</blockquote>.*?</article>',
            data, re.DOTALL)

        if not searchItems:
            return None

        article = Article()
        article.title = searchItems[0][1].strip()
        article.link = baseUrl + searchItems[0][2].strip()
        article.pubDate = searchItems[0][0].strip()
        # article.size = searchItems[0][3].strip()
        article.description = searchItems[0][4].strip()

        return article
