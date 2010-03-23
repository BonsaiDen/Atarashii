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

def compare(item_x, item_y):
    if item_x.id > item_y.id:
        return -1
    
    elif item_x.id < item_y.id:
        return 1
    
    else:
        return 0
        
def compare_sub(item_x, item_y):
    if item_x[0].id > item_y[0].id:
        return 1
    
    elif item_x[0].id < item_y[0].id:
        return -1
    
    else:
        return 0

