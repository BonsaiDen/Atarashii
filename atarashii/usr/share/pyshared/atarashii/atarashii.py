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


# DBUS Integration -------------------------------------------------------------
# ------------------------------------------------------------------------------
import dbus
import dbus.service
import sys
import os
if 'org.Atarashii' in dbus.Interface(dbus.SessionBus().get_object(
   'org.freedesktop.DBus', '/org/freedesktop/DBus'),
   'org.freedesktop.DBus').ListNames():
    sys.exit(69) # os.EX_UNAVAILABLE

DBUS = dbus.SessionBus()
DBUSNAME = dbus.service.BusName('org.Atarashii', bus = DBUS)


# Atarashii --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import time

gtk.gdk.threads_init()
gtk.gdk.threads_enter()

import notify
import gui
import settings
import updater

from language import LANG as lang
from utils import SHORTS_LIST
from atarashii_actions import AtarashiiActions

from constants import ST_CONNECT, ST_LOGIN_ERROR, ST_LOGIN_SUCCESSFUL, \
                      ST_UPDATE,ST_LOGIN_COMPLETE, ST_RECONNECT, ST_ALL, \
                      ST_NONE, ST_SEND, ST_DELETE

from constants import UNSET_ID_NUM, UNSET_TEXT, UNSET_TIMEOUT, \
                      MODE_TWEETS, MODE_MESSAGES


class Atarashii(AtarashiiActions):
    def __init__(self, version, secret, kittens,
                 debug = False, debug_path = None):
        
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
        self.notifier.setDaemon(True)
        self.notifier.start()
        
        # Updater
        self.updater = updater.Updater(self)
        self.updater.setDaemon(True)
        
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
    
    def login(self, change_user = None):
        # We need a username!
        if self.username == UNSET_TEXT \
           and (change_user == None or change_user == UNSET_TEXT):
            self.gui.set_app_title()
            return
            
        # Wait until the last update/delete/send is complete
        # FIXME does this thing every gets into action?
        while self.any_status(ST_UPDATE, ST_DELETE, ST_SEND, ST_CONNECT):
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
        
        self.gui.tray.settings_menu.set_sensitive(False)
        self.gui.message.init(True)
        if self.gui.mode == MODE_TWEETS:
            self.gui.message.start()
        
        self.gui.text.reset()
        self.gui.set_app_title()
        self.updater.do_init = True
    
    def on_login(self):
        self.unset_status(ST_LOGIN_ERROR | ST_CONNECT | ST_DELETE)
        self.set_status(ST_LOGIN_SUCCESSFUL)
        
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
        
        if self.gui.settings_dialog != None:
            self.gui.settings_dialog.activate(True)
        
        self.gui.tray.settings_menu.set_sensitive(True)
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
        self.gui.set_app_title()
        self.gui.hide_all()
        
        if self.gui.settings_dialog != None:
            self.gui.settings_dialog.activate(True)
        
        gobject.idle_add(self.gui.message.init, True)
        gobject.idle_add(self.gui.html.init, True)
    
    
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
                '\n'.join(info_text), self.get_user_picture())
        
        self.notifier.items.append(info)
    
    def set_user_picture(self, img):
        self.settings['picture_' + self.username] = img
    
    def get_user_picture(self):
        img = self.settings['picture_' + self.username]
        if not self.any_status(ST_LOGIN_SUCCESSFUL, ST_CONNECT):
            img = None
        
        if img == None or not os.path.exists(img):
            return self.get_image()
        
        else:
            return img
    
    def get_image(self):
        icon = '/usr/share/icons/atarashii.png'
        if self.debug_path == None:
            return icon
        
        else:
            return os.path.join(self.debug_path, 'atarashii'+ icon)
    
    def get_resource(self, res):
        if self.debug_path == None:
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
