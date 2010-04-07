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
import pygtk
pygtk.require('2.0')
import gtk
import gobject
import gnome.ui

import os
import sys
import calendar
import time
import math
import socket
from urllib2 import URLError

import send

from language import LANG as lang
from settings import LOGOUT_FILE

from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_ERROR
from constants import ST_LOGIN_SUCCESSFUL, ST_WAS_RETWEET_NEW, \
                      ST_RECONNECT, ST_SEND, ST_DELETE, ST_WAS_SEND, \
                      ST_WAS_RETWEET, ST_WAS_DELETE, ST_LOGIN_SUCCESSFUL

from constants import ERR_TWEET_NOT_FOUND, ERR_MESSAGE_NOT_FOUND, \
                      ERR_ALREADY_RETWEETED, ERR_TWEET_DUPLICATED, \
                      ERR_USER_NOT_FOUND, ERR_RATE_RECONNECT, \
                      ERR_RATE_LIMIT, ERR_NETWORK_FAILED, \
                      ERR_NETWORK_TWITTER_FAILED, ERR_URLLIB_FAILED, \
                      ERR_URLLIB_TIMEOUT

from constants import HT_400_BAD_REQUEST, HT_401_UNAUTHORIZED, \
                      HT_403_FORBIDDEN, HT_404_NOT_FOUND, \
                      HT_500_INTERNAL_SERVER_ERROR, HT_502_BAD_GATEWAY, \
                      HT_503_SERVICE_UNAVAILABLE


