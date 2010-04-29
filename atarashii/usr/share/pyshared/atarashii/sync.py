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


# Syncer -----------------------------------------------------------------------
# ------------------------------------------------------------------------------
import httplib
import urllib

import threading

from errors import log_error
from constants import UNSET_USERNAME, HTML_UNSET_ID
from constants import SYNC_KEY_CHARS, SYNC_SERVER_HOST, SYNC_SERVER_PORT, \
                      SYNC_MAX_TRIES


class Async(threading.Thread):
    def __init__(self, callback, *args):
        threading.Thread.__init__(self)
        self.callback = callback
        self.args = args
        self.start()
    
    def run(self):
        self.callback(*self.args)


class Syncer(object):
    def __init__(self, main):
        self.main = main
        self.gui = main.gui
        self.settings = main.settings
        self.key = None
        self.pending = False
        self.reset()
    
    def reset(self):
        self.first_tweet = HTML_UNSET_ID
        self.last_tweet = HTML_UNSET_ID
        self.first_message = HTML_UNSET_ID
        self.last_message = HTML_UNSET_ID
    
    
    # Sync up to the cloud -----------------------------------------------------
    # --------------------------------------------------------------------------
    def set_ids(self):
        if self.settings['syncing'] is not True:
            return False
        
        if self.main.username == UNSET_USERNAME:
            return False
        
        # Check for change
        username = self.main.username
        if self.first_tweet < self.settings['firsttweet_' + username] \
           or self.last_tweet < self.settings['lasttweet_' + username] \
           or self.first_message < self.settings['firstmessage_' + username] \
           or self.last_message < self.settings['lastmessage_' + username]:
            
            pass
        
        else:
            return False
        
        # Start async
        Async(self.async_set_ids, username)
    
    def async_set_ids(self, username):
        self.pending = True
        if self.get_key():
            try:
                self.request('set', {
                    'token': self.key,
                    'user': username,
                    'first_tweet': self.settings['firsttweet_' + username],
                    'last_tweet': self.settings['lasttweet_' + username],
                    'first_message': self.settings['firstmessage_' + username],
                    'last_message': self.settings['lastmessage_' + username]
                })
                
                # Set stuff
                self.first_tweet = self.settings['firsttweet_' + username]
                self.last_tweet = self.settings['lasttweet_' + username]
                self.first_message = self.settings['firstmessage_' + username]
                self.last_message = self.settings['lastmessage_' + username]
                self.pending = False
                return True
            
            except IOError:
                if self.settings['syncing']:
                    self.main.on_sync_up_fail()
                
                log_error('Syncing up failed')
                self.pending = False
                return False
        
        else:
            self.pending = False
            return False
    
    
    # Sync down to Atarashii ---------------------------------------------------
    # --------------------------------------------------------------------------
    def get_ids(self):
        if self.settings['syncing'] is not True:
            return False
        
        if self.main.username == UNSET_USERNAME:
            return False
        
        if self.get_key():
            try:
                username = self.main.username
                data = self.request('get', {'token': self.key,
                                            'user': username})
                
                # no userdata was found, sync up!
                if data == 'Result: Empty':
                    self.set_ids()
                    return False
                
                tweet, message = data.split(';')
                first_tweet, last_tweet = tweet.split(',')
                first_message, last_message = message.split(',')
                
                # Set the IDs
                first_tweet = long(first_tweet)
                if first_tweet > self.settings['firsttweet_' + username]:
                    self.settings['firsttweet_' + username] = first_tweet
                
                last_tweet = long(last_tweet)
                if last_tweet > self.settings['lasttweet_' + username]:
                    self.settings['lasttweet_' + username] = last_tweet
                
                first_message = long(first_message)
                if first_message > self.settings['firstmessage_' + username]:
                    self.settings['firstmessage_' + username] = first_message
                
                last_message = long(last_message)
                if last_message > self.settings['lastmessage_' + username]:
                    self.settings['lastmessage_' + username] = last_message
                
                return True
            
            except IOError:
                if self.settings['syncing']:
                    self.main.on_sync_down_fail()
                
                log_error('Syncing down failed')
                return False
        
        else:
            return False
    
    def set_key(self):
        pass
    
    
    # Token requests -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def new_key(self):
        try:
            self.key = self.request('new', {'coding': 'kittens'})
            self.settings['synckey'] = self.key
            return True
        
        except IOError:
            log_error('Key request failed')
            return False
    
    def retrieve_new_key(self):
        try:
            key = self.request('new', {'coding': 'kittens'})
            return key
        
        except IOError:
            log_error('Key retrieve failed')
            return None
    
    def check_key(self, key):
        try:
            self.request('check', {'token': key})
            return True
        
        except IOError:
            return False
    
    
    # Check current token and retrieve a new one if needed ---------------------
    # --------------------------------------------------------------------------
    def get_key(self):
        key = self.settings['synckey']
        if key is None:
            pass
        
        elif key in ('', 'None'):
            key = None
        
        elif len(key) != 22:
            key = None
        
        else:
            for i in key:
                if not i in SYNC_KEY_CHARS:
                    key = None
                    break
        
        # new key
        if key is None:
            if self.settings['syncing'] is not True:
                return False
            
            return self.new_key()
        
        else:
            self.key = key
            return True
    
    
    # Make HTTP requests -------------------------------------------------------
    # --------------------------------------------------------------------------
    def request(self, method, data):
        tries = 1
        while True:
            conn = httplib.HTTPSConnection(SYNC_SERVER_HOST, SYNC_SERVER_PORT,
                                           timeout = 2)
            
            try:
                conn.request('POST',  '/' + method, urllib.urlencode(data))
                response = conn.getresponse()
                if response.status == 200:
                    break
                
                raise IOError
            
            except IOError:
                log_error('Syncing request #%d failed' % tries)
                tries += 1
                if tries > SYNC_MAX_TRIES:
                    raise IOError
        
        # Response check
        if response.status == 200:
            data = response.read()
            if data.startswith('Error: '):
                if data == 'Error: Invalid Token':
                    self.key = None
                    self.settings['synckey'] = None
                    self.settings['syncing'] = False
                    self.main.on_sync_key_fail()
                
                raise IOError
            
            else:
                return data
        
        else:
            raise IOError

