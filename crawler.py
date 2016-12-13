import re
import codecs
import argparse
import requests
from html.parser import HTMLParser

URL = "http://www.quanxue.cn/ct_nanhuaijin/neijingindex.html"
class url_parser(HTMLParser):

    """This parser  will find all the urls matching 
    the regularation"""

    def __init__(self):
        HTMLParser.__init__(self)
        self.handletag = 'a'
        self.urls = []
        self.url_head = "http://www.quanxue.cn/ct_nanhuaijin/"
        self.url_count = 0

    def handle_starttag(self, tag, attrs):
        if tag == self.handletag:
            reg = r'(NeiJing/NeiJing[0-9]+\.html)'
            for name, value in attrs:
                if name == 'href' and re.search(reg, value):
                    self.urls.append(self.url_head)
                    self.urls[self.url_count] +=  re.search(reg, value).groups()[0]
                    self.url_count += 1
        
class content_parser(HTMLParser):
    def __init__(self):
        HTMLParser.__init__(self)
        self.processing = None
        self.title = []
        self.data = []

    def handle_starttag(self, tag, attrs):
        if tag == 'p':
            self.processing = 'content'
            if attrs:
                for name, value in attrs:
                    if value == 'jingwen':
                        self.data.append('    <%s class=\"yanse\">' % tag)
                    elif value == 'shici':
                        self.data.append('    <%s class=\"yanse\">' % tag)
            else:
                self.data.append('<%s>' % tag)
                    
        elif tag == 'h1':
            self.processing = 'title'
            self.data.append('    <%s class=\"title\">' % tag)

    def handle_data(self, data):
        if self.processing == 'title':
            self.data.append(data.replace("《小言黄帝内经与生命科学》", ''))
            self.title.append(data)
        elif self.processing == 'content':
            if '<' in data or '>' in data:
                data = data.replace('<', '《')
                data = data.replace('>', '》')
            self.data.append(data)
            
    def get_title(self):
        return self.title

    def handle_endtag(self, tag):
        if self.processing:
            if tag == 'p':
                self.processing = None
                self.data.append('</%s>' % tag)
            elif tag == 'h1':
                self.processing = None
                self.data.append('</%s>' % tag)

    def handle_entityref(self, name):
        if self.processing:
            self.data.append('&%s;' % name)

    def handle_charref(self, name):
        if self.processing:
            self.data.append('&#%s;' % name)

def get_urls(url):
    urllists = url_parser()
    page = requests.get(url)
    html = page.text
    urllists.feed(html)
    return urllists.urls

def get_content(url):
    page = requests.get(url)
    page.encoding = 'utf-8'
    html = page.text
    content = content_parser()
    content.feed(html)
    return content.data, content.title

head_template = ('<?xml version="1.0" encoding="utf-8" standalone="no"?>', '\n',
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">', '\n',
        '<html xmlns="http://www.w3.org/1999/xhtml">', '\n',
        '<head>', '\n',
        '<title></title>', '\n',
        '<style type="text/css">', '\n',
        '.content {', '\n',
        '    text-indent:2em;', '\n',
        '}', '\n',
        '.title {', '\n',
        '    color:#CC0099;', '\n',
        '    font-size: 22px;', '\n',
        '    text-align:center;', '\n',
        '}', '\n',
        '.yanse {', '\n',
        '    color: #993300;', '\n',
        '}', '\n',
        '</style>', '\n',
        '</head>', '\n',
        '<body>', '\n')

tail_template = ['</body>', '\n', '</html>']
index = 0
for url in get_urls(URL):
    index += 1
    content, title = get_content(url)
    filename = "Section_" + "%04d" % index + '.xhtml'
    with codecs.open(filename, 'w', "utf-8") as file:
        for item in head_template:
            file.write(item)
        for item in content:
            file.write(item)
        for item in tail_template:
            file.write(item)

    file.close()
