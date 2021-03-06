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
import time
import math
import socket
from urllib2 import URLError, HTTPError

import api

from errors import log_error
from utils import gmtime
from lang import LANG as lang

from constants import LOGOUT_FILE
from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_ERROR, UNSET_USERNAME, \
                      HTML_LOADING, MODE_PROFILE, HTML_LOADED, MODE_PROFILE

from constants import ST_LOGIN_SUCCESSFUL, ST_WAS_RETWEET_NEW, \
                      ST_RECONNECT, ST_SEND, ST_DELETE, ST_WAS_SEND, \
                      ST_WAS_RETWEET, ST_WAS_DELETE, \
                      ST_CONNECT, ST_LOGIN_COMPLETE

from constants import ERR_TWEET_NOT_FOUND, ERR_MESSAGE_NOT_FOUND, \
                      ERR_ALREADY_RETWEETED, ERR_TWEET_DUPLICATED, \
                      ERR_USER_NOT_FOUND, ERR_RATE_RECONNECT, \
                      ERR_RATE_LIMIT, ERR_NETWORK_FAILED, \
                      ERR_NETWORK_TWITTER_FAILED, ERR_URLLIB_FAILED, \
                      ERR_URLLIB_TIMEOUT, ERR_USER_NOT_FOLLOW, ERR_MAPPING

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
    
    # Add / Delete indicator file
    def on_logout(self, *args):
        self.save_settings(True, True, True)
        i = open(LOGOUT_FILE, 'wb')
        i.close()
    
    def on_logout_cancel(self, *args):
        if os.path.exists(LOGOUT_FILE):
            os.unlink(LOGOUT_FILE)
    
    def quit(self):
        self.save_settings(True, True, True)
        self.updater.running = False
        self.dbus.main = None
        self.gui.hide()
        self.gui.tray.set_property('visible', False)
        if self.gui.settings_dialog is not None:
            self.gui.settings_dialog.hideall()
        
        if self.gui.about_dialog is not None:
            self.gui.about_dialog.on_close()
        
        gobject.idle_add(self.real_quit)
    
    def real_quit(self):
        gtk.main_quit()
        self.notifier.close()
        self.settings.check_cache()
        sys.last_traceback = None
        
        # Wait for sync up to finish
        while self.syncer.pending:
            time.sleep(0.01)
        
        sys.exit(0) # os.EX_OK
    
    def save_settings(self, mode=False, tweets=False, messages=False):
        if mode:
            self.save_mode()
        
        if self.username != UNSET_USERNAME:
            if tweets:
                self.gui.tweet.save_first()
                self.gui.tweet.save_last_id()
            
            if messages:
                self.gui.message.save_first()
                self.gui.message.save_last_id()
            
            if tweets or messages:
                self.syncer.set_ids()
        
        self.settings['position'] = str(self.gui.get_normalized_position())
        size = self.gui.get_allocation()
        self.settings['size'] = str((size[2], size[3]))
        self.settings['username'] = self.username
        self.settings.save()
    
    def save_mode(self):
        if self.username != UNSET_TEXT and self.gui.mode != MODE_PROFILE:
            self.settings['mode_' + self.username] = self.gui.mode
    
    
    # API ----------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def send(self, text, multi=False):
        if self.any_status(ST_SEND, ST_DELETE):
            return False
        
        # Send
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.tabs.set_sensitive(False)
        self.gui.show_progress()
        
        # Statusbar
        edit = False
        if self.edit_text != UNSET_TEXT:
            if self.edit_reply_user != UNSET_USERNAME:
                self.gui.set_status(lang.status_edit_reply \
                                    % self.edit_reply_user)
            
            else:
                self.gui.set_status(lang.status_edit)
            
            edit = True
        
        elif self.reply_user != UNSET_USERNAME:
            self.gui.set_status(lang.status_reply % self.reply_user)
        
        elif self.retweet_user != UNSET_USERNAME:
            self.gui.set_status(lang.status_retweet % self.retweet_user)
        
        elif self.message_text != UNSET_TEXT:
            self.gui.set_status(lang.status_message_reply % self.message_user)
        
        elif self.message_user != UNSET_USERNAME:
            self.gui.set_status(lang.status_message % self.message_user)
        
        else:
            self.gui.set_status(lang.status_send)
        
        if edit:
            api.Edit(self, text)
        
        else:
            api.Send(self, text, multi)
    
    # New style Retweet
    def retweet(self, name, tweet_id, new_style=False):
        # Abort if pending
        if self.any_status(ST_SEND, ST_DELETE):
            return False
        
        if new_style:
            self.set_status(ST_WAS_RETWEET_NEW)
        
        # Setup
        self.set_status(ST_SEND)
        self.gui.text.set_sensitive(False)
        self.gui.tabs.set_sensitive(False)
        self.gui.show_progress()
        self.gui.set_status(lang.status_retweet % name)
        
        api.Retweet(self, name, tweet_id)
    
    # Delete
    def delete(self, tweet_id=UNSET_ID_NUM, message_id=UNSET_ID_NUM):
        # Abort if pending
        if self.any_status(ST_SEND, ST_DELETE):
            return False
        
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
        
        api.Delete(self, tweet_id, message_id)
    
    # Favorite
    def favorite(self, tweet_id, mode, name):
        if not tweet_id in self.favorites_pending:
            self.favorites_pending[tweet_id] = mode
            api.Favorite(self, tweet_id, mode, name)
    
    def set_favorite(self, tweet_id, mode):
        gobject.idle_add(self.gui.tweet.favorite, tweet_id, mode)
        if self.gui.mode == MODE_PROFILE:
            gobject.idle_add(self.gui.profile.favorite, tweet_id, mode)
    
    # Follow / Unfollow
    def follow(self, menu, user_id, name, mode):
        self.follow_pending[name.lower()] = True
        api.Follow(self, user_id, name, mode)
    
    def followed(self, mode, name):
        if self.profile_current_user != UNSET_USERNAME:
            self.gui.profile.update_follow(mode)
        
        self.gui.show_follow_info(mode, name)
    
    def follow_error(self, mode, name):
        if self.profile_current_user != UNSET_USERNAME:
            self.gui.profile.enable_button()
        
        self.gui.show_follow_error(mode, name)
    
    # Block / Unblock
    def block(self, menu, user_id, name, mode, spam=None):
        if mode and spam is None:
            
            def block_spam():
                self.block(menu, user_id, name, mode, True)
            
            def simple_block():
                self.block(menu, user_id, name, mode, False)
            
            self.gui.ask_for_block_spam(name, block_spam, simple_block)
            return False
        
        self.block_pending[name.lower()] = True
        api.Block(self, user_id, name, mode, spam)
    
    def blocked(self, mode, name, spam):
        if self.profile_current_user != UNSET_USERNAME:
            self.gui.profile.update_block(mode)
        
        self.gui.show_block_info(mode, name, spam)
    
    def block_error(self, mode, name):
        if self.profile_current_user != UNSET_USERNAME:
            self.gui.profile.enable_button()
        
        self.gui.show_block_error(mode, name)
    
    # Show profile
    def profile(self, name, retry=False):
        if self.profile_current_user.lower() == name.lower() and not retry:
            return False
        
        # Button
        if not retry:
            self.profile_pending = True
            name = self.settings.get_username(name)
            self.profile_current_user = name
            self.gui.load_button.show(lang.profile_loading % lang.name(name),
                                      None)
        
        # Make sure to stop when aborted
        if not self.profile_pending:
            return False
        
        # Wait until send/delete etc. is completed
        if self.any_status(ST_DELETE, ST_SEND, ST_CONNECT) \
           or not self.status(ST_LOGIN_COMPLETE) \
           or name.lower() in self.follow_pending \
           or name.lower() in self.block_pending:
            
            gobject.timeout_add(50, self.profile, name, True)
            return False
        
        # View
        if self.gui.mode != MODE_PROFILE:
            self.profile_mode = self.gui.mode
        
        self.gui.profile.load_state = HTML_LOADING
        self.gui.profile.start()
        self.gui.text.remove_auto_complete(True)
        gobject.idle_add(self.gui.set_mode, MODE_PROFILE)
        gobject.idle_add(self.gui.on_mode)
        api.Profile(self, name, self.show_profile)
    
    def show_profile(self, user, friend, tweets):
        if not self.profile_pending:
            return False
        
        self.gui.load_button.show(lang.profile_close % \
                                  lang.name(user.screen_name), None)
        
        self.profile_current_user = user.screen_name
        self.gui.profile.load_state = HTML_LOADED
        self.gui.profile.history_level = 0
        self.gui.profile.render(user, friend, tweets)
        gobject.idle_add(self.gui.show_input)
    
    def stop_profile(self, blank=False, name=UNSET_USERNAME, not_found=False):
        if name == UNSET_USERNAME or name == self.profile_current_user:
            if name == self.profile_current_user and name != UNSET_USERNAME:
                if not_found:
                    gobject.idle_add(self.gui.show_profile_error, name)
                
                else:
                    gobject.idle_add(self.gui.show_profile_warning, name)
            
            self.profile_pending = False
            self.profile_current_user = UNSET_USERNAME
            self.gui.load_button.hide()
            
            if blank is not True:
                if self.gui.mode == MODE_PROFILE:
                    self.gui.mode = self.profile_mode
                    self.gui.on_mode(no_check = True, from_profile = True)
                
                self.gui.profile.load_state = HTML_LOADING
                self.gui.profile.start()
    
    def update_user_list(self):
        if not self.settings.userlist_uptodate(self.username):
            api.Friends(self, self.username, self.settings.add_users)
    
    def update_user_stats(self):
        api.User(self, self.username, self.settings.update_user_stats_user)
    
    
    # Reconnect ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def reconnect(self):
        ratelimit = self.api.rate_limit_status()
        if ratelimit is not None:
            minutes = math.ceil((ratelimit['reset_time_in_seconds'] \
                                 - gmtime()) / 60.0) + 2
        
        else:
            minutes = 5
        
        self.refresh_timeout = int(minutes * 60)
        
        # Schedule a reconnect if the actual login failed
        if not self.status(ST_LOGIN_SUCCESSFUL):
            self.reconnect_time = gmtime()
            self.set_status(ST_RECONNECT)
            self.reconnect_timeout = gobject.timeout_add(
                                     int(self.refresh_timeout * 1000),
                                     self.login,
                                     self.last_username)
            
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
        
        # HTTP Errors
        elif isinstance(error, HTTPError):
            msg = UNSET_ERROR
            error_code = error.code
            error_errno = None
        
        # GAI errors
        elif isinstance(error, socket.gaierror) or isinstance(error, URLError):
            msg = UNSET_ERROR
            if hasattr(error, 'errno'):
                error_errno = error.errno
            
            else:
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
            error_code = error.code if hasattr(error, 'code') else 0
        
        # Tweepy errors
        else:
            msg = error.reason
            error_code = error.response.status
            error_errno = None
        
        # Catch errors due to missing network
        if error_errno in (ERR_URLLIB_FAILED, ERR_URLLIB_TIMEOUT):
            code = ERR_NETWORK_FAILED
            if self.status(ST_LOGIN_SUCCESSFUL) \
               or error_errno == ERR_URLLIB_TIMEOUT:
                
                code = ERR_NETWORK_TWITTER_FAILED
                self.gui.set_multi_button(True)
                self.gui.tray.refresh_menu.set_sensitive(False)
                
                # Refresh Views
                gobject.idle_add(self.gui.tweet.render)
                gobject.idle_add(self.gui.message.render)
        
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
            
            elif msg.lower().startswith('you cannot send messages'):
                code = ERR_USER_NOT_FOLLOW
            
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
        
        else:
            log_error('Unkown error code %s' % error_code)
            code = ERR_NETWORK_FAILED
        
        # Reset stuff
        self.unset_status(ST_WAS_SEND | ST_WAS_RETWEET | \
                          ST_WAS_RETWEET_NEW | ST_WAS_DELETE)
        
        # Leave it to the GUI!
        self.gui.show_error(code, rate_error)
        
        # Log the error
        if error_errno is None:
            error_errno = 0
        
        log_error('%s %d' % (ERR_MAPPING[code], error_errno))

