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

STRIP = re.compile('<(.|\n)*?>')
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

def menu_escape(text):
    return text.replace('_', '__')

def strip_tags(text):
    return STRIP.sub('', text)

def compare(item_x, item_y):
    if item_x.id < item_y.id:
        return 1
    
    elif item_x.id > item_y.id:
        return -1
    
    else:
        return 0

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
import urlparse
import httplib
import threading
import time
import gobject

# Shorter ----------------------------------------------------------------------
SHORT_REGEX = re.compile(r'((https?://|www\.)[^\s]{35,})')
SHORTS = {
    'is.gd': 'http://is.gd/api.php?longurl=%s',
    'tinyurl.com': 'http://tinyurl.com/api-create.php?url=%s',
    'snipurl.com': 'http://snipr.com/site/snip?r=simple&link=%s'
}

SHORTS_LIST = ['is.gd', 'tinyurl.com', 'snipurl.com']


class URLShorter(threading.Thread):
    url_list = {}
    black_list = []
        
    def __init__(self, text, text_box):
        threading.Thread.__init__(self)
        self.text = text
        self.text_box = text_box
        self.daemon = True
        self.start()

    def run(self):
        # Don't make multiple api calls for the same url
        find_urls = SHORT_REGEX.findall(self.text + ' ')
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
            short = self.try_shorten(url, api)
            self.__class__.url_list[url] = short
            return short
        
        except IOError:
            self.__class__.black_list.append(url)
            return url
    
    def try_shorten(self, url, api):
        parsed_url = urlparse.urlparse(url)
        
        # Special treating of youtube links
        if parsed_url.netloc.find('youtube.com') != -1 \
           and parsed_url.path == '/watch':
            video = urlparse.parse_qs(parsed_url.query).get('v', None)
            if video is not None:
                return 'http://youtu.be/%s' % video[0]
        
        # Handle everything else
        else:
            return urllib2.urlopen(SHORTS[api] % urllib2.quote(url)).read()
    
    @classmethod
    def reset(cls):
        cls.url_list = {}
        cls.black_list = []


# Expander ---------------------------------------------------------------------
class URLExpander(threading.Thread):
    url_list = {}
    black_list = []
    
    def __init__(self, url, callback):
        threading.Thread.__init__(self)
        self.url = url
        self.callback = callback
        self.daemon = True
        self.start()

    def run(self):
        # Check for already resolved / failed urls
        if self.__class__.url_list.has_key(self.url):
            current_url = self.__class__.url_list[self.url]
        
        elif self.url in self.__class__.black_list:
            current_url = self.url
        
        else:
            current_url = self.url
            try:
                hops = 0
                while hops < 5:
                    host, path = self.get_url_parts(current_url)
                    conn = httplib.HTTPConnection(host, 80)
                    conn.request('HEAD', path)
                    response = conn.getresponse()
                    if not response.status in (301, 302):
                        raise IOError
                    
                    else:
                        current_url = response.getheader('location', self.url)
                        hops += 1
            
            except IOError:
                self.__class__.black_list.append(current_url)
        
        gobject.idle_add(self.callback, self.url, current_url)
    
    def get_url_parts(self, url):
        pos = 7 if url.lower().startswith('http://') else 8
        host = url[pos:]
        host = host[:host.find('/')]
        path = url[pos + len(host):]
        return host, path
    
    @classmethod
    def reset(cls):
        cls.url_list = {}
        cls.black_list = []

