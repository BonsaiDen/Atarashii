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


# Constants --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import sys
import time
import re
import os


# Time / Paths / DBUS ----------------------------------------------------------
# ------------------------------------------------------------------------------
START_TIME = time.time()

HOME_DIR = os.path.expanduser('~')
DESKTOP_FILE = os.path.join(HOME_DIR, '.config',
                            'autostart', 'atarashii.desktop')

AUTOSTART_DIR = os.path.join(HOME_DIR, '.config', 'autostart')
CACHE_DIR = os.path.join(HOME_DIR, '.cache', 'atarashii')

ATARASHII_DIR = os.path.join(HOME_DIR, '.atarashii')

CONFIG_FILE = os.path.join(ATARASHII_DIR, 'atarashii.conf')
USERLIST_FILE = os.path.join(ATARASHII_DIR, 'usernames.list')
COPY_FILE = '/usr/share/applications/atarashii.desktop'
CRASH_FILE = os.path.join(HOME_DIR, '.atarashii', 'crashed')
CRASH_LOG_FILE = os.path.join(ATARASHII_DIR, 'crash.log')
ERROR_LOG_FILE = os.path.join(ATARASHII_DIR, 'error.log')
LOGOUT_FILE = os.path.join(ATARASHII_DIR, 'logout')

# DBUS
DESK_NAME = 'org.freedesktop.DBus'
DESK_PATH = '/org/freedesktop/DBus'

DBUS_NAME = 'org.bonsaiden.Atarashii'
DBUS_PATH = '/org/bonsaiden/Atarashii'


# Generic Stuff ----------------------------------------------------------------
# ------------------------------------------------------------------------------
UNSET_TOOLTIP = ''       # Should be ''
UNSET_PASSWORD = ''      # Must be ''
UNSET_RESOURCE = ''      # Should be ''
UNSET_SETTING = ''       # Must be ''
UNSET_USERNAME = ''      # Must be ''
UNSET_ID_NUM = -1        # Must be lower than 0
UNSET_TEXT = ''          # Must be ''
UNSET_LABEL = ''         # Should be ''
UNSET_TIMEOUT = -1       # Must be lower than 0
UNSET_ERROR = ''         # Must be ''
UNSET_SOUND = ''         # Must be ''
UNSET_HOST = ''          # Must be ''
UNSET_URL = ''           # Must be ''

USERNAME_CHARS = 'abcdefghijklmnopqrstuvwxyz' \
                 + 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
                 + '_1234567890'

CACHE_TIMEOUT = 60 * 60 * 24 * 7 # 7 Days
USERLIST_TIMEOUT = 60 * 60 * 2 # 2 Hours

# Rewteets
RETWEET_NEW = 1          # Can be anything
RETWEET_OLD = 2          # Can be anything

# Message Dialogs, can be anything
MESSAGE_ERROR = 1
MESSAGE_WARNING = 2
MESSAGE_QUESTION = 3
MESSAGE_INFO = 4

# Buttons, can be anything
BUTTON_REFRESH = 1
BUTTON_READ = 2
BUTTON_HISTORY = 3


# Views ------------------------------------------------------------------------
# ------------------------------------------------------------------------------
MODE_TWEETS = 0          # Can be anything
MODE_MESSAGES = 1        # Can be anything
MODE_SEARCH = 2          # Can be anything, currently unused
MODE_PROFILE = 4

# HTML
HTML_UNSET_ID = -1       # Must be lower than 0
HTML_UNSET_TEXT = ''     # Should be ''
HTML_RESET = -1          # Can be anything
HTML_LOADING = 0         # Can be anything
HTML_LOADED = 1          # Can be anything
HTML_STATE_NONE = 0      # Can be anything
HTML_STATE_START = 1     # Can be anything
HTML_STATE_SPLASH = 2    # Can be anything
HTML_STATE_RENDER = 3    # Can be anything

# Sizes
FONT_DEFAULT = 10
FONT_SIZES = [9, 10, 11, 12, 16]
AVATAR_DEFAULT = 32
AVATAR_SIZES = [24, 32, 40, 48, 64, 96]
THEME_DEFAULT = 'fuji_blue_default'


