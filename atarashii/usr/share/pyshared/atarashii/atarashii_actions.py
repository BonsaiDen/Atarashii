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


# Atarashii / Actions ----------------------------------------------------------
# ------------------------------------------------------------------------------
import gtk
import gobject

import sys
import calendar
import time
import math

import send

from language import LANG as lang
from constants import ST_LOGIN_SUCCESSFUL, ST_WAS_RETWEET_NEW, \
                      ST_RECONNECT, ST_SEND, ST_DELETE, ST_WAS_SEND, \
                      ST_WAS_RETWEET, ST_WAS_DELETE, ST_NETWORK_FAILED

from constants import UNSET_ID_NUM, UNSET_TEXT


class AtarashiiActions:
    def __init__(self):
        pass
    
    # Start & Quit -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def start(self):
        gtk.quit_add(gtk.main_level(), self.save_on_quit)
        gtk.main()

    def quit(self):
        self.updater.running = False
        gtk.main_quit()
        
    def save_on_quit(self, *args):
        self.save_mode()
        self.save_settings()
        self.settings.crash_file(False)
        sys.exit(1)
    
    def save_settings(self):
        self.settings['position'] = str(self.gui.get_position())
        size = self.gui.get_allocation()
        self.settings['size'] = str((size[2], size[3]))
        self.settings['username'] = self.username
        self.settings.save()
    
    def save_mode(self):
        if self.username != UNSET_TEXT:
            self.settings['mode_' + self.username] = self.gui.mode
    
    
    # Sending ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def send(self, text):
        if self.status(ST_SEND) or self.status(ST_DELETE):
            return
        
        # Send
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.message_button.set_sensitive(False)
        self.gui.show_progress()
        if self.reply_user != UNSET_TEXT:
            self.gui.set_status(lang.status_reply % self.reply_user)
        
        elif self.retweet_user != UNSET_TEXT:
            self.gui.set_status(lang.status_retweet % self.retweet_user)
        
        elif self.message_text != UNSET_TEXT:
            self.gui.set_status(lang.status_message_reply % self.message_user)
        
        elif self.message_user != UNSET_TEXT:
            self.gui.set_status(lang.status_message % self.message_user)
        
        else:
            self.gui.set_status(lang.status_send)
        
        # Sender
        sender = send.Send(self, self.gui.mode, text)
        sender.setDaemon(True)
        sender.start()
    
    
    # New style Retweet
    def retweet(self, name, tweet_id, new_style = False):
        # Abort if pending
        if self.status(ST_SEND) or self.status(ST_DELETE):
            return
        
        if new_style:
            self.set_status(ST_WAS_RETWEET_NEW)
        
        # Setup
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.message_button.set_sensitive(False)
        self.gui.show_progress()
        self.gui.set_status(lang.status_retweet % name)
        
        # Retweeter
        retweeter = send.Retweet(self, name, tweet_id)
        retweeter.setDaemon(True)
        retweeter.start()
    
    
    # Delete
    def delete(self, tweet_id = UNSET_ID_NUM, message_id = UNSET_ID_NUM):
        # Abort if pending
        if self.status(ST_SEND) or self.status(ST_DELETE):
            return
        
        # Setup
        self.set_status(ST_DELETE)
        self.gui.text.set_sensitive(False)
        self.gui.message_button.set_sensitive(False)
        self.gui.show_progress()
        self.gui.set_status(lang.status_deleting_tweet if \
                            tweet_id != UNSET_ID_NUM else \
                            lang.status_deleting_message)
    
        # Deleter
        deleter = send.Delete(self, tweet_id, message_id)
        deleter.setDaemon(True)
        deleter.start()
    
    
    # Favorite
    def favorite(self, tweet_id, mode, name):
        if not self.favorites_pending.has_key(tweet_id):
            self.favorites_pending[tweet_id] = mode
            
            # Favoriter
            favoriter = send.Favorite(self, tweet_id, mode, name)
            favoriter.setDaemon(True)
            favoriter.start()     
    
    
    # Reconnect ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def reconnect(self):
        ratelimit = self.api.oauth_rate_limit_status()
        if ratelimit != None:
            minutes = math.ceil((ratelimit['reset_time_in_seconds'] - \
                                 calendar.timegm(time.gmtime())) / 60.0)
        
        else:
            minutes = 5
        
        self.refresh_timeout = int(minutes * 60 + 2)
        
        # Schedule a reconnect if the actual login failed
        if not self.status(ST_LOGIN_SUCCESSFUL):
            self.reconnect_time = calendar.timegm(time.gmtime())
            self.set_status(ST_RECONNECT)
            self.reconnect_timeout = gobject.timeout_add(
                                     int(self.refresh_timeout * 1000),
                                     self.login)
            
            return -7, lang.error_ratelimit_reconnect % math.ceil(minutes)
        
        # Just display an error if we exiced the ratelimit while being logged in
        else:
            return -6, lang.error_ratelimit % math.ceil(minutes)
    
    
    # Handle Errors and Warnings -----------------------------------------------
    # --------------------------------------------------------------------------
    def handle_error(self, error):
        if self.status(ST_WAS_SEND) or self.status(ST_WAS_DELETE):
            self.gui.show_input()
            
            if not self.status(ST_WAS_RETWEET) or \
               (self.retweet_text != UNSET_TEXT or \
               self.reply_user != UNSET_TEXT or \
               self.reply_id != UNSET_ID_NUM):
                
                if not self.status(ST_WAS_RETWEET_NEW):
                    self.gui.text.grab_focus()
            
            if self.gui.text.has_typed and \
               (self.status(ST_WAS_RETWEET_NEW) or \
               self.status(ST_WAS_DELETE)):
                self.gui.text.grab_focus()
        
        
        # Determine the kind of the error
        rate_error = ""  
        if isinstance(error, IOError):
            if hasattr(error, "read"):
                msg = error.read()
            
            else:
                msg = ""
        else:
            msg = error.reason
            error.code = error.response.status
            error.errno = None
        
        # Catch errors due to missing network
        if error.errno == -2:
            self.set_status(ST_NETWORK_FAILED)
            code = -4
            if self.status(ST_LOGIN_SUCCESSFUL):
                code = -5
                self.set_status(ST_NETWORK_FAILED)
                self.gui.refresh_button.set_sensitive(False)
        
        # Catch common Twitter errors
        elif error.code in (400, 401, 403, 404, 500, 502, 503):
            if msg.startswith("Share sharing"):
                code = -2
            
            else:
                code = error.code
                
                # Ratelimit errors
                if (code == 400 and not self.status(ST_WAS_SEND)) or \
                   (code == 403 and self.status(ST_WAS_SEND)):
                    
                    self.gui.refresh_button.set_sensitive(False)
                    self.gui.tray.refresh_menu.set_sensitive(False)
                    code, rate_error = self.reconnect()
                
                # Just normal 400's and 403'
                elif (code == 400 and self.status(ST_WAS_SEND)) or \
                     (code == 403 and not self.status(ST_WAS_SEND)):
                    
                    code = 500
                
                # A real 404! This may be raised if a user wasn't found
                elif self.status(ST_WAS_SEND) and code == 404:
                    code = -3 
                    
        # Catch network errors
        else:
            code = -1
        
        # Reset stuff
        self.unset_status(ST_WAS_SEND | ST_WAS_RETWEET | \
                               ST_WAS_RETWEET_NEW | ST_WAS_DELETE)
        
        # Leave it to GUI!
        self.gui.show_error(code, error, rate_error)

