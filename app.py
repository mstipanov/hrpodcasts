# -*- coding: utf-8 -*-
import json as mod_json
import re
import urllib

import webapp2 as mod_webapp2
import urllib2
from HTMLParser import HTMLParser
import time

class Channel:
    title = None
    link = None
    image = None
    description = None
    lastBuildDate = None
    articles = []

    def __init__(self):
        self.articles = []

    def __repr__(self):
        return mod_json.dumps(self.__dict__)

class Article:
    aricleId = None
    title = None
    link = None
    description = None
    pubDate = None

    def __init__(self, aricleId):
        self.aricleId = aricleId

    def __repr__(self):
        return mod_json.dumps(self.__dict__)

class ItemsHTMLParser(HTMLParser):
    articleDiv = False
    innerDivCount = 0
    article = None
    channel = None
    readDescription = False
    readPubDateStrong = False
    readPubDate = False

    def __init__(self, channel):
        HTMLParser.__init__(self)
        self.channel = channel

    def handle_starttag(self, tag, attrs):
        if not self.articleDiv and tag == "div" and self.tagContainsAttrs(attrs, [("class", "article-listing vertical")]):
            self.articleDiv = True
        elif self.articleDiv and tag == "div":
            self.innerDivCount = self.innerDivCount + 1
        elif self.articleDiv and tag == "article":
            self.article = Article(self.getTagAttr(attrs, "id"))
            self.channel.articles.append(self.article)
        elif self.articleDiv and not self.article == None and tag == 'input' and self.tagContainsAttrs(attrs, [("type", "hidden"), ("name", "file")]):
            self.article.link = self.getTagAttr(attrs, "value")
        elif self.articleDiv and not self.article == None and tag == 'input' and self.tagContainsAttrs(attrs, [("type", "hidden"), ("name", "caption")]):
            self.article.title = self.getTagAttr(attrs, "value")
        elif self.articleDiv and not self.article == None and tag == 'a' and self.tagContainsAttrs(attrs, [("class", "image")]):
            self.channel.link = self.getTagAttr(attrs, "href")
            self.readImage = True
        elif self.articleDiv and not self.article == None and tag == 'img' and self.readImage:
            self.readImage = False
            self.channel.image = self.getTagAttr(attrs, "src")
        elif self.articleDiv and not self.article == None and self.article.description == None and tag == 'p':
            self.readDescription = True
        elif self.articleDiv and not self.article == None and not self.article.description == None and tag == 'p':
            self.readPubDateStrong = True
        elif self.articleDiv and not self.article == None and not self.article.description == None and self.readPubDateStrong and tag == 'strong':
            self.readPubDateStrong = False
            self.readPubDate = True

    def handle_endtag(self, tag):
        if self.articleDiv and self.innerDivCount > 0 and tag == "div":
            self.innerDivCount = self.innerDivCount - 1
        elif self.articleDiv and self.innerDivCount == 0 and tag == "div":
            self.articleDiv = False
        elif self.articleDiv and tag == "article":
            self.article = None
        elif self.articleDiv and not self.article == None and tag == 'p':
            self.readDescription = False

    def handle_data(self, data):
        if self.articleDiv and not self.article == None and self.readDescription:
            self.article.description = data
            self.readDescription = False
        elif self.readPubDate:
            self.article.pubDate = data
            self.readPubDate = False

    def handle_comment(self, data):
        #print "Comment  :", data
        pass

    def handle_entityref(self, name):
        #c = unichr(name2codepoint[name])
        #print "Named ent:", c
        pass

    def handle_charref(self, name):
        #if name.startswith('x'):
        #    c = unichr(int(name[1:], 16))
        #else:
        #    c = unichr(int(name))
        #print "Num ent  :", c
        pass

    def handle_decl(self, data):
        #print "Decl     :", data
        pass

    def tagContainsAttrs(self, allAttrs, attrs):
        for attr in attrs:
            found = False
            key, value = attr
            for allAttr in allAttrs:
                allKey, allValue = allAttr
                if key == allKey and value == allValue:
                    found = True
                    break
            if not found:
                return False

        return True

    def getTagAttr(self, attrs, attrKey):
        for attr in attrs:
            key, value = attr
            if key == attrKey:
                return value

        return None

class ChannelHTMLParser(HTMLParser):
    articleDiv = False
    aside = False
    readDescription = False
    readTitle = False
    channel = None
    dateSpanCount = -1
    doReadTitle = False
    readLastBuildDate = False

    def __init__(self, channel):
        HTMLParser.__init__(self)
        self.channel = channel
        self.channel.link = None

    def handle_starttag(self, tag, attrs):
        if not self.articleDiv and tag == "article" and self.tagContainsAttrs(attrs, [("class", "article-content")]):
            self.articleDiv = True
        elif not self.articleDiv and tag == "div" and self.tagContainsAttrs(attrs, [("class", "breadcrumbs")]):
            self.readTitle = True
        elif not self.articleDiv and self.readTitle and not self.doReadTitle and tag == "a":
            self.doReadTitle = True
        elif not self.articleDiv and self.doReadTitle and tag == "li" and self.tagContainsAttrs(attrs, [("class", "selected")]):
            self.readTitle = False
            self.doReadTitle = False
        elif self.articleDiv and tag == "p" and self.tagContainsAttrs(attrs, [("class", "meta")]):
            self.dateSpanCount = 3
        elif self.articleDiv and tag == "span" and self.dateSpanCount > 0:
            self.dateSpanCount = self.dateSpanCount - 1
        elif self.articleDiv and tag == "aside" and self.tagContainsAttrs(attrs, [("class", "aside-content padding")]):
            self.aside = True
        elif self.aside and self.channel.description == None and tag == 'p':
            self.readDescription = True
        elif self.aside and self.channel.description != None and self.channel.link == None and tag == 'a':
            self.channel.link = self.getTagAttr(attrs, "href")

