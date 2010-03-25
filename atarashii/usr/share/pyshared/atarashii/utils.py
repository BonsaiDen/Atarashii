#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Tweepy Wrapper ---------------------------------------------------------------
# ------------------------------------------------------------------------------
try:
    import sys
    sys.path.insert(0, __file__[:__file__.rfind('/')])
    import tweepy
    TweepError = tweepy.get_error()

finally:
    sys.path.pop(0)
    del sys


# Utility stuff ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import re

STRIP = re.compile("<(.|\n)*?>")
SPACES = re.compile('\s+')
ENTITIES = {
    '&': '&amp;',
    '"': '&quot;',
    '\'': '&apos;',
    '>': '&gt;',
    '<': '&lt;'
}

REPLY_REGEX = re.compile(ur'^[@\uFF20]([a-z0-9_]{1,20})\s.*',
                            re.UNICODE | re.IGNORECASE)
 
MESSAGE_REGEX = re.compile('d ([a-z0-9_]{1,20})\s.*',
                            re.UNICODE | re.IGNORECASE)

def escape(text):
    return ''.join(ENTITIES.get(c, c) for c in text)

def unescape(text):
    for key, value in ENTITIES.iteritems():
        text = text.replace(value, key)
    
    return text

def strip_tags(text):
    return STRIP.sub("", text)

def compare_sub(item_x, item_y):
    if item_x[0].id > item_y[0].id:
        return 1
    
    elif item_x[0].id < item_y[0].id:
        return -1
    
    else:
        return 0
        
# URL Shortener / Expander------------------------------------------------------
# ------------------------------------------------------------------------------
import urllib2
import httplib
import threading
import time
import gobject

SHORT_REGEX = re.compile(r'((https?://|www\.)[^\s]{35,})')
SHORTS = {
    'is.gd' : 'http://is.gd/api.php?longurl=%s',
    'tinyurl.com' : 'http://tinyurl.com/api-create.php?url=%s',
    'snipurl.com' : 'http://snipr.com/site/snip?r=simple&link=%s'
}

SHORTS_LIST = ['is.gd', 'tinyurl.com', 'snipurl.com']
EXPAND_LIST = ['is.gd', 'tl.gd', 'tinyurl.com', 'snipurl.com', 'bit.ly']


class Shortener(threading.Thread):
    url_list = {}
    black_list = []
    
    def __init__(self, text, text_box):
        threading.Thread.__init__(self)
        self.text = text
        self.text_box = text_box
        self.setDaemon(True)
        self.start()

    def run(self):
        # Don't make multiple api calls for the same url
        find_urls = SHORT_REGEX.findall(self.text + " ")
        urls = []
        for url in find_urls:
            if not url[0] in urls and not url[0] in self.__class__.black_list:
                urls.append(url[0])
        
        # Replace them all
        if len(urls) > 0:
            # Wait a bit, this is better for the user experience!
            time.sleep(0.25)
            short_text = self.text_box.get_text()
            for url in urls:
                short = self.shorten_url(url,
                                self.text_box.main.settings['shortener'])
                
                short_text = short_text.replace(url, short)
            
            self.text_box.is_shortening = True
            gobject.idle_add(self.text_box.shorten_text, short_text)
    
    def shorten_url(self, url, api):
        if self.__class__.url_list.has_key(url):
            return self.__class__.url_list[url]
        
        try:
            short = urllib2.urlopen(SHORTS[api] % urllib2.quote(url)).read()
            self.__class__.url_list[url] = short
            return short
        
        except IOError:
            self.__class__.black_list.append(url)
            return url


class Expander(threading.Thread):
    url_list = {}
    black_list = []

    def __init__(self, url, service, callback):
        threading.Thread.__init__(self)
        self.url = url
        self.service = service
        self.callback = callback
        self.setDaemon(True)
        self.start()

    def run(self):
        path = self.url[7 + len(self.service):]
        
        # Check for already resolved / failed urls
        if self.__class__.url_list.has_key(self.url):
            url = self.__class__.url_list[self.url]
        
        elif self.url in self.__class__.black_list:
            url = self.url
        
        # tl.gd urls get just prepended since there a bugs with wrong urls 
        # coming back somehow...
        elif self.service == 'tl.gd':
            url = 'http://www.twitlonger.com/show' + path
        
        else:
            try:
                conn = httplib.HTTPConnection('bit.ly', 80)
                conn.request('HEAD', path)
                response = conn.getresponse()
                if not response.status == 301:
                    raise IOError
                
                else:
                    url = response.getheader('location', self.url)
            
            except IOError:
                self.__class__.black_list.append(self.url)
                url = self.url
        
        gobject.idle_add(self.callback, self.url, url)

