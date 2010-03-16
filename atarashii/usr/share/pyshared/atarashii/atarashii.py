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

# TODO enable deletion
# TODO add favorite
# TODO add timeout to requests!!!!!
# TODO fix link dragging


# Atarashii --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import bus

import pygtk
pygtk.require('2.0')
import gtk
import gobject

import os
import calendar
import time
import math
import sys

gtk.gdk.threads_init()
gtk.gdk.threads_enter()

import notify
import send
import gui
import settings
import updater

from lang import lang
from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_TIMEOUT, RETWEET_ASK, \
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
        self.login_error = False
        self.login_status = False
        self.network_failed = False
        self.is_sending = False
        self.is_connecting = False
        self.is_reconnecting = False
        self.is_updating = False
        self.is_loading_history = False
        self.was_sending = False
        self.was_retweeting = False
        self.was_new_retweeting = False
        self.rate_warning_shown = False
        self.request_warning_shown = False
        
        # Current Username
        self.username = self.settings['username'] or UNSET_TEXT
        
        # Retweet Style
        self.retweet_style = self.settings['retweet'] or RETWEET_ASK
        
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
        if self.is_sending:
            return
        
        # Send
        self.is_sending = True
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
        if not self.is_sending:
            if new_style:
                self.was_new_retweeting = True
            
            self.is_sending = True
            self.gui.text.set_sensitive(False)
            self.gui.message_button.set_sensitive(False)
            self.gui.show_progress()
            self.gui.set_status(lang.status_retweet % name)
            
            # Sender
            sender = send.Retweet(self, name, tweet_id)
            sender.setDaemon(True)
            sender.start()
    
    
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
        while self.is_updating:
            time.sleep(0.1)
        
        # Switch User
        if change_user != None:
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
        
        self.login_status = False
        self.is_sending = False
        self.is_connecting = True
        self.is_reconnecting = False
        self.reconnect_timeout = None
        self.is_updating = False
        self.login_error = False
        
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
        self.login_error = False
        self.login_status = True
        self.is_connecting = False
        self.network_failed = False
        self.gui.settings_button.set_sensitive(True)
        self.gui.tray.settings_menu.set_sensitive(True)
        self.gui.set_title(lang.title_logged_in % self.username)
        self.gui.update_status()
        self.gui.show_input()
    
    def on_login_failed(self, error = None):
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.login_error = True if error != None else False
        self.login_status = False
        self.is_connecting = False
        self.network_failed = False
        self.gui.settings_button.set_sensitive(True)
        self.gui.tray.settings_menu.set_sensitive(True)
        self.gui.set_app_title()
        self.gui.hide_all()
        self.gui.update_status()
        if error:
            self.gui.show_error(error)
        
        gobject.idle_add(lambda: self.gui.message.init(True))
        gobject.idle_add(lambda: self.gui.html.init(True))
    
    def on_network_failed(self, error):
        self.on_login_failed(error)
    
    def logout(self):
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.login_error = False
        self.login_status = False
        self.is_sending = False
        self.is_connecting = False
        self.is_reconnecting = False
        self.is_updating = False
        self.network_failed = False
        self.gui.settings_button.set_sensitive(True)
        self.gui.update_status()
        self.gui.set_app_title()
        self.gui.hide_all()
        
        gobject.idle_add(lambda: self.gui.message.init(True))
        gobject.idle_add(lambda: self.gui.html.init(True))
    
    
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
        if not self.login_status:
            self.reconnect_time = calendar.timegm(time.gmtime())
            self.is_reconnecting = True
            self.reconnect_timeout = gobject.timeout_add(
                                     int(self.refresh_timeout * 1000),
                                     lambda: self.login())
            
            return lang.error_ratelimit_reconnect % math.ceil(minutes)
        
        # Just display an error if we exiced the ratelim while being logged in
        else:
            return lang.error_ratelimit % math.ceil(minutes)
    
    
    # Helper Functions ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_user_picture(self, img):
        self.settings['picture_' + self.username] = img
    
    def get_user_picture(self):
        img = self.settings['picture_' + self.username]
        if not self.login_status and not self.is_connecting:
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
    
    
    # Start & Quit -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def start(self):
        gtk.main()
    
    def save_settings(self):
        self.settings['position'] = str(self.gui.get_position())
        size = self.gui.get_allocation()
        self.settings['size'] = str((size[2], size[3]))
        self.settings['username'] = self.username
        self.settings.save()
    
    def save_mode(self):
        if self.username != UNSET_TEXT:
            self.settings['mode_' + self.username] = self.gui.mode
    
    def quit(self):
        self.updater.running = False
        self.save_mode()
        self.save_settings()
        gtk.main_quit()
        sys.exit(1)

