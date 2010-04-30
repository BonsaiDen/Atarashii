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

import sys
import re
import htmlentitydefs
import time
import urllib2
import urlparse
import httplib
import threading
import calendar

from constants import UNSET_STRING, UNSET_HOST, UNSET_URL
from constants import ENTITIES, STRIP, SHORT_REGEX, SHORTS, BASE58


# Tweepy Wrapper ---------------------------------------------------------------
# ------------------------------------------------------------------------------
try:
    sys.path.insert(0, __file__[:__file__.rfind('/')])
    import tweepy
    TweepError = tweepy.get_error()

finally:
    sys.path.pop(0)


# Escaping stuff ---------------------------------------------------------------
# ------------------------------------------------------------------------------
def escape(text):
    return UNSET_STRING.join(ENTITIES.get(c, c) for c in text)


# Credit to Fredrik Lundh
# http://effbot.org/zone/re-sub.htm#unescape-html
def unescape(text):
    
    def fixup(match):
        text = match.group(0)
        if text[:2] == '&#':
            try:
                if text[:3] == '&#x':
                    return unichr(int(text[3:-1], 16))
                
                else:
                    return unichr(int(text[2:-1]))
            
            except ValueError:
                pass
        
        else:
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            
            except KeyError:
                pass
        
        return text
    
    return re.sub('&#?\w+;', fixup, text)

def menu_escape(text):
    return text.replace('_', '__')

def strip_tags(text):
    return STRIP.sub(UNSET_STRING, text)

def filter_chars(text, chars):
    return UNSET_STRING.join([i for i in text if i in chars])


# Time stuff -------------------------------------------------------------------
# ------------------------------------------------------------------------------
def gmtime(value=None):
    if value is None:
        return long(calendar.timegm(time.gmtime()))
    
    else:
        return long(calendar.timegm(value.timetuple()))

def localtime(value=None):
    return time.localtime(gmtime(value))


# URL Shortener / Expander------------------------------------------------------
# ------------------------------------------------------------------------------
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
            if not url[0] in urls and not url[0] in self.black_list:
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
        if url in self.url_list:
            return self.url_list[url]
        
        try:
            short = self.try_shorten(url, api).strip()
            if not short.lower().startswith('http://'):
                raise ValueError
            
            self.url_list[url] = short
            return short
        
        except (IOError, ValueError):
            self.black_list.append(url)
            return url
    
    def try_shorten(self, url, api):
        parsed_url = urlparse.urlparse(url)
        
        # Special treating of youtube links
        if parsed_url.netloc.find('youtube.com') != -1 \
           and parsed_url.path == '/watch':
            video = urlparse.parse_qs(parsed_url.query).get('v', None)
            if video is None:
                video = urlparse.parse_qs(
                                 parsed_url.fragment.strip('!')).get('v', None)
            
            if video is not None:
                return 'http://youtu.be/%s' % video[0]
            
            else:
                raise ValueError
        
        # Special handling of flickr links, those will be base58 encoded
        elif parsed_url.netloc.find('flickr.com') != -1:
            photo_id = -1
            for i in parsed_url.path.strip('/').split('/')[::-1]:
                try:
                    photo_id = long(i)
                    break
                
                except ValueError:
                    pass
            
            # Give up, we could not find the photo id
            if photo_id == -1:
                raise ValueError
            
            # Base58 encode the id
            url = UNSET_URL
            while photo_id >= 58:
                div, mod = divmod(photo_id, 58)
                url = BASE58[mod] + url
                photo_id = int(div)
            
            return 'http://flic.kr/p/%s' % BASE58[photo_id] + url
        
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
        if self.url in self.url_list:
            current_url = self.url_list[self.url]
        
        elif self.url in self.black_list:
            current_url = self.url
        
        else:
            current_url = self.url
            try:
                hops = 0
                last_host = UNSET_HOST
                while hops < 5:
                    host, path = self.get_url_parts(current_url)
                    if host != UNSET_HOST:
                        last_host = host
                    
                    conn = httplib.HTTPConnection(host, 80)
                    conn.request('HEAD', path)
                    response = conn.getresponse()
                    if not response.status in (301, 302):
                        raise IOError
                    
                    else:
                        current_url = response.getheader('location', self.url)
                        
                        # Work around locations without hosts
                        # Who the hell would return something like that?
                        # Flickr does with 'flic.kr' links
                        # Wordpress does this too
                        if not current_url.startswith('http:'):
                            if not last_host.startswith('http'):
                                last_host = 'http://' + last_host
                            
                            current_url = last_host.rstrip('/') \
                                          + '/' + current_url.lstrip('/')
                        
                        hops += 1
            
            except IOError:
                self.black_list.append(current_url)
        
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

