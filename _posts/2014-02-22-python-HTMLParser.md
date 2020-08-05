---
title: HTMLParser 提取网页元素
category: python
---

The `HTMLParser` class is instantiated without arguments. An `HTMLParser` instance is fed HTML data and calls handler functions when tags begin and end. The `HTMLPrser` class is meant to be overridden by the user to provide a desired behavior.
<!--more-->

Ulike the parser in `htmllib`, this parser does not check that end tags match start tags or call the end-tag handler for elements which are closed implicitly by closing an outer element.

A simple example:

``` python
from HTMLParser import HTMLParser

class MyHTMLParser(HTMLParser):

    def handle_starttag(self, tag, attrs):
        print "Encountered the beginning of a %s tag" % tag

    def handle_endtag(self, tag):
        print "Encountered the end of a %s tag" % tag

if __name__=="__main__":
    IParser = MyHTMLParser()
    IParser.feed(urllib.urlopen("http://www.python.org/index.html").read())
```

上面这个程序会输出 `http://www.python.org/index.html` 上的所有标签

## 下面我们再来看一个使用 `HTMLParser` 提取网页标签信息的例子

``` python
import HTMLParser
class HtmlAna(HTMLParser.HTMLParser):
    def __init__(self):
            HTMLParser.HTMLParser.__init__(self)
            self.Recording = 0
            self.recType = ''
            self.tData  = []
            self.tLink  = []
            self.tid    = []
            self.uData  = []

    def handle_starttag(self, tag, attrs):
        if tag != 'a':
            return
        if self.Recording:
            self.Recording += 1
            return
        for name, value in attrs:
            if name == 'href':
                self.tmpURI = value
            if name == 'class':
                if value == 'j_th_tit':
                    self.Recording = 1
                    self.tLink.append(self.tmpURI)
                    self.tid.append(self.tmpURI[3:])
                    self.recType = 't'
                if value == 'j_user_card' or value == 'sign_highlight j_user_card':
                    self.Recording = 1
                    self.recType = 'u'
                break
            else:
                continue

    def handle_endtag(self, tag):
        if tag == 'a' and self.Recording:
            self.Recording -= 1

    def handle_data(self, data):
        if self.Recording:
            if self.recType == 't':

f = file('test.txt', 'r')
str = f.read().decode('utf-8')
f.close

myHA = HtmlAna()
myHA.feed(str)
```

例程中 `str` 是百度贴吧首页的 html 源码。运行程序可以把贴吧中 帖子标题，帖子链接，帖子id，和发帖人用户名抓取到列表 self.tData, self.tLink, self.tid, self.uData

html 源码参见下列信息：
``` html
<a class="j_th_tit" target="_blank" title="(帖子标题)" href="(帖子链接)">(帖子标题)</a>
<a class="j_user_card" target="_blank" href="****" data-field="{"un":"****"}">(用户名)</a>
<a class="sign_highlight j_user_card" target="_blank" href="****" title="****" data-field="{"un":"****"}">(用户名)</a>
```
