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

# TODO add real errors to the tray icon tooltip


# DBUS Integration -------------------------------------------------------------
# ------------------------------------------------------------------------------
import dbus
import dbus.service
import sys
if 'org.Atarashii' in dbus.Interface(dbus.SessionBus().get_object(
   "org.freedesktop.DBus", "/org/freedesktop/DBus"), 
   "org.freedesktop.DBus").ListNames():
    sys.exit(2)

DBUS = dbus.SessionBus()
DBUSNAME = dbus.service.BusName('org.Atarashii', bus = DBUS)


# Atarashii --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import os
import calendar
import time
import math

gtk.gdk.threads_init()
gtk.gdk.threads_enter()

import notify
import send
import gui
import settings
import updater
import dialog

from language import LANG as lang
from constants import ST_CONNECT, ST_LOGIN_ERROR, \
                      ST_LOGIN_SUCCESSFUL, ST_UPDATE, ST_WAS_RETWEET_NEW, \
                      ST_LOGIN_COMPLETE, ST_RECONNECT, ST_ALL, ST_NONE, \
                      ST_SEND, ST_DELETE

from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_TIMEOUT, \
                      MODE_TWEETS, MODE_MESSAGES, HTML_UNSET_ID


class Atarashii:
    def __init__(self, version, debug = None):
        # Setup
        self.version = version
        self.debug = debug
        
        # Load Settings
        self.settings = settings.Settings()
        
        # API
        self.api = None
        self.api_temp_password = None
        
        # Variables
        self.reply_user = UNSET_ID_NUM
        self.reply_text = UNSET_TEXT
        self.reply_id = UNSET_ID_NUM
        
        self.retweet_user = UNSET_TEXT
        self.retweet_text = UNSET_TEXT
        
        self.message_user = UNSET_TEXT
        self.message_id = UNSET_ID_NUM
        self.message_text = UNSET_TEXT
        
        self.load_tweet_count = 20
        self.max_tweet_count = 200
        self.load_message_count = 20
        self.max_message_count = 200
        
        
        # Timer
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.reconnect_time = UNSET_TIMEOUT
        self.reconnect_timeout = None # The reconnect timer reference
        
        # State
        self.current_status = 0
        self.set_status(ST_NONE)
        self.favorites_pending = {}
        
        # Current Username
        self.username = self.settings['username'] or UNSET_TEXT
                
        # Notifier
        self.notifier = notify.Notifier(self)
        
        # Updater
        self.updater = updater.Updater(self)
        self.updater.setDaemon(True)
        
        # GUI
        self.gui = gui.GUI(self)
        
        # Start
        self.updater.start()
    
    
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
    
    
    # Login & Logout -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_init(self):
        self.login()
    
    def login(self, change_user = None):
        # We need a username!
        if self.username == UNSET_TEXT and (change_user == None or \
           change_user == UNSET_TEXT):
            self.gui.set_app_title()
            return
            
        # Wait until the last update is complete
        while self.status(ST_UPDATE):
            time.sleep(0.1)
        
        # Switch User
        if change_user != None:
            self.gui.text.reset()
            self.username = change_user
            self.settings['username'] = change_user
        
        # Set Mode
        self.gui.set_mode(self.settings['mode_' + self.username])
        
        # Progress
        self.gui.hide_all(False)
        self.gui.show_progress()
        
        # Connect
        if self.reconnect_timeout != None:
            gobject.source_remove(self.reconnect_timeout)
        
        # Status
        self.unset_status(ST_LOGIN_SUCCESSFUL | ST_LOGIN_COMPLETE | ST_SEND | \
                          ST_RECONNECT | ST_UPDATE | ST_LOGIN_ERROR)
        
        self.set_status(ST_CONNECT)
        self.reconnect_timeout = None
        
        # Reset
        self.gui.update_status()
        self.gui.html.init(True)
        if self.gui.mode == MODE_MESSAGES:
            self.gui.html.start()
        
        self.gui.settings_button.set_sensitive(False)
        self.gui.tray.settings_menu.set_sensitive(False)
        self.gui.message.init(True)
        if self.gui.mode == MODE_TWEETS:
            self.gui.message.start()
        
        self.gui.set_app_title()
        self.updater.do_init = True
    
    def on_login(self):
        self.unset_status(ST_LOGIN_COMPLETE | ST_LOGIN_ERROR | ST_CONNECT | \
                          ST_DELETE)
        
        self.set_status(ST_LOGIN_SUCCESSFUL)
        self.gui.settings_button.set_sensitive(True)
        self.gui.tray.settings_menu.set_sensitive(True)
        self.gui.set_title(lang.title_logged_in % self.username)
        self.gui.update_status()
        self.gui.show_input()
    
    def on_login_failed(self, error = None):
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.unset_status(ST_ALL)
        if error != None:
            self.set_status(ST_LOGIN_ERROR)
        
        self.gui.settings_button.set_sensitive(True)
        self.gui.tray.settings_menu.set_sensitive(True)
        self.gui.set_app_title()
        self.gui.hide_all()
        self.gui.update_status()
        if error:
            self.gui.handle_error(error)
        
        gobject.idle_add(self.gui.message.init, True)
        gobject.idle_add(self.gui.html.init, True)
    
    def on_network_failed(self, error):
        self.on_login_failed(error)
    
    def logout(self):
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.unset_status(ST_ALL)
        self.gui.settings_button.set_sensitive(True)
        self.gui.update_status()
        self.gui.set_app_title()
        self.gui.hide_all()
        
        gobject.idle_add(self.gui.message.init, True)
        gobject.idle_add(self.gui.html.init, True)
    
    
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
            msg = error.read()
            
        else:
            msg = error.reason
            error.code = error.response.status
            error.errno = None
        
        # Catch common Twitter errors
        if error.code in (400, 401, 403, 404, 500, 502, 503):
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
        elif error.errno == -2:
            code = -4
            if self.status(ST_LOGIN_SUCCESSFUL):
                code = -5
        
        else:
            code = -1
        
        # Reset stuff
        self.unset_status(ST_WAS_SEND | ST_WAS_RETWEET | \
                               ST_WAS_RETWEET_NEW | ST_WAS_DELETE)
        
        
        # Show Warning Button --------------------------------------------------
        if code in (-5, 503):
            if code == -5: # Network lost
                info = lang.warning_network
                button = lang.warning_button_network
                
            else: # overload warning
                info = lang.warning_overload
                button = lang.warning_button_overload
            
            self.gui.warning_button.show(button, info)
        
        # Show Error Button
        elif code in (500, 502, -6):
            if code != -6:
                if code == 500: # internal twitter error
                    button = lang.error_button_twitter
                    info = lang.error_twitter
                
                else: # Twitter down
                    button = lang.error_button_down
                    info = lang.error_down
            
            # Rate limit exceeded
            else:
                info = rate_error
                button = lang.error_button_rate_limit
                
            self.gui.error_button.show(button, info)
        
        # Show Error Dialog ----------------------------------------------------
        else:
            # Show GUI if minimized to tray
            gobject.idle_add(self.gui.force_show)
            
            description = {
                -4 : lang.error_network,
                -3 : lang.error_user_not_found % self.message_user,
                -2 : lang.error_already_retweeted,
                0 : lang.error_internal % str(error),
                -7 : rate_error,
                401 : lang.error_login % self.username,
                404 : lang.error_login % self.username
            }[code]
            dialog.MessageDialog(self, MESSAGE_ERROR, description,
                                 lang.error_title)
        
        self.gui.update_status()
    
    
    # Helper Functions ---------------------------------------------------------
    # -------------------------------------------------------------------------- 
    def show_start_notifications(self):
        if not self.settings.is_true("notify") and \
           self.status(ST_LOGIN_SUCCESSFUL):
            return False
        
        info_text = []
        
        # Tweet Info
        if self.gui.html.count > 0:
            info_text.append(
              (lang.notification_login_tweets if self.gui.html.count > 1 else \
               lang.notification_login_tweet) % self.gui.html.count)  
        
        # Message Info
        if self.gui.message.count > 0:
            info_text.append(
              (lang.notification_login_messages if self.gui.message.count > 1 \
               else lang.notification_login_message) % self.gui.message.count)  
        
        # Create notification
        info = [(lang.notification_login % self.username,
                "\n".join(info_text), self.get_user_picture())]
        
        self.notifier.show(info)
    
    def set_user_picture(self, img):
        self.settings['picture_' + self.username] = img
    
    def get_user_picture(self):
        img = self.settings['picture_' + self.username]
        if not self.status(ST_LOGIN_SUCCESSFUL) and not self.status(ST_CONNECT):
            img = None
        
        if img == None or not os.path.exists(img):
            return self.get_image()
        
        else:
            return img
    
    def get_image(self):
        if self.debug == None:
            return '/usr/share/icons/atarashii.png'
        
        else:
            return os.path.join(self.debug,
                                'atarashii/usr/share/icons/atarashii.png')
    
    def get_resource(self, res):
        if self.debug == None:
            return os.path.join("/usr/share/atarashii", res)
        
        else:
            return os.path.join(self.debug,
                                "atarashii/usr/share/atarashii", res)
    
    def get_latest_id(self):
        if self.settings.isset('lasttweet_' + self.username):
            return long(self.settings['lasttweet_' + self.username])
        
        else:
            return HTML_UNSET_ID
    
    def get_first_id(self):
        if self.settings.isset('firsttweet_' + self.username):
            return long(self.settings['firsttweet_' + self.username])
        
        else:
            return HTML_UNSET_ID
    
    def get_latest_message_id(self):
        if self.settings.isset('lastmessage_' + self.username):
            return long(self.settings['lastmessage_' + self.username])
        
        else:
            return HTML_UNSET_ID
    
    def get_first_message_id(self):
        if self.settings.isset('firstmessage_' + self.username):
            return long(self.settings['firstmessage_' + self.username])
        
        else:
            return HTML_UNSET_ID
    
    def set_tweet_count(self, count):
        self.max_tweet_count = count
    
    def get_tweet_count(self):
        return self.max_tweet_count
    
    def set_message_count(self, count):
        self.max_message_count = count
    
    def get_message_count(self):
        return self.max_message_count
    
    def status(self, flag):
        return self.current_status & flag == flag
    
    def set_status(self, flag):
        self.current_status |= flag
    
    def unset_status(self, flag):
        self.current_status &= ~flag
    
    
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

