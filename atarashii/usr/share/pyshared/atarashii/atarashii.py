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

# TODO add multireply via shift/ctrl, replyid is from the first selected tweet
# TODO make longer replies easier, either split them and add @user to each of 
#      them, or use ctrl+enter to send and start a new reply to the same tweet
# TODO fixup tooltips not getting removed when switching workspaces
# TODO fix tooltip flickering during updating. Maybe an issues with the loading
#      state???
# TODO add block/unfollow to avatar menus


# Make sure there is only one instance of Atarashii ----------------------------
import bus
DBUS_INSTANCE = bus.get_instance()


# Atarashii --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gobject

import time
import os
import sys

gobject.threads_init()

import notify
import gui
import settings
import updater

from language import LANG as lang
from utils import SHORTS_LIST
from atarashii_actions import AtarashiiActions

from constants import ST_CONNECT, ST_LOGIN_ERROR, ST_LOGIN_SUCCESSFUL, \
                      ST_UPDATE,ST_LOGIN_COMPLETE, ST_RECONNECT, ST_ALL, \
                      ST_NONE, ST_SEND, ST_DELETE, ST_LOGIN_COMPLETE

from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_TIMEOUT, \
                      MODE_TWEETS, MODE_MESSAGES


class Atarashii(AtarashiiActions):
    def __init__(self, version, secret, kittens,
                 debug=False, debug_path=None):
        
        # Setup
        self.version = version
        self.secret = secret
        self.kittens = kittens
        self.debug = debug
        self.debug_path = debug_path
        self.exited = False
        self.start_time = time.time()
        
        # Catch python errors
        sys.exitfunc = self.crash_exit
        
        # Load Settings
        self.settings = settings.Settings()
        
        # API
        self.api = None
        self.api_temp_password = None
        
        # Variables
        self.unset('reply', 'retweet', 'message', 'edit')
        self.delete_tweet_id = UNSET_ID_NUM
        self.delete_message_id = UNSET_ID_NUM
        
        # The number of items that should be loaded on each history call
        self.load_tweet_count = 20
        
        # The maximum number of items that should be displayed at one time
        self.max_tweet_count = 200
        
        # The maximum number of items that should be displayed at one time
        # even if the initial load returns more than the above limit!
        # Essentially this is the hard limit for tweets that are beeing loaded
        # on startup
        self.max_tweet_init_count = 400
        
        # Look above
        self.load_message_count = 20
        self.max_message_count = 200
        self.max_message_init_count = 400
        
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
        
        # GUI
        self.gui = gui.GUI(self)
        
        # Check Shortener
        if not self.settings['shortener'] in SHORTS_LIST:
            self.settings['shortener'] = SHORTS_LIST[0]
        
        # Start
        self.updater.start()
    
    
    # Login & Logout -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_init(self):
        self.login()
    
    def login(self, change_user=None):
        # We need a username!
        if self.username == UNSET_TEXT \
           and (change_user is None or change_user == UNSET_TEXT):
            self.gui.set_app_title()
            return
        
        # Disable the account menu
        self.gui.tray.activate_menu(False)
        
        # Wait until the last update/delete/send/login is complete
        if self.any_status(ST_UPDATE, ST_DELETE, ST_SEND, ST_CONNECT) \
           or (not self.status(ST_LOGIN_COMPLETE) and change_user != None and self.username != ''):
            print "blaaa", self.status(ST_CONNECT), self.status(ST_UPDATE)
            gobject.timeout_add(50, self.login, change_user)
            return None
        
        # Switch User
        if change_user is not None:
            self.gui.text.reset()
            self.username = change_user
            self.settings['username'] = change_user
        
        # Set Mode
        self.gui.set_mode(self.settings['mode_' + self.username])
        
        # Progress
        self.gui.hide_all(False)
        self.gui.show_progress()
        
        # Connect
        if self.reconnect_timeout is not None:
            gobject.source_remove(self.reconnect_timeout)
        
        # Status
        self.unset_status(ST_LOGIN_SUCCESSFUL | ST_LOGIN_COMPLETE | ST_SEND | \
                          ST_RECONNECT | ST_UPDATE | ST_LOGIN_ERROR \
                          | ST_LOGIN_COMPLETE | ST_LOGIN_ERROR)
        
        self.set_status(ST_CONNECT)
        self.reconnect_timeout = None
        
        # Reset
        self.gui.update_status()
        self.gui.html.init(load = True)
        if self.gui.mode == MODE_MESSAGES:
            self.gui.html.start()
        
        self.gui.message.init(load = True)
        if self.gui.mode == MODE_TWEETS:
            self.gui.message.start()
        
        self.gui.text.reset()
        self.gui.set_app_title()
        self.updater.unwait(init = True)
    
    def on_login(self):
        self.unset_status(ST_LOGIN_ERROR | ST_CONNECT | ST_DELETE)
        self.set_status(ST_LOGIN_SUCCESSFUL)
        self.gui.tray.activate_menu(True)
        self.gui.set_title(lang.title_logged_in % self.username)
        self.gui.update_status()
        self.gui.show_input()
    
    def on_login_failed(self, error=None):
        self.username = ''
        self.settings['username'] = ''
        self.gui.tray.update_account_menu()
        
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.unset_status(ST_ALL)
        if error is not None:
            self.set_status(ST_LOGIN_ERROR)
                
        self.gui.tray.activate_menu(True)
        self.gui.set_multi_button(False, None, False)
        self.gui.set_app_title()
        self.gui.hide_all()
        self.gui.update_status()
        if error:
            self.handle_error(error)
        
        gobject.idle_add(self.gui.message.init, True)
        gobject.idle_add(self.gui.html.init, True)
    
    def on_network_failed(self, error):
        self.on_login_failed(error)
    
    def logout(self):
        self.refresh_time = UNSET_TIMEOUT
        self.refresh_timeout = UNSET_TIMEOUT
        self.gui.set_mode(MODE_TWEETS)
        self.unset_status(ST_ALL)
        self.gui.update_status()
        self.gui.hide_all()
        
        self.gui.tray.activate_menu(True)
        gobject.idle_add(self.gui.message.init, True)
        gobject.idle_add(self.gui.html.init, True)
        gobject.idle_add(self.gui.set_app_title)
    
    
    # Helper Functions ---------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_start_notifications(self):
        if not self.settings.is_true('notify') \
           and self.status(ST_LOGIN_SUCCESSFUL):
            return False
        
        info_text = []
        
        # Tweet Info
        if self.gui.html.count > 0:
            info_text.append(
              (lang.notification_login_tweets if self.gui.html.count > 1 \
               else lang.notification_login_tweet) % self.gui.html.count)
        
        # Message Info
        if self.gui.message.count > 0:
            info_text.append(
              (lang.notification_login_messages if self.gui.message.count > 1 \
               else lang.notification_login_message) % self.gui.message.count)
        
        # Create notification
        info = (lang.notification_login % self.username,
                '\n'.join(info_text), self.get_user_picture(),
                'theme:service-login')
        
        self.notifier.add(info)
    
    def set_user_picture(self, img):
        self.settings['picture_' + self.username] = img
    
    def get_user_picture(self):
        img = self.settings['picture_' + self.username]
        if not self.any_status(ST_LOGIN_SUCCESSFUL, ST_CONNECT):
            img = None
        
        if img is None or not os.path.exists(img):
            return self.get_image()
        
        else:
            return img
    
    def get_image(self):
        icon = '/usr/share/icons/atarashii.png'
        if self.debug_path is None:
            return icon
        
        else:
            return os.path.join(self.debug_path, 'atarashii'+ icon)
    
    def get_resource(self, res):
        if self.debug_path is None:
            return os.path.join('/usr/share/atarashii', res)
        
        else:
            return os.path.join(self.debug_path,
                                'atarashii/usr/share/atarashii', res)
    
    # Statuses
    def status(self, flag):
        return self.current_status & flag == flag
    
    def any_status(self, *flags):
        return len([i for i in flags if self.status(i)]) > 0
    
    def all_status(self, *flags):
        return len([i for i in flags if self.status(i)]) == len(flags)
    
    def set_status(self, flag):
        self.current_status |= flag
    
    def unset_status(self, flag):
        self.current_status &= ~flag
    
    # Attributes
    def unset(self, *args):
        for key in args:
            if key == 'reply':
                self.reply_text = UNSET_TEXT
                self.reply_user = UNSET_TEXT
                self.reply_id = UNSET_ID_NUM
            
            elif key == 'retweet':
                self.retweet_text = UNSET_TEXT
                self.retweet_user = UNSET_TEXT
            
            elif key == 'edit':
                self.edit_id = UNSET_ID_NUM
                self.edit_text = UNSET_TEXT
                self.edit_reply_id = UNSET_ID_NUM
                self.edit_reply_user = UNSET_TEXT
            
            elif key == 'message':
                self.message_user = UNSET_TEXT
                self.message_id = UNSET_ID_NUM
                self.message_text = UNSET_TEXT

