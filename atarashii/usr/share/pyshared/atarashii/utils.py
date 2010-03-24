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
        
# URL Shortener ----------------------------------------------------------------
# ------------------------------------------------------------------------------
SHORT_REGEX = re.compile(r'((https?://|www\.)[^\s]{35,})')
SHORTS = {
    'is.gd' : 'http://is.gd/api.php?longurl=%s',
    'tinyurl.com' : 'http://tinyurl.com/api-create.php?url=%s',
    'snipurl.com' : 'http://snipr.com/site/snip?r=simple&link=%s'
}

SHORTS_LIST = ['is.gd', 'tinyurl.com', 'snipurl.com']
EXPAND_LIST = ['is.gd', 'tl.gd', 'tinyurl.com', 'snipurl.com', 'bit.ly']

import urllib2
import threading
import time
import gobject


# FIXME clean this up...
class Shortener(threading.Thread):
    def __init__(self, textbox):
        threading.Thread.__init__(self)
        self.textbox = textbox
        self.reset()
    
    def reset(self):
        self.text = ''
        self.blacklist = []
        self.url_list = {}
        
        self.expand = ''
        self.expand_callback = None
    
    def run(self):
        while True:
            # Expand a URL
            if self.expand != '':
                url = self.expand_url(self.expand)
                print url
                gobject.idle_add(self.expand_callback, self.expand, url)
                self.expand = ''
            
            # Shorten a URL
            if self.text != '':
                find_urls = SHORT_REGEX.findall(self.text + " ")
                
                # Don't make multiple api calls for the same url
                urls = []
                for url in find_urls:
                    if not url[0] in urls and not url[0] in self.blacklist:
                        urls.append(url[0])
                
                # Replace them all
                if len(urls) > 0:
                    # Wait a bit, this is better for the user experience!
                    time.sleep(0.25)
                    box_text = self.textbox.get_text()
                    for url in urls:
                        short = self.shorten_url(url,
                                        self.textbox.main.settings['shortener'])
                        
                        box_text = box_text.replace(url, short)
                    
                    self.textbox.is_shortening = True
                    gobject.idle_add(self.textbox.shorten_text, box_text)
                
                self.text = ''
            
            # Fix a bug when the modules get unloaded, since we're set to Daemon
            if time == None:
                break
            
            time.sleep(0.1)
    
    def shorten_url(self, url, api):
        if self.url_list.has_key(url):
            return self.url_list[url]
        
        try:
            short = urllib2.urlopen(SHORTS[api] % urllib2.quote(url)).read()
            self.url_list[url] = short
            return short
        
        except IOError:
            self.blacklist.append(url)
            return url
    
    def expand_url(self, url):
        try:
            return urllib2.urlopen(url).geturl()
        
        except IOError:
            return url

