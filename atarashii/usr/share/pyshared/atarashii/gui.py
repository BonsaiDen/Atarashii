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
from utils import escape

from language import LANG as lang
from constants import ST_CONNECT, \
                      ST_LOGIN_ERROR, ST_LOGIN_SUCCESSFUL, ST_DELETE, \
                      ST_UPDATE, ST_WAS_RETWEET, ST_WAS_RETWEET_NEW, ST_SEND, \
                      ST_LOGIN_COMPLETE, ST_WAS_SEND, ST_RECONNECT, \
                      ST_HISTORY, ST_WAS_DELETE

from constants import MODE_MESSAGES, MODE_TWEETS, UNSET_TEXT, UNSET_ID_NUM, \
                      HTML_LOADING, HTML_LOADED, MESSAGE_WARNING, \
                      MESSAGE_ERROR, MESSAGE_QUESTION, MESSAGE_INFO, \
                      UNSET_LABEL, UNSET_TIMEOUT, HTML_UNSET_ID


class GUI(gtk.Window):
    def __init__(self, main):
        # Setup
        self.main = main
        gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)
        self.hide_on_delete()
        self.set_border_width(2)
        self.set_size_request(280, 400)
        self.set_icon_from_file(main.get_image())
        
        # Hide in Taskbar?
        self.show_taskbar(main.settings.is_true('taskbar'))
        
        # Load Components
        gtb = gtk.Builder()
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
        self.warning_box = gtb.get_object("warning")
        self.warning_button = gtb.get_object("warning_button")
        self.warning_label = gtb.get_object("warning_label")
        self.warning_button.connect("clicked", self.show_warning_dialog)
        self.warning_dialog = None
        self.warning_shown = False
        self.warning_information = UNSET_TEXT
        
        # Error Button
        self.error_box = gtb.get_object("error")
        self.error_button = gtb.get_object("error_button")
        self.error_label = gtb.get_object("error_label")
        self.error_button.connect("clicked", self.show_error_dialog)
        self.error_dialog = None
        self.error_shown = False
        self.error_information = UNSET_TEXT
                
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
        
        # Enable Mode
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
        self.hide_warning_button()
        self.hide_error_button() 
        
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
        
        self.is_shown = True
    
    def force_show(self):
        if not self.is_shown:
            self.show_gui()
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def delete_event(self, widget, event, data=None):
        self.window_position = self.get_position()
        self.main.settings['position'] = str(self.window_position)
        self.hide()
        return True
    
    def destroy_event(self, widget, data=None):
        self.window_position = self.get_position()
        self.main.settings['position'] = str(self.window_position)
        self.hide()
        return True
    
    def state_event(self, window, event):
        if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.minimized = event.new_window_state & \
                                gtk.gdk.WINDOW_STATE_ICONIFIED
    
    
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
        self.hide_warning_button()
        self.hide_error_button()
    
    
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
    
    
    # Info Label ---------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_label(self):    
        if self.main.status(ST_SEND):
            return
        
        if self.main.reply_user == UNSET_TEXT and \
            self.main.retweet_user == UNSET_TEXT and \
            self.main.message_user == UNSET_TEXT:
            
            self.info_label.set_markup(UNSET_LABEL)
            self.info_label.hide()
        
        elif self.main.retweet_user != UNSET_TEXT:
            self.set_label_text(lang.label_retweet, self.main.retweet_user)
            self.info_label.show()
        
        elif self.main.reply_text != UNSET_TEXT:
            self.set_label_text(lang.label_reply_text, self.main.reply_text)
            self.info_label.show()
        
        elif self.main.reply_user != UNSET_TEXT:
            self.set_label_text(lang.label_reply, self.main.reply_user)
            self.info_label.show()
        
        # Messages
        elif self.main.message_text != UNSET_TEXT:
            self.set_label_text(lang.label_message_text, self.main.message_text)
            self.info_label.show()
        
        elif self.main.message_user != UNSET_TEXT:
            self.set_label_text(lang.label_message, self.main.message_user)
            self.info_label.show()
    
    def set_label_text(self, info, label_text):
        self.info_label.set_markup(info % escape(label_text))
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_height(self, widget):
        size = widget.get_allocation()
        return size[3] - size[0]
    
    def set_app_title(self):
        if self.main.username == UNSET_TEXT or \
            (not self.main.status(ST_LOGIN_SUCCESSFUL) and \
            not self.main.status(ST_CONNECT)):
            self.set_title(lang.title)
        
        elif self.mode == MODE_MESSAGES:
            if self.html.count > 0:
                self.set_title(
                     (lang.title_tweets if self.html.count > 1 else \
                      lang.title_tweet) % self.html.count)
            
            else:
                self.set_title(lang.title_logged_in % self.main.username)
        
        elif self.mode == MODE_TWEETS:
            if self.message.count > 0:
                self.set_title(
                     (lang.title_messages if self.html.count > 1 else \
                      lang.title_message) % self.message.count)
            
            else:
                self.set_title(lang.title_logged_in % self.main.username)
        
        # Tray Tooltip
        if not self.main.status(ST_CONNECT) and \
           self.main.status(ST_LOGIN_COMPLETE):
           
            if self.main.username == UNSET_TEXT or \
                (not self.main.status(ST_LOGIN_SUCCESSFUL) and \
                not self.main.status(ST_CONNECT)):
                
                self.tray.set_tooltip(lang.tray_logged_out)
            
            elif self.mode == MODE_MESSAGES:
                self.tray.set_tooltip(lang.tray_logged_in % self.main.username,
                                      self.html.count, self.message.count)
            
            elif self.mode == MODE_TWEETS:                
                self.tray.set_tooltip(lang.tray_logged_in % self.main.username,
                                      self.html.count, self.message.count)
        
        elif self.main.status(ST_CONNECT):
            self.tray.set_tooltip(lang.tray_logging_in % self.main.username)
        
        else:
            self.tray.set_tooltip(lang.tray_logged_out)
    
    
    def check_refresh(self):
        if self.is_ready():
            self.refresh_button.set_sensitive(True)
            self.tray.refresh_menu.set_sensitive(True)
            
            # Check for message/tweet switch
            if self.text.go_send_message != None:
                self.set_mode(MODE_MESSAGES)
            
            elif self.text.go_send_tweet != None:
                self.set_mode(MODE_TWEETS)
            
            self.update_status()
    
    def check_read(self):
        if self.mode == MODE_MESSAGES:
            mode = self.message.last_id > self.message.init_id            
            
        elif self.mode == MODE_TWEETS:
            mode = self.html.last_id > self.html.init_id
        
        else:
            mode = False
        
        self.read_button.set_sensitive(mode)
        self.tray.read_menu.set_sensitive(mode)
    
    
    def set_mode(self, mode):
        if mode == self.mode:
            return
        
        if mode == None:
            self.mode = MODE_TWEETS
        
        else:
            self.mode = mode
        
        if self.mode == MODE_MESSAGES:
            self.message_button.set_active(True)
        
        elif self.mode == MODE_TWEETS:
            self.message_button.set_active(False)
    
    def is_ready(self):
        return not self.main.status(ST_UPDATE) and self.load_state()
    
    def load_state(self):
        return self.message.load_state == HTML_LOADED and \
               self.html.load_state == HTML_LOADED
    
    def show_taskbar(self, mode):
        self.main.settings['taskbar'] = mode
        self.set_property('skip-taskbar-hint', not mode)
    
    def show_start_notifications(self):
        if self.main.settings.is_true("notify") and \
           self.main.status(ST_LOGIN_SUCCESSFUL):
            info_text = []
            
            # Tweet Info
            if self.html.count > 0:
                info_text.append(
                  (lang.notification_login_tweets if self.html.count > 1 else \
                   lang.notification_login_tweet) % self.html.count)  
            
            # Message Info
            if self.message.count > 0:
                info_text.append(
                  (lang.notification_login_messages if self.message.count > 1 \
                   else lang.notification_login_message) % self.message.count)  
            
            # Create notification
            info = [(lang.notification_login % self.main.username,
                    "\n".join(info_text), self.main.get_user_picture())]
            
            self.main.notifier.show(info)
    
    
    # Handlers -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_refresh(self, *args):
        self.refresh_button.set_sensitive(False)
        if self.mode == MODE_MESSAGES:
            self.main.updater.refresh_messages = True
        
        else:
            self.main.updater.refresh_now = True
    
    def on_history(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(self.message.clear)
        
        else:
            gobject.idle_add(self.html.clear)
    
    def on_read(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(self.message.read)
        
        else:
            gobject.idle_add(self.html.read)
    
    def on_read_all(self, *args):
        gobject.idle_add(self.message.read)
        gobject.idle_add(self.html.read)
    
    def on_mode(self, *args):
        if self.message_button.get_active():
            self.mode = MODE_MESSAGES
        
        else: # TODO add case for searchbutton
            self.mode = MODE_TWEETS
        
        if self.mode == MODE_MESSAGES:
            self.history_button.set_tooltip_text(lang.tool_history_message)
            self.read_button.set_tooltip_text(lang.tool_read_message)
            self.refresh_button.set_tooltip_text(lang.tool_refresh_message)
            self.html_scroll.hide()
            self.message_scroll.show()
            self.message.focus_me()
            self.message.fix_scroll()
            
            self.check_read()
            self.history_button.set_sensitive(self.message.history_loaded)
            
            if self.message.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.message.load_state == HTML_LOADED:
                self.show_input()
        
        elif self.mode == MODE_TWEETS:
            self.history_button.set_tooltip_text(lang.tool_history)
            self.read_button.set_tooltip_text(lang.tool_read)
            self.refresh_button.set_tooltip_text(lang.tool_refresh)
            self.message_scroll.hide()
            self.html_scroll.show()
            self.html.focus_me()
            self.html.fix_scroll()
            
            self.check_read()
            self.history_button.set_sensitive(self.html.history_loaded)
            
            if self.html.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.html.load_state == HTML_LOADED:
                self.show_input()
        
        else: # TODO implement search here
            pass
        
        self.set_app_title()
        self.text.check_mode()
        self.text.loose_focus()
    
    def on_settings(self, menu):
        if not self.settings_toggle:
            self.settings_toggle = True
            if self.settings_button.get_active() and not self.settings_dialog:
                self.settings_dialog = dialog.SettingsDialog(self)
            
            elif menu and not self.settings_dialog:
                self.settings_dialog = dialog.SettingsDialog(self)
                self.settings_button.set_active(True)
            
            
            elif menu and self.settings_dialog:
                self.settings_dialog.on_close()
                self.settings_button.set_active(False)
            
            elif self.settings_dialog:
                self.settings_dialog.on_close()
            
            self.settings_toggle = False
    
    def on_about(self, menu):
        if not self.about_toggle:
            self.about_toggle = True
            if self.about_button.get_active() and not self.about_dialog:
                self.about_dialog = dialog.AboutDialog(self)
            
            elif menu and not self.about_dialog:
                self.about_dialog = dialog.AboutDialog(self)
                self.about_button.set_active(True)
            
            elif menu and self.about_dialog:
                self.about_dialog.on_close()
                self.about_button.set_active(False)
            
            elif self.about_dialog:
                self.about_dialog.on_close()
            
            self.about_toggle = False
    
    def on_quit(self, widget = None, data = None):
        if data:
            data.set_visible(False)
        
        self.main.quit()
    
    
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
    
    
    # Error & Warning aka I'm Error! -------------------------------------------
    # --------------------------------------------------------------------------
    def show_error(self, error):
        # Select Textbox?
        if self.main.status(ST_WAS_SEND) or self.main.status(ST_WAS_DELETE):
            self.show_input()
            
            if not self.main.status(ST_WAS_RETWEET) or \
               (self.main.retweet_text != UNSET_TEXT or \
               self.main.reply_user != UNSET_TEXT or \
               self.main.reply_id != UNSET_ID_NUM):
                
                if not self.main.status(ST_WAS_RETWEET_NEW):
                    self.text.grab_focus()
                    
            if self.text.has_typed and \
               (self.main.status(ST_WAS_RETWEET_NEW) or \
               self.main.status(ST_WAS_DELETE)):
                self.text.grab_focus()
        
        
        # Determine the kind of ther error
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
                if (code == 400 and not self.main.status(ST_WAS_SEND)) or \
                   (code == 403 and self.main.status(ST_WAS_SEND)):
                    
                    self.refresh_button.set_sensitive(False)
                    self.tray.refresh_menu.set_sensitive(False)
                    code, rate_error = self.main.reconnect()
                
                # Just normal 400's and 403'
                elif (code == 400 and self.main.status(ST_WAS_SEND)) or \
                     (code == 403 and not self.main.status(ST_WAS_SEND)):
                    
                    code = 500
                
                # A real 404! This may be raised if a user wasn't found
                elif self.main.status(ST_WAS_SEND) and code == 404:
                    code = -3 
                    
        # Catch network errors
        elif error.errno == -2:
            code = -4
            if self.main.status(ST_LOGIN_SUCCESSFUL):
                code = -5
        
        else:
            code = -1
        
        # Reset stuff
        self.main.unset_status(ST_WAS_SEND | ST_WAS_RETWEET | \
                               ST_WAS_RETWEET_NEW | ST_WAS_DELETE)
        
        
        # Show Warning Button --------------------------------------------------
        if code in (-5, 503):
            if code == -5: # Network lost
                info = lang.warning_network
                button = lang.warning_button_network
                
            else: # overload warning
                info = lang.warning_overload
                button = lang.warning_button_overload
            
            self.show_warning_button(button, info)
        
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
                
            self.show_error_button(button, info)
        
        # Show Error Dialog ----------------------------------------------------
        else:
            # Show GUI if minized in tray
            gobject.idle_add(self.gui.force_show)
            
            description = {
                -4 : lang.error_network,
                -3 : lang.error_user_not_found % self.main.message_user,
                -2 : lang.error_already_retweeted,
                0 : lang.error_internal % str(error),
                -7 : rate_error,
                401 : lang.error_login % self.main.username,
                404 : lang.error_login % self.main.username
            }[code]
            dialog.MessageDialog(self, MESSAGE_ERROR, description,
                                 lang.error_title)
        
        self.update_status()
    
    
    # Warning Button -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def hide_warning_button(self):
        if self.warning_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.warning_box.hide()
        
    def show_warning_button(self, button, info):
        self.warning_information = info
        if self.warning_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.warning_box.show()
        self.warning_label.set_markup(button)
    
    def show_warning_dialog(self, *args):
        if self.warning_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.hide_warning_button()
        self.warning_dialog = dialog.MessageDialog(self, MESSAGE_WARNING,
                             self.warning_information, lang.warning_title)



    # Warning Button -----------------------------------------------------------
    # --------------------------------------------------------------------------
    def hide_warning_button(self):
        if self.error_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.warning_box.hide()
        
    def show_warning_button(self, button, info):
        self.warning_information = info
        if self.warning_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.warning_box.show()
        self.warning_label.set_markup(button)
        
        # Show GUI if not shown so the user does notice the message
        if not self.is_shown:
            gobject.idle_add(self.show_gui)

    def show_warning_dialog(self, *args):
        if self.warning_dialog != None:
            self.warning_dialog.destroy()
            self.warning_dialog = None
        
        self.hide_warning_button()
        self.warning_dialog = dialog.MessageDialog(self, MESSAGE_WARNING,
                             self.warning_information, lang.warning_title)
    
    
    # Error Button -------------------------------------------------------------
    # --------------------------------------------------------------------------
    def hide_error_button(self):
        if self.error_dialog != None:
            self.error_dialog.destroy()
            self.error_dialog = None
        
        self.error_box.hide()
        
    def show_error_button(self, button, info):
        self.error_information = info
        if self.error_dialog != None:
            self.error_dialog.destroy()
            self.error_dialog = None
    
    def show_error_dialog(self, *args):
        if self.error_dialog != None:
            self.error_dialog.destroy()
            self.error_dialog = None
        
        self.hide_error_button()
        self.error_dialog = dialog.MessageDialog(self, MESSAGE_ERROR,
                             self.error_information, lang.error_title)

