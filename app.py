# -*- coding: utf-8 -*-
import json as mod_json
import re
import urllib

import webapp2 as mod_webapp2
import urllib2
import time


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


class Article:
    title = None
    link = None
    description = None
    pubDate = None

    def __repr__(self):
        return mod_json.dumps(self.__dict__)


class RssPage(mod_webapp2.RequestHandler):
    def readUrl(self, url):
        data = urllib2.urlopen(url)
        return data.read()

    def formatTime(self, date):
        time_strptime = time.localtime()
        if date != None:
            time_strptime = time.strptime(date.split(",")[1].strip(), "%d.%m.%Y %H:%M")
            #Tue, 28 May 2013 15:30:00 +0100
        return time.strftime("%a, %d %b %Y %H:%M:%S", time_strptime) + " +0100"

    def get(self):
        showName = self.request.get("show")

        baseUrl = 'http://radio.hrt.hr'
        data = self.readUrl(baseUrl + '/slusaonica/?' + urllib.urlencode({'q': showName.encode('utf-8')}))

        searchItems = re.findall(
            r'<article id="(.+?)">.*<input type="hidden" name="file" value="(.+?)" />.*<input type="hidden" name="caption" value="(.+?)" />.*<a href="(.+?)" class="image">.*<img src="(.+?)" alt=".+?" title=".+?">.*</a>.*<p>(.+?)</p>.*<p>Posljednja emisija: <strong>(.+?)</strong></p>.*</article>',
            data, re.DOTALL)
        if (len(searchItems) == 0):
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        searchItem = searchItems[0]
        chanelDetailsUrl = searchItem[3]
        chanelImageUrl = searchItem[4]

        data = self.readUrl(baseUrl + chanelDetailsUrl)
        chennelDataList = re.findall(
            r'<div class="breadcrumbs">.*<ul>.*<li><a href="/">Naslovnica</a></li>.*<li><a href="/slusaonica/">Slušaonica</a></li>.*<li><a href="(.+?)">(.+?)</a></li>.*<li class="selected">.+?</li>.*</ul>.*</div>.*<aside class="aside-content padding">.*<blockquote>.*<h2>.+?</h2>.*<p>(.+?)</p>.*<p class="read_more"><a href=".+?">.+?</a></p>.*</blockquote>.*</aside>.*<h3>Poslušajte</h3>.*<ul>.*<li>.*<a href=".+?">.+?<span class="date">(.+?)</span>.*</a>.*</li>',
            data, re.DOTALL)
        if (len(chennelDataList) == 0):
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        chennelData = chennelDataList[0]

        channel = Channel()
        channel.link = chennelData[0]
        channel.title = chennelData[1]
        channel.description = chennelData[2]
        channel.image = chanelImageUrl
        channel.lastBuildDate = chennelData[3]

        articleDataList = re.findall(r'<div class="widget archive">.*?<h3>Poslušajte</h3>(.*?)</div>', data, re.DOTALL)
        data = ''
        if len(articleDataList) > 0:
            data = articleDataList[0]

        articleDataList = re.findall(r'<li>.*?<a href="(.+?)">(.+?)<span class="date">(.+?)</span>.*?</a>.*?</li>',
                                     data, re.DOTALL)
        for articleData in articleDataList:
            channel.articles.append(self.createArticle(baseUrl, articleData))

        with open('templates/channel_template.xml', 'r') as content_file:
            channelContent = content_file.read()

        channelContent = channelContent.replace("${channel.title}", channel.title)
        channelContent = channelContent.replace("${channel.link}", baseUrl + channel.link)
        channelContent = channelContent.replace("${channel.description}", channel.description)
        channelContent = channelContent.replace("${channel.lastBuildDate}", self.formatTime(channel.lastBuildDate))
        channelContent = channelContent.replace("${channel.image}", baseUrl + channel.image)

        with open('templates/item_template.xml', 'r') as content_file:
            itemContentTemplate = content_file.read()

        items = ""
        for article in channel.articles:
            itemContent = itemContentTemplate
            itemContent = itemContent.replace("${item.title}", article.title)
            itemContent = itemContent.replace("${item.link}", baseUrl + article.link)
            itemContent = itemContent.replace("${item.description}", article.description)
            itemContent = itemContent.replace("${item.pubDate}", self.formatTime(article.pubDate))
            items = items + itemContent

        channelContent = channelContent.replace("${channel.items}", items)

        self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        #self.response.headers['Content-Type'] = 'text/plain'

        self.response.write(channelContent)

    def createArticle(self, baseUrl, articleData):
        data = self.readUrl(baseUrl + articleData[0])

        chennelDatas = re.findall(
            r'<div class="main-content">.*?<article class="article-content">.*?<div class="user-content">.*?<img src="(.+?)" title="(.+?)" alt=".*?" />.*?<h1>.*?</h1>.*?</article>.*?<script type="text/javascript">.*?mp3: "(.+?)".*?</script>.*?</div>',
            data, re.DOTALL)

        article = Article()
        article.link = chennelDatas[0][2]
        article.title = chennelDatas[0][1]
        article.pubDate = articleData[2]
        article.description = ''

        descriptionDatas = re.findall(r'<p class="description">(.+?)</p>', data, re.DOTALL)
        if len(descriptionDatas) > 0:
            article.description = descriptionDatas[0]
        else:
            descriptionDatas = re.findall(r'<div class="content">.*?<p>(.+?)</p>.*?</div>', data, re.DOTALL)
            if len(descriptionDatas) > 0:
                article.description = descriptionDatas[0]

        return article


routes = [
    ('/rss', RssPage),
]

application = mod_webapp2.WSGIApplication(routes, debug=True)
