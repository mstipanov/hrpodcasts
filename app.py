# -*- coding: utf-8 -*-
import re
import urllib2
import time

import webapp2 as mod_webapp2

from article import Article
from parsers import Parser


class RssPage(mod_webapp2.RequestHandler):
    def readUrl(self, url):
        data = urllib2.urlopen(url)
        return data.read()

    def formatTime(self, date):
        time_strptime = time.localtime()
        if date:
            time_strptime = time.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
            #Tue, 28 May 2013 15:30:00 +0100
        return time.strftime("%a, %d %b %Y %H:%M:%S", time_strptime) + " +0100"

    def get(self):
        showName = self.request.get("show")

        channel = Parser().parse(showName)
        if not channel:
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        with open('templates/channel_template.xml', 'r') as content_file:
            channelContent = content_file.read()

        channelContent = channelContent.replace("${channel.title}", channel.title)
        channelContent = channelContent.replace("${channel.link}", channel.link)
        channelContent = channelContent.replace("${channel.description}", channel.description)
        channelContent = channelContent.replace("${channel.lastBuildDate}", self.formatTime(None))
        channelContent = channelContent.replace("${channel.image}", channel.image)

        with open('templates/item_template.xml', 'r') as content_file:
            itemContentTemplate = content_file.read()

        items = ""
        for article in channel.articles:
            itemContent = itemContentTemplate
            itemContent = itemContent.replace("${item.title}", article.title)
            itemContent = itemContent.replace("${item.link}", article.link)
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
            r'<div class="main-content">.*?<article class="article-content">.*?<div class="user-content">.*?<h1>(.*?)</h1>.*?</article>.*?<script type="text/javascript">.*?mp3: "(.+?)".*?</script>.*?</div>',
            data, re.DOTALL)

        article = Article()
        article.title = chennelDatas[0][0]
        article.link = chennelDatas[0][1]
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