#<div class="breadcrumbs">
#<ul>
#<li><a href="/">Naslovnica</a></li>
#<li><a href="/slusaonica/">Slušaonica</a></li>
#<li><a href="/arhiva/dnevne-novosti/575/">Dnevne novosti</a></li>
#<li class="selected">Dnevne novosti 06.06.</li>
#</ul>
#</div>

    def handle_endtag(self, tag):
        if self.aside and self.readDescription and tag == 'p':
            self.readDescription = False
        elif self.dateSpanCount == -2 and tag == 'i':
            self.dateSpanCount = -3

    def handle_data(self, data):
        if self.doReadTitle and len(data.strip()) > 0:
            self.channel.title = data
        elif self.readDescription:
            self.channel.description = data
            self.readDescription = False
        elif data == "Emitirano:":
            self.readLastBuildDate = True
        elif self.readLastBuildDate:
            self.channel.lastBuildDate = data
            self.readLastBuildDate = False
        elif self.dateSpanCount == -3:
            self.channel.lastBuildDate = data
            self.dateSpanCount = -1

    def handle_comment(self, data):
        #print "Comment  :", data
        pass

    def handle_entityref(self, name):
        #c = unichr(name2codepoint[name])
        #print "Named ent:", c
        pass

    def handle_charref(self, name):
        #if name.startswith('x'):
        #    c = unichr(int(name[1:], 16))
        #else:
        #    c = unichr(int(name))
        #print "Num ent  :", c
        pass

    def handle_decl(self, data):
        #print "Decl     :", data
        pass

    def tagContainsAttrs(self, allAttrs, attrs):
        for attr in attrs:
            found = False
            key, value = attr
            for allAttr in allAttrs:
                allKey, allValue = allAttr
                if key == allKey and value == allValue:
                    found = True
                    break
            if not found:
                return False

        return True

    def getTagAttr(self, attrs, attrKey):
        for attr in attrs:
            key, value = attr
            if key == attrKey:
                return value

        return None


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

        items = re.findall(r'<article id="(.+?)">.*<input type="hidden" name="file" value="(.+?)" />.*<input type="hidden" name="caption" value="(.+?)" />.*<a href="(.+?)" class="image">.*<img src="(.+?)" alt=".+?" title=".+?">.*</a>.*<p>(.+?)</p>.*<p>Posljednja emisija: <strong>(.+?)</strong></p>.*</article>', data, re.DOTALL)
        if(len(items) == 0):
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        channel = Channel()
        chanelDetailsUrl=None
        chanelImageUrl=None
        for item in items:
            article = Article(item[0])
            article.link = item[1]
            article.title = item[2]
            chanelDetailsUrl= item[3]
            chanelImageUrl = item[4]
            article.description = item[5]
            article.pubDate = item[6]
            channel.articles.append(article)

        data = self.readUrl(baseUrl + chanelDetailsUrl)

        chennelDatas = re.findall(r'<div class="breadcrumbs">.*<ul>.*<li><a href="/">Naslovnica</a></li>.*<li><a href="/slusaonica/">Slušaonica</a></li>.*<li><a href="(.+?)">(.+?)</a></li>.*<li class="selected">.+?</li>.*</ul>.*</div>.*<aside class="aside-content padding">.*<blockquote>.*<h2>.+?</h2>.*<p>(.+?)</p>.*<p class="read_more"><a href=".+?">.+?</a></p>.*</blockquote>.*</aside>.*<h3>Poslušajte</h3>.*<ul>.*<li>.*<a href=".+?">.+?<span class="date">(.+?)</span>.*</a>.*</li>', data, re.DOTALL)
        if(len(chennelDatas) == 0):
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        chennelData = chennelDatas[0]
        channel.link = chennelData[0]
        channel.title = chennelData[1]
        channel.description = chennelData[2]
        channel.image = chanelImageUrl
        channel.lastBuildDate = chennelData[3]


        with open('templates/channel_template.xml', 'r') as content_file:
            channelContent = content_file.read()

        channelContent = channelContent.replace("${channel.title}", channel.title)
        channelContent = channelContent.replace("${channel.link}", baseUrl + channel.link)
        channelContent = channelContent.replace("${channel.description}", channel.description)
        channelContent = channelContent.replace("${channel.lastBuildDate}", self.formatTime(channel.lastBuildDate))

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

    def get2(self):
        showName = self.request.get("show")

        baseUrl = 'http://radio.hrt.hr'
        data = self.readUrl(baseUrl + '/slusaonica/?' + urllib.urlencode({'q': showName}))

        channel = Channel()
        itemsParser = ItemsHTMLParser(channel)
        itemsParser.feed(data)

        if(len(channel.articles) == 0):
            self.response.status = '404 Not Found'
            self.response.write('404 Not Found')
            return

        data = self.readUrl(baseUrl + channel.link)
        channelParser = ChannelHTMLParser(channel)
        channelParser.feed(data)

        with open('templates/channel_template.xml', 'r') as content_file:
            channelContent = content_file.read()

        channelContent = channelContent.replace("${channel.title}", channel.title)
        channelContent = channelContent.replace("${channel.link}", baseUrl + channel.link)
        channelContent = channelContent.replace("${channel.description}", channel.description)
        channelContent = channelContent.replace("${channel.lastBuildDate}", self.formatTime(channel.lastBuildDate))

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

        #self.response.headers['Content-Type'] = 'text/xml; charset=utf-8'
        self.response.headers['Content-Type'] = 'text/plain'

        self.response.write(channelContent)

routes = [
    ('/rss', RssPage),
]

application = mod_webapp2.WSGIApplication(routes, debug=True)
