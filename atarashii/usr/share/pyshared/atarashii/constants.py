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
# Rewteets
RETWEET_NEW = 1          # Can be anything
RETWEET_OLD = 2          # Can be anything

# General Stuff
UNSET_ID_NUM = -1        # Must be lower than 0
UNSET_TEXT = ""          # Must be ""
UNSET_LABEL = ""         # Should be ""
UNSET_TIMEOUT = -1       # Don't know if this is needed anymore at all...

# Modes
MODE_TWEETS = 0          # Can be anything
MODE_MESSAGES = 1        # Can be anything
MODE_SEARCH = 2          # Can be anything, currently unused

# HTML
HTML_UNSET_ID = -1       # Must be lower than 0
HTML_RESET = -1          # Can be anything
HTML_LOADING = 0         # Can be anything
HTML_LOADED = 1          # Can be anything
HTML_STATE_NONE = 0      # Can be anything
HTML_STATE_START = 1     # Can be anything
HTML_STATE_SPLASH = 2    # Can be anything
HTML_STATE_RENDER = 3    # Can be anything

# Message Dialogs
MESSAGE_ERROR = 1        # Can be anything
MESSAGE_WARNING = 2      # Can be anything
MESSAGE_QUESTION = 3     # Can be anything
MESSAGE_INFO = 4         # Can be anything


# Status Flags -----------------------------------------------------------------
ST_NONE = 0
ST_CONNECT = 1
ST_RECONNECT = 2
ST_UPDATE = 4
ST_SEND = 8
ST_HISTORY = 16
ST_DELETE = 32
ST_ALL_PENDING = ST_CONNECT | ST_RECONNECT | ST_UPDATE | ST_SEND | ST_HISTORY |\
                 ST_DELETE

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

# All
ST_ALL = ST_ALL_PENDING | ST_WAS_ALL | ST_WARNING_RATE | ST_LOGIN_ALL | \
         ST_NETWORK_FAILED