# Errors, should be below 0 ----------------------------------------------------
# ------------------------------------------------------------------------------
ERR_TWEET_NOT_FOUND = -12
ERR_MESSAGE_NOT_FOUND = -13
ERR_ALREADY_RETWEETED = -2
ERR_TWEET_DUPLICATED = -11
ERR_USER_NOT_FOUND = -3
ERR_USER_NOT_FOLLOW = -15

ERR_RATE_RECONNECT = -7
ERR_RATE_LIMIT = -6

ERR_NETWORK_FAILED = -4
ERR_NETWORK_TWITTER_FAILED = -9

ERR_URLLIB_FAILED = -2
ERR_URLLIB_TIMEOUT = -3

# HTTP status codes, guess what they should be...
HT_400_BAD_REQUEST = 400
HT_401_UNAUTHORIZED = 401
HT_403_FORBIDDEN = 403
HT_404_NOT_FOUND = 404
HT_500_INTERNAL_SERVER_ERROR = 500
HT_502_BAD_GATEWAY = 502
HT_503_SERVICE_UNAVAILABLE = 503

ERR_NAMES = [i for i in dir() if i.startswith('ERR') or i.startswith('HT')]

# Must be defined after ERR_NAMES otherwise we try to make a hash from a dict
# which of course doesn't work
ERR_MAPPING = {}
for i in ERR_NAMES:
    ERR_MAPPING[sys.modules[__name__].__dict__[i]] = i


# Status Flags -----------------------------------------------------------------
# ------------------------------------------------------------------------------
ST_NONE = 0
ST_CONNECT = 1
ST_RECONNECT = 2
ST_UPDATE = 4
ST_SEND = 8
ST_HISTORY = 16
ST_DELETE = 32
ST_ALL_PENDING = ST_CONNECT | ST_RECONNECT | ST_UPDATE | ST_SEND | \
                 ST_HISTORY | ST_DELETE

# Was stuff
ST_WAS_SEND = 64
ST_WAS_RETWEET = 128
ST_WAS_RETWEET_NEW = 256
ST_WAS_DELETE = 512
ST_WAS_ALL = ST_WAS_SEND | ST_WAS_RETWEET | ST_WAS_RETWEET_NEW | ST_WAS_DELETE

# Warning stuff
ST_WARNING_RATE = 1024

# Login Stuff
ST_LOGIN_ERROR = 4096
ST_LOGIN_SUCCESSFUL = 8192
ST_LOGIN_COMPLETE = 16384
ST_LOGIN_ALL = ST_LOGIN_ERROR | ST_LOGIN_SUCCESSFUL | ST_LOGIN_COMPLETE

# Network
ST_NETWORK_FAILED = 32768
ST_TRAY_WARNING = 65536

# All
ST_ALL = ST_ALL_PENDING | ST_WAS_ALL | ST_WARNING_RATE | ST_LOGIN_ALL | \
         ST_NETWORK_FAILED | ST_TRAY_WARNING


# Shortening / Escaping / Textbox ----------------------------------------------
# ------------------------------------------------------------------------------
SHORT_REGEX = re.compile(r'((https?://|www\.)[^\s]{35,})')
SHORTS = {
    'is.gd': 'http://is.gd/api.php?longurl=%s',
    'tinyurl.com': 'http://tinyurl.com/api-create.php?url=%s',
    'snipurl.com': 'http://snipr.com/site/snip?r=simple&link=%s',
    'u.nu': 'http://u.nu/unu-api-simple?url=%s'
}

SHORTS_LIST = [e for i, e in sorted([(len(i), i) for i in SHORTS.keys()])]

# Note the missing lowercase l, the uppercase I, the O and the 0(zero)
BASE58 = '123456789abcdefghijkmnopqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ'

# Escaping
STRIP = re.compile('<(.|\n)*?>')
SPACES = re.compile('\s+')
ENTITIES = {
    '&': '&amp;',
    '"': '&quot;',
    '\'': '&apos;',
    '>': '&gt;',
    '<': '&lt;'
}

# Textbox
MSG_SIGN = 'd'
AT_SIGNS = u'@\uFF20'

CONTINUATION = '...'

REPLY_REGEX = re.compile(ur'^[@\uFF20]([a-z0-9_]{1,20})\s.*',
                            re.UNICODE | re.IGNORECASE)

MESSAGE_REGEX = re.compile('d\s([a-z0-9_]{1,20})\s.*',
                            re.UNICODE | re.IGNORECASE)

