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


# Utility functions and classes ------------------------------------------------
# ------------------------------------------------------------------------------
import gobject

from __init__ import __version__ as VERSION
from settings import CRASH_LOG_FILE

import sys
import re
import time
import traceback
import locale
import urllib2
import urlparse
import httplib
import threading


# Tweepy Wrapper ---------------------------------------------------------------
# ------------------------------------------------------------------------------
try:
    sys.path.insert(0, __file__[:__file__.rfind('/')])
    import tweepy
    TweepError = tweepy.get_error()

finally:
    sys.path.pop(0)


# Python error handling --------------------------------------------------------
# ------------------------------------------------------------------------------
START_TIME = time.time()

def crash_exit():
    # Check if an uncatched error occured
    try:
        if sys.last_traceback is None:
            return
    
    except AttributeError:
        return
    
    # Set date format to english
    locale.setlocale(locale.LC_TIME, 'C')
    
    # Save the crashlog
    trace = traceback.extract_tb(sys.last_traceback)
    with open(CRASH_LOG_FILE, 'ab') as f:
        error = '''Atarashii %s\nStarted at %s\nCrashed at %s\nTraceback:\n''' \
                % (VERSION,
                   time.strftime('%a %b %d %H:%M:%S +0000 %Y',
                   time.gmtime(START_TIME)),
                   
                   time.strftime('%a %b %d %H:%M:%S +0000 %Y',
                   time.gmtime()))
        
        f.write(error + '\n'.join(traceback.format_list(trace)) + '\n')
    
    # Exit with specific error
    sys.exit(70) # os.EX_SOFTWARE

sys.exitfunc = crash_exit


# Escaping stuff ---------------------------------------------------------------
# ------------------------------------------------------------------------------
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


# URL Shortener / Expander------------------------------------------------------
# ------------------------------------------------------------------------------
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
            time.sleep(0.2)
            short_text = self.text_box.get_text()
            for url in urls:
                short = self.shorten_url(url,
                                self.text_box.main.settings['shortener'])
                
                short_text = short_text.replace(url, short)
            
            self.text_box.is_shortening = True
            gobject.idle_add(self.text_box.shorten_text, short_text)
    
    def shorten_url(self, url, api):
        if url in self.__class__.url_list:
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
        if self.url in self.__class__.url_list:
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