class AtarashiiActions(object):
    def start(self):
        # Remove old logout indicator
        self.on_logout_cancel()
        
        # Connect to gnome session in order to be notified on shutdown
        gnome.program_init('Atarashii', self.version)
        client = gnome.ui.master_client()
        client.connect('save-yourself', self.on_logout)
        client.connect('shutdown-cancelled', self.on_logout_cancel)
        client.connect('die', self.on_logout)
        
        # Start GTK
        gtk.main()
    
    def crash_exit(self):
        # Catch Python Errors
        if not self.exited:
            # Set date format to english
            import locale
            locale.setlocale(locale.LC_TIME, 'C')
                        
            # Save the crashlog
            import traceback
            from settings import CRASH_LOG_FILE
            crash_file = open(CRASH_LOG_FILE, 'ab')
            trace = traceback.extract_tb(sys.last_traceback)
            crash_file.write(
                 '''Atarashii %s\nStarted at %s\nCrashed at %s\nTraceback:\n'''
                 % (self.version,
                 time.strftime('%a %b %d %H:%M:%S +0000 %Y',
                                time.gmtime(time.time())),
                 
                 time.strftime('%a %b %d %H:%M:%S +0000 %Y', time.gmtime())
                 ))
        
            crash_file.write('\n'.join(traceback.format_list(trace)))
            crash_file.close()
            
            # Exit with specific error
            sys.exit(70) # os.EX_SOFTWARE
    
    # Add / Delete indicator file
    def on_logout(self, *args):
        self.save_settings(True)
        i = open(LOGOUT_FILE, 'wb')
        i.close()
    
    def on_logout_cancel(self, *args):
        if os.path.exists(LOGOUT_FILE):
            os.unlink(LOGOUT_FILE)
    
    def quit(self):
        self.save_settings(True)
        self.updater.running = False
        gtk.main_quit()
        self.notifier.close()
        self.settings.check_cache()
        self.exited = True
        sys.exit(0) # os.EX_OK
    
    def save_settings(self, mode=False):
        if mode:
            self.save_mode()
        
        self.gui.html.save_first()
        self.gui.message.save_first()
        self.gui.html.save_last_id()
        self.gui.message.save_last_id()
        
        self.settings['position'] = str(self.gui.get_normalized_position())
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
        if self.any_status(ST_SEND, ST_DELETE):
            return
        
        # Send
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.tabs.set_sensitive(False)
        self.gui.show_progress()
        
        # Statusbar
        edit = False
        if self.edit_text != UNSET_TEXT:
            if self.edit_reply_user != UNSET_TEXT:
                self.gui.set_status(lang.status_edit_reply \
                                    % self.edit_reply_user)
            
            else:
                self.gui.set_status(lang.status_edit)
        
            edit = True
        
        elif self.reply_user != UNSET_TEXT:
            self.gui.set_status(lang.status_reply % self.reply_user)
        
        elif self.retweet_user != UNSET_TEXT:
            self.gui.set_status(lang.status_retweet % self.retweet_user)
        
        elif self.message_text != UNSET_TEXT:
            self.gui.set_status(lang.status_message_reply % self.message_user)
        
        elif self.message_user != UNSET_TEXT:
            self.gui.set_status(lang.status_message % self.message_user)
        
        else:
            self.gui.set_status(lang.status_send)
        
        # Editer
        if edit:
            editer = send.Edit(self, self.edit_id, text, self.edit_reply_id)
            editer.setDaemon(True)
            editer.start()
        
        # Sender
        else:
            sender = send.Send(self, self.gui.mode, text)
            sender.setDaemon(True)
            sender.start()
    
    
    # New style Retweet
    def retweet(self, name, tweet_id, new_style=False):
        # Abort if pending
        if self.any_status(ST_SEND, ST_DELETE):
            return
        
        if new_style:
            self.set_status(ST_WAS_RETWEET_NEW)
        
        # Setup
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.tabs.set_sensitive(False)
        self.gui.show_progress()
        self.gui.set_status(lang.status_retweet % name)
        
        # Retweeter
        retweeter = send.Retweet(self, name, tweet_id)
        retweeter.setDaemon(True)
        retweeter.start()
    
    
    # Delete
    def delete(self, tweet_id=UNSET_ID_NUM, message_id=UNSET_ID_NUM):
        # Abort if pending
        if self.any_status(ST_SEND, ST_DELETE):
            return
        
        # Setup
        self.delete_tweet_id = tweet_id
        self.delete_message_id = message_id
        self.set_status(ST_DELETE)
        self.gui.text.set_sensitive(False)
        self.gui.tabs.set_sensitive(False)
        self.gui.show_progress()
        self.gui.set_status(lang.status_deleting_tweet \
                            if tweet_id != UNSET_ID_NUM \
                            else lang.status_deleting_message)
    
        # Deleter
        deleter = send.Delete(self, tweet_id, message_id)
        deleter.setDaemon(True)
        deleter.start()
    
    
    # Favorite
    def favorite(self, tweet_id, mode, name):
        if not tweet_id in self.favorites_pending:
            self.favorites_pending[tweet_id] = mode
            
            # Favoriter
            favoriter = send.Favorite(self, tweet_id, mode, name)
            favoriter.setDaemon(True)
            favoriter.start()
    
    
    # Reconnect ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def reconnect(self):
        ratelimit = self.api.rate_limit_status()
        if ratelimit is not None:
            minutes = math.ceil((ratelimit['reset_time_in_seconds'] \
                                 - calendar.timegm(time.gmtime())) / 60.0)
        
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
            
            return ERR_RATE_RECONNECT, lang.error_ratelimit_reconnect \
                                         % math.ceil(minutes)
        
        # Just display an error if we exiced the ratelimit while being logged in
        else:
            return ERR_RATE_LIMIT, lang.error_ratelimit % math.ceil(minutes)
    
    
    # Handle Errors and Warnings -----------------------------------------------
    # --------------------------------------------------------------------------
    def handle_error(self, error):
        # Do we need to give focus back to the textbox?
        self.gui.text.check_refocus()
        
        # Determine the kind of the error
        rate_error = UNSET_ERROR
        
        # Timeout errors
        if isinstance(error, socket.timeout):
            msg = UNSET_ERROR
            error_code = 0
            error_errno = ERR_URLLIB_TIMEOUT
        
        # GAI errors
        elif isinstance(error, socket.gaierror) or isinstance(error, URLError):
            msg = UNSET_ERROR
            error_errno = ERR_URLLIB_FAILED
            error_code = 0
        
        # IO errors
        elif isinstance(error, IOError):
            if hasattr(error, 'read'):
                msg = error.read()
            
            elif hasattr(error, 'msg'):
                msg = error.msg
            
            else:
                msg = UNSET_ERROR
            
            error_errno = error.errno
            error_code = error.code
        
        # Tweepy errors
        else:
            msg = error.reason
            error_code = error.response.status
            error_errno = None
        
        
        # Catch errors due to missing network
        if error_errno in (ERR_URLLIB_FAILED, ERR_URLLIB_TIMEOUT):
            code = ERR_NETWORK_FAILED
            if self.status(ST_LOGIN_SUCCESSFUL) or ERR_URLLIB_FAILED:
                code = ERR_NETWORK_TWITTER_FAILED
                self.gui.set_multi_button(True)
                self.gui.tray.refresh_menu.set_sensitive(False)
        
        # Catch common Twitter errors
        elif error_code in (HT_400_BAD_REQUEST, HT_401_UNAUTHORIZED,
                            HT_403_FORBIDDEN, HT_404_NOT_FOUND,
                            HT_500_INTERNAL_SERVER_ERROR, HT_502_BAD_GATEWAY,
                            HT_503_SERVICE_UNAVAILABLE):
            
            if msg.lower().startswith('no status'):
                code = ERR_TWEET_NOT_FOUND
        
            elif msg.lower().startswith('no direct message'):
                code = ERR_MESSAGE_NOT_FOUND
        
            elif msg.lower().startswith('share sharing'):
                code = ERR_ALREADY_RETWEETED
            
            elif msg.lower().startswith('status is a duplicate'):
                code = ERR_TWEET_DUPLICATED
                
            else:
                code = error_code
                
                # Ratelimit errors
                if code == HT_400_BAD_REQUEST and not self.status(ST_WAS_SEND) \
                   or code == HT_403_FORBIDDEN and self.status(ST_WAS_SEND):
                    
                    self.gui.set_multi_button(False)
                    self.gui.tray.refresh_menu.set_sensitive(False)
                    code, rate_error = self.reconnect()
                
                # Just normal HT_400_BAD_REQUEST's and HT_403_FORBIDDEN'
                elif code == HT_400_BAD_REQUEST and self.status(ST_WAS_SEND) \
                     or code == HT_403_FORBIDDEN \
                     and not self.status(ST_WAS_SEND):
                    
                    code = HT_500_INTERNAL_SERVER_ERROR
                
                # A real 404. This may be raised if a user wasn't found
                elif self.status(ST_WAS_SEND) and code == HT_404_NOT_FOUND:
                    code = ERR_USER_NOT_FOUND
        
        # Reset stuff
        self.unset_status(ST_WAS_SEND | ST_WAS_RETWEET | \
                          ST_WAS_RETWEET_NEW | ST_WAS_DELETE)
        
        # Leave it to the GUI!
        self.gui.show_error(code, error_code, error_errno, rate_error)

