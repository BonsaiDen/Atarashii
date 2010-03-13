#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Tweet Formatter --------------------------------------------------------------
# ------------------------------------------------------------------------------
import re
import urllib

# Some of this code has been translated from the twitter-text-java library:
# <http://github.com/mzsanford/twitter-text-java>
AT_REGEX = re.compile(ur"\B[@\uFF20]([a-z0-9_]{1,20})",
                      re.UNICODE | re.IGNORECASE)
TAG_REGEX = re.compile(ur"(^|[^0-9A-Z&/]+)(#|\uff03)([0-9A-Z_]*[A-Z_]+[a-z0-9_\u00c0-\u00d6\u00d8-\u00f6\u00f8-\u00ff]*)",
                       re.UNICODE | re.IGNORECASE)

PRE_CHARS = "(?:[^/\"':!=]|^|\\:)"
DOMAIN_CHARS = "(?:[\\.-]|[^\\s])+\\.[a-z]{2,}(?::[0-9]+)?"
PATH_CHARS = "(?:[\\.,]?[a-z0-9!\\*'\\(\\);:=\\+\\$/%#\\[\\]\\-_,~@])"
QUERY_CHARS = "[a-z0-9!\\*'\\(\\);:&=\\+\\$/%#\\[\\]\\-_\\.,~]"

# Valid end-of-path chracters (so /foo. does not gobble the period).
# 1. Allow ) for Wikipedia URLs.
# 2. Allow =&# for empty URL parameters and other URL-join artifacts
PATH_ENDING_CHARS = "[a-z0-9\\)=#/]"
QUERY_ENDING_CHARS = "[a-z0-9_&=#]"

URL_REGEX = re.compile("((" + PRE_CHARS + ")((https?://|www\\.)(" + \
                       DOMAIN_CHARS + ")(/" + PATH_CHARS + "*" + \
                       PATH_ENDING_CHARS + "?)?(\\?" + QUERY_CHARS + "*" + \
                       QUERY_ENDING_CHARS + ")?))", re.UNICODE | re.IGNORECASE)

from lang import lang

class Formatter:
    def parse(self, text):
        self.urls = []
        self.users = []
        self.tags = []
        URL_REGEX.sub(self.url, text)
        
        
        # Filter URLS
        self.text_parts = []
        last = 0
        for i in self.urls:
            self.text_parts.append((0, text[last:i.start()]))
            self.text_parts.append((1, text[i.start():i.end()]))
            last = i.end()
        
        self.text_parts.append((0, text[last:]))
        
        # Filter @
        self.filter_by(AT_REGEX, 2)
        
        # Filter Hashtags
        self.filter_by(TAG_REGEX, 3)
        
        # Replace all the stuff
        result = []
        for i in self.text_parts:
            ttype, data = i
            if ttype == 0:
                result.append(data)
            
            # URL
            elif ttype == 1:
                if len(data) > 30:
                    text = data[0:27] + "..."
                else:
                    text = data
                
                result.append(
                    '<a href="%s" title="%s">%s</a>' %
                    (self.escape(data), self.escape(data), text))
            
            # @
            elif ttype == 2:
                at_user = data[1:]
                self.users.append(at_user)
                result.append(
                    ('<a href="http://twitter.com/%s" title="' + lang.html_at +\
                    '">@%s</a>') % (at_user, at_user, at_user))
            
            # tag
            elif ttype == 3:
                pos = data.rfind("#")
                stuff, tag = data[:pos], data[pos + 1:]
                self.tags.append(tag)
                result.append((
                    '%s<a href="http://search.twitter.com/search?%s" title="'+\
                    lang.html_search + '">#%s</a>') %
                    (stuff, urllib.urlencode({'q': '#' + tag}), tag, tag))
                
        return "".join(result)
    
    # Crazy filtering and splitting :O
    def filter_by(self, regex, stype):
        pos = 0
        while pos < len(self.text_parts):
            ttype, data = self.text_parts[pos]
            if ttype == 0:
                match = regex.search(data)
                if match != None:
                    self.text_parts.pop(pos)
                    self.text_parts.insert(pos, 
                                    (0, data[:match.start()]))
                    
                    self.text_parts.insert(pos + 1,
                                    (stype, data[match.start():match.end()]))
                    
                    self.text_parts.insert(pos + 2,
                                    (0, data[match.end():]))
                    pos += 1
            
            pos += 1
    
    def url(self, match):
        self.urls.append(match)
    
    # Regex stuff
    def escape(self, text):
        ent = {
            "&": "&amp;",
            '"': "&quot;",
            "'": "&apos;",
            ">": "&gt;",
            "<": "&lt;"
        }
        return "".join(ent.get(c, c) for c in text)

