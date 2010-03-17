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


# GUI --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import calendar
import time
import math

import html
import message
import tray
import text
import dialog

from language import LANG as lang
from constants import ST_CONNECT, ST_LOGIN_ERROR, ST_LOGIN_SUCCESSFUL, \
                      ST_DELETE, ST_UPDATE, ST_SEND, ST_RECONNECT, ST_HISTORY

from constants import MODE_MESSAGES, MODE_TWEETS, UNSET_ID_NUM, HTML_LOADING, \
                      MESSAGE_WARNING, MESSAGE_QUESTION, MESSAGE_INFO, \
                      UNSET_TIMEOUT, HTML_UNSET_ID


from gui_events import GUIEventHandler
from gui_helpers import GUIHelpers


class GUI(gtk.Window, GUIEventHandler, GUIHelpers):
    def __init__(self, main):
        # Setup
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.main = main
        self.hide_on_delete()
        self.set_border_width(2)
        self.set_size_request(280, 400)
        self.set_icon_from_file(main.get_image())
        
        # Hide in Taskbar?
        self.show_in_taskbar(main.settings.is_true('taskbar'))
        
        # Load Components
        self.gtb = gtb = gtk.Builder()
        gtb.add_from_file(main.get_resource("main.glade"))
        frame = gtb.get_object("frame")
        self.add(frame)
        gtb.get_object("content").set_border_width(2)
        
        # Link Components
        self.refresh_button = gtb.get_object("refresh")
        self.refresh_button.connect("clicked", self.on_refresh)
        self.refresh_button.set_tooltip_text(lang.tool_refresh)
        
        self.history_button = gtb.get_object("history")
        self.history_button.connect("clicked", self.on_history)
        self.history_button.set_tooltip_text(lang.tool_history)
        
        self.read_button = gtb.get_object("read")
        self.read_button.connect("clicked", self.on_read)
        self.read_button.set_tooltip_text(lang.tool_read)
        
        self.message_button = gtb.get_object("message")
        self.message_button.connect("clicked", self.on_mode)
        self.message_button.set_tooltip_text(lang.tool_mode)
        
        # Settings Button
        self.settings_button = gtb.get_object("settings")
        self.settings_button.connect("toggled",
                                     lambda *args: self.on_settings(False))
        
        self.settings_button.set_tooltip_text(lang.tool_settings)
        self.settings_toggle = False
        
        # About Button
        self.about_button = gtb.get_object("about")
        self.about_button.connect("toggled",
                                  lambda *args: self.on_about(False))
        
        self.about_button.set_tooltip_text(lang.tool_about)
        self.about_toggle = False
        
        self.quit_button = gtb.get_object("quit")
        self.quit_button.connect("clicked", self.on_quit)
        self.quit_button.set_tooltip_text(lang.tool_quit)
        
        # Info Label
        self.info_label = gtb.get_object("label")
        
        # Text Input
        self.text_scroll = gtb.get_object("textscroll")
        self.text = text.TextInput(self)
        self.text_scroll.add(self.text)
        
        # HTML
        self.html_scroll = gtb.get_object("htmlscroll")
        self.html = html.HTML(self.main, self)
        self.html_scroll.add(self.html)
        self.html_scroll.set_shadow_type(gtk.SHADOW_IN)
        self.html.splash()
        
        # Messages
        self.message_scroll = gtb.get_object("messagescroll")
        self.message = message.HTML(self.main, self)
        self.message_scroll.add(self.message)
        self.message_scroll.set_shadow_type(gtk.SHADOW_IN)
        self.message.splash()
        
        # Bars
        self.toolbar = gtb.get_object("toolbar")
        self.progress = gtb.get_object("progressbar")
        self.status = gtb.get_object("statusbar")
        
        # Warning Button
        self.warning_button = dialog.ButtonDialog(self, "warning",
                                     lang.warning_template, lang.warning_title)
        
        # Error Button
        self.error_button = dialog.ButtonDialog(self, "error",
                                     lang.error_template, lang.error_title)
        
        # Restore Position & Size
        if main.settings.isset("position"):
            self.window_position = main.settings['position'][1:-1].split(",")
            self.move(int(self.window_position[0]),
                      int(self.window_position[1]))
        
        if main.settings.isset("size"):
            size = main.settings['size'][1:-1].split(",")
            self.resize(int(size[0]), int(size[1]))
        
        else:
            self.resize(280, 400)
        
        # Tray
        self.tray = tray.TrayIcon(self)
        
        # Events
        self.connect("delete_event", self.delete_event)
        self.connect("destroy", self.destroy_event)
        self.connect("window-state-event", self.state_event)
        
        # Dialogs
        self.about_dialog = None
        self.settings_dialog = None
        
        # Variables
        self.mode = MODE_TWEETS
        self.window_position = None
        self.minimized = False
        self.is_shown = False
        self.progress_visible = False
        
        # Set Message/Tweet Mode
        self.set_mode(self.mode)
        self.set_app_title()
        self.on_mode()
        
        # Show GUI
        if not main.settings.is_true("tray", False) or \
            main.settings.is_true("crashed", False): # show after crash
            self.show_gui()
        
        gobject.idle_add(self.main.on_init)
    
    
    # Initial Show -------------------------------------------------------------
    def show_gui(self):
        self.show_all()
        
        # Hide Warning/Error Buttons
        self.warning_button.hide()
        self.error_button.hide()
        self.on_mode()
        
        # Statusbar Updater
        self.update_status()
        gobject.timeout_add(1000, self.update_status)
        
        # Crash Info
        if self.main.settings.is_true("crashed", False):
            gobject.timeout_add(250, self.show_crash_report)
        
        # Show
        if not self.main.status(ST_CONNECT):
            self.show_input()
        
        else:
            self.show_progress()
        
        #gobject.timeout_add(250, lambda: self.error_button.show("foo", "bla"))
        #gobject.timeout_add(250,lambda: self.warning_button.show("foo", "bla"))
        self.is_shown = True
    
    def force_show(self):
        if not self.is_shown:
            self.show_gui()
    
    
    # GUI Switchers ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_input(self, resize = True):
        self.progress.hide()
        self.progress_visible = False
        self.text_scroll.show()
        if resize:
            self.text.resize()
        
        else:
            self.text.resize(1)
        
        self.text.set_sensitive(True)
        self.check_refresh()
        self.check_read()
        self.message_button.set_sensitive(self.main.status(ST_LOGIN_SUCCESSFUL))
    
    def show_progress(self):
        def progress_activity():
            self.progress.pulse()
            return self.main.status(ST_SEND) or \
                self.main.status(ST_DELETE) or \
                self.main.status(ST_CONNECT) or \
                self.main.status(ST_HISTORY) or \
                (self.mode == MODE_MESSAGES and \
                self.message.load_state == HTML_LOADING) or \
                (self.mode == MODE_TWEETS and \
                self.html.load_state == HTML_LOADING)
        
        self.progress.set_fraction(0.0)
        self.progress.show()
        self.info_label.hide()
        self.text_scroll.hide()
        if not self.progress_visible:
            gobject.timeout_add(100, progress_activity)
        
        self.progress_visible = True
    
    def hide_all(self, progress = True):
        if progress:
            self.progress.hide()
            self.progress_visible = False
        
        self.text_scroll.hide()
        self.refresh_button.set_sensitive(False)
        self.tray.refresh_menu.set_sensitive(False)
        self.read_button.set_sensitive(False)
        self.tray.read_menu.set_sensitive(False)
        self.history_button.set_sensitive(False)
        self.message_button.set_sensitive(False)
        
        self.warning_button.hide()
        self.error_button.hide()
    
    
    # Statusbar ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def update_status(self, once = False):
        if self.text.has_typed:
            pass
        
        elif self.main.status(ST_RECONNECT):
            wait = self.main.refresh_timeout - \
                    (calendar.timegm(time.gmtime()) - self.main.reconnect_time)
            if wait < 60:
                self.set_status(lang.status_reconnect_seconds % wait)
            
            elif wait < 105:
                self.set_status(lang.status_reconnect_minute)
            
            else:
                self.set_status(
                    lang.status_reconnect_minutes % math.ceil(wait / 60.0))
        
        elif self.main.status(ST_HISTORY):
            self.set_status(
                lang.status_load_history if \
                self.html.load_history_id != HTML_UNSET_ID else \
                lang.status_load_message_history)
        
        elif self.main.status(ST_CONNECT):
            self.set_status(lang.status_connecting % self.main.username)
        
        elif self.main.status(ST_LOGIN_ERROR):
            self.set_status(lang.status_error)
        
        elif not self.main.status(ST_LOGIN_SUCCESSFUL):
            self.set_status(lang.status_logout)
        
        elif self.main.status(ST_SEND) or self.main.status(ST_DELETE):
            pass
        
        elif self.main.status(ST_UPDATE):
            self.refresh_button.set_sensitive(False)
            self.tray.refresh_menu.set_sensitive(False)
            self.set_status(lang.status_update)
        
        elif self.main.refresh_time == UNSET_TIMEOUT or \
            (self.mode == MODE_MESSAGES and \
            self.message.load_state == HTML_LOADING) or \
            (self.mode == MODE_TWEETS and \
            self.html.load_state == HTML_LOADING):
            
            self.set_status(lang.status_connected)
        
        elif (not self.text.is_typing or not self.text.has_focus) and not \
            self.main.status(ST_SEND):
            
            wait = self.main.refresh_timeout - \
                (calendar.timegm(time.gmtime()) - self.main.refresh_time)
            
            if wait == 0:
                self.refresh_button.set_sensitive(False)
                self.tray.refresh_menu.set_sensitive(False)
                self.set_status(lang.status_update)
            
            elif wait == 1:
                self.set_status(lang.status_one_second)
            
            else:
                if wait < 60:
                    self.set_status(lang.status_seconds % wait)
                
                elif wait < 105:
                    self.set_status(lang.status_minute)
                
                else:
                    self.set_status(
                         lang.status_minutes % math.ceil(wait / 60.0))
        
        if once:
            return False
        
        else:
            return True
    
    def set_status(self, status):
        self.status.pop(0)
        self.status.push(0, status)
    
    
    # Message Dialogs ----------------------------------------------------------
    # --------------------------------------------------------------------------
    def enter_password(self):
        self.main.api_temp_password = None
        dialog.PasswordDialog(self, lang.password_title,
                              lang.password_question % \
                              lang.name(self.main.username))
    
    def show_retweet_info(self, name):
        dialog.MessageDialog(self, MESSAGE_INFO,
                        lang.retweet_info % name,
                        lang.retweet_info_title)
    
    def ask_for_delete_tweet(self, info_text, yes, noo):
        dialog.MessageDialog(self, MESSAGE_QUESTION,
                        lang.delete_tweet_question % info_text,
                        lang.delete_title,
                        yes_callback = yes, no_callback = noo)
    
    def ask_for_delete_message(self, info_text, yes, noo):
        dialog.MessageDialog(self, MESSAGE_QUESTION,
                        lang.delete_message_question % info_text,
                        lang.delete_title,
                        yes_callback = yes, no_callback = noo)
    
    def show_delete_info(self, tweet, msg):
        dialog.MessageDialog(self, MESSAGE_INFO,
                        lang.delete_info_tweet if tweet != UNSET_ID_NUM else \
                        lang.delete_info_message,
                        lang.delete_info_title)
    
    def show_favorite_error(self, name, mode):
        dialog.MessageDialog(self, MESSAGE_WARNING, 
               lang.error_favorite_on % lang.name(name) if mode else \
               lang.error_favorite_off % lang.name(name), lang.error_title)
    
    def show_crash_report(self):
        dialog.MessageDialog(self, MESSAGE_WARNING, 
               "Atarashii has crashed and automatically restarted itself.",
               lang.error_title)    

