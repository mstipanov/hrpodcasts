# -*- coding: utf-8 -*-
import logging
import os
import time

from parsers import Parser
from flask import Flask, render_template, send_from_directory, request
from xml.sax.saxutils import escape

app = Flask(__name__)


@app.route('/')
def root():
    return render_template('index.html')


@app.route('/index.html')
def index():
    return render_template('index.html')


@app.route('/robots.txt')
def robots():
    return render_template('robots.txt')


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


@app.route('/liveness_check')
def liveness_check():
    return "OK", 200


@app.route('/readiness_check')
def readiness_check():
    return "OK", 200


@app.route('/rss')
def rss():
    showName = request.args.get("show")

    channel = Parser().parse(showName)
    if not channel:
        return "404 Not Found", 404

    with open('templates/channel_template.xml', 'r') as content_file:
        channelContent = content_file.read()

    channelContent = channelContent.replace("${channel.title}", escape(channel.title))
    channelContent = channelContent.replace("${channel.link}", escape(channel.link))
    channelContent = channelContent.replace("${channel.description}", escape(channel.description))
    channelContent = channelContent.replace("${channel.lastBuildDate}", format_time(None))
    channelContent = channelContent.replace("${channel.image}", channel.image)

    with open('templates/item_template.xml', 'r') as content_file:
        itemContentTemplate = content_file.read()

    items = ""
    for article in channel.articles:
        itemContent = itemContentTemplate
        itemContent = itemContent.replace("${item.title}", escape(article.title))
        itemContent = itemContent.replace("${item.link}", escape(article.link))
        itemContent = itemContent.replace("${item.description}", escape(article.description))
        itemContent = itemContent.replace("${item.pubDate}", format_time(article.pubDate))
        items = items + itemContent

    channelContent = channelContent.replace("${channel.items}", items)

    return channelContent, 200, {'Content-Type': 'text/xml; charset=utf-8'}


def format_time(date):
    time_strptime = time.localtime()
    if date:
        time_strptime = time.strptime(date, "%Y-%m-%dT%H:%M:%SZ")
        #Tue, 28 May 2013 15:30:00 +0100
    return time.strftime("%a, %d %b %Y %H:%M:%S", time_strptime) + " +0100"


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request.')
    return """
    An internal error occurred: <pre>{}</pre>
    See logs for full stacktrace.
    """.format(e), 500


if __name__ == '__main__':
    # This is used when running locally. Gunicorn is used to run the
    # application on Google App Engine. See entrypoint in app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
