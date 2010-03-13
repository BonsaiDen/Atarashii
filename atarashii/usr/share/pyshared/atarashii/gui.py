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
import exceptions

import html
import message
import tray
import text
import dialog

from lang import lang
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
        
        # Load Components
        gtb = gtk.Builder()
        gtb.add_from_file(main.get_resource("main.glade"))
        frame = gtb.get_object("frame")
        self.add(frame)
        
        # Link Components
        self.refresh_button = gtb.get_object("refresh")
        self.refresh_button.connect("clicked", self.on_refresh)
        self.refresh_button.set_tooltip_text(lang.toolRefresh)
        
        self.history_button = gtb.get_object("history")
        self.history_button.connect("clicked", self.on_history)
        self.history_button.set_tooltip_text(lang.toolHistory)
        
        self.read_button = gtb.get_object("read")
        self.read_button.connect("clicked", self.on_read)
        self.read_button.set_tooltip_text(lang.toolRead)
        
        self.message_button = gtb.get_object("message")
        self.message_button.connect("clicked", self.on_mode)
        self.message_button.set_tooltip_text(lang.toolMode)
        
        # Settings Button
        self.settings_button = gtb.get_object("settings")
        self.settings_button.connect("toggled",
                                     lambda *args: self.on_settings(False))
        
        self.settings_button.set_tooltip_text(lang.toolSettings)
        self.settings_toggle = False
        
        # About Button
        self.about_button = gtb.get_object("about")
        self.about_button.connect("toggled",
                                  lambda *args: self.on_about(False))
        
        self.about_button.set_tooltip_text(lang.toolAbout)
        self.about_toggle = False
        
        self.quit_button = gtb.get_object("quit")
        self.quit_button.connect("clicked", self.on_quit)
        self.quit_button.set_tooltip_text(lang.toolQuit)
        
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
        
        # Messages
        self.message_scroll = gtb.get_object("messagescroll")
        self.message = message.HTML(self.main, self)
        self.message_scroll.add(self.message)
        self.message_scroll.set_shadow_type(gtk.SHADOW_IN)
        
        
        self.content = gtb.get_object("content")
        self.content.set_border_width(2)
        
        # Bars
        self.toolbar = gtb.get_object("toolbar")
        self.progress = gtb.get_object("progressbar")
        self.status = gtb.get_object("statusbar")
        
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
        self.init_event = self.connect("expose-event", self.draw_event)
        
        # Dialogs
        self.about_dialog = None
        self.settings_dialog = None
        
        # Variables
        self.mode = MODE_TWEETS
        self.window_position = None
        self.minimized = False
        
        self.show_all()
        
        self.set_mode(self.mode)
        
        # Statusbar Updater
        self.update_status()
        gobject.timeout_add(1000, lambda: self.update_status())
        
        # Show
        self.show_input()
    
    
    # GUI Switchers ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_input(self, resize = True):
        self.progress.hide()
        self.text_scroll.show()
        if resize:
            self.text.resize()
        else:
            self.text.resize(1)
        
        self.text.set_sensitive(True)
        self.check_refresh()
        self.check_read()
        self.message_button.set_sensitive(True)
    
    def show_progress(self):
        def progress_activity():
            self.progress.pulse()
            return self.main.is_sending or self.main.is_connecting or \
                self.main.is_loading_history or \
                (self.mode == MODE_MESSAGES and \
                self.message.loaded == HTML_LOADING) or \
                (self.mode == MODE_TWEETS and self.html.loaded == HTML_LOADING)
            
        self.progress.set_fraction(0.0)
        self.progress.show()
        self.info_label.hide()
        self.text_scroll.hide()
        gobject.timeout_add(100, lambda: progress_activity())
    
    def hide_all(self, progress = True):
        if progress:
            self.progress.hide()
            
        self.text_scroll.hide()
        self.refresh_button.set_sensitive(False)
        self.read_button.set_sensitive(False)
        self.history_button.set_sensitive(False)
        self.message_button.set_sensitive(False)
    
    
    # Statusbar ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def update_status(self, once = False):
        if self.text.has_typed:
            pass
        
        elif self.main.is_reconnecting:
            wait = self.main.refresh_timeout - \
                    (calendar.timegm(time.gmtime()) - self.main.reconnect_time)
            if wait < 60:
                self.set_status(lang.statusReconnectSeconds % wait)
            
            elif wait < 105:
                self.set_status(lang.statusReconnectMinute)
                
            else:
                self.set_status(
                    lang.statusReconnectMinutes % math.ceil(wait / 60.0))
        
        elif self.main.is_loading_history:
            self.set_status(
                lang.statusLoadHistory if \
                self.html.load_history_id != HTML_UNSET_ID else \
                lang.statusLoadMessageHistory)
        
        elif self.main.is_connecting:
            self.set_status(lang.statusConnecting % self.main.username)
        
        elif self.main.login_error:
            self.set_status(lang.statusError)
        
        elif not self.main.login_status:
            self.set_status(lang.statusLogout)
        
        elif self.main.is_updating:
            self.refresh_button.set_sensitive(False)
            self.read_button.set_sensitive(False)
            self.set_status(lang.statusUpdate)
        
        elif self.main.refresh_time == UNSET_TIMEOUT or \
            (self.mode == MODE_MESSAGES and \
            self.message.loaded == HTML_LOADING) or \
            (self.mode == MODE_TWEETS and self.html.loaded == HTML_LOADING):
            
            self.set_status(lang.statusConnected)
        
        elif (not self.text.is_typing or not self.text.has_focus) and not \
            self.main.is_sending:
            
            wait = self.main.refresh_timeout - \
                (calendar.timegm(time.gmtime()) - self.main.refresh_time)
            
            if wait == 0:
                self.refresh_button.set_sensitive(False)
                self.read_button.set_sensitive(False)
                self.set_status(lang.statusUpdate)
            
            elif wait == 1:
                self.set_status(lang.statusOneSecond)
                
            else:
                if wait < 60:
                    self.set_status(lang.statusSeconds % wait)
                
                elif wait < 105:
                    self.set_status(lang.statusMinute)
                    
                else:
                    self.set_status(lang.statusMinutes % math.ceil(wait / 60.0))
        
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
        if self.main.is_sending:
            return
        
        if self.main.reply_user == UNSET_TEXT and \
            self.main.retweet_user == UNSET_TEXT and \
            self.main.message_user == UNSET_TEXT:
            
            self.info_label.set_markup(UNSET_LABEL)
            self.info_label.hide()
        
        elif self.main.retweet_user != UNSET_TEXT:
            self.set_label_text(lang.labelRetweet % self.main.retweet_user)
            self.info_label.show()
        
        elif self.main.reply_text != UNSET_TEXT:
            self.set_label_text(lang.labelReplyText % self.main.reply_text)
            self.info_label.show()
        
        elif self.main.reply_user != UNSET_TEXT:
            self.set_label_text(lang.labelReply % self.main.reply_user)
            self.info_label.show()
        
        # Messages
        elif self.main.message_text != UNSET_TEXT:
            self.set_label_text(lang.labelMessageText % self.main.message_text)
            self.info_label.show()
        
        elif self.main.message_user != UNSET_TEXT:
            self.set_label_text(lang.labelMessage % self.main.message_user)
            self.info_label.show()
    
    def set_label_text(self, text):
        # Get Font Width
        font = self.info_label.create_pango_context().get_font_description()
        layout = self.info_label.create_pango_layout("")
        layout.set_markup(text)
        layout.set_font_description(font)
        
        # Truncate till it fits
        width = self.info_label.get_allocation()[2]
        cur = layout.get_pixel_size()[0]
        if cur > width:
            while cur > width:
                text = text[:-3]
                layout.set_markup(text + "...")
                cur = layout.get_pixel_size()[0]
            
            self.info_label.set_markup(text + "...")
            
        else:
            self.info_label.set_markup(text)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_height(self, widget):
        size = widget.get_allocation()
        return size[3] - size[0]
    
    def set_app_title(self):
        if self.main.username == UNSET_TEXT:
            self.set_title(lang.title)
        
        elif self.mode == MODE_MESSAGES:
            if self.html.count > 0:
                self.set_title((lang.titleTweets if self.html.count > 1 else \
                                lang.titleTweet) % self.html.count)
            else:
                self.set_title(lang.titleLoggedIn % self.main.username)
        
        elif self.mode == MODE_TWEETS:
            if self.message.count > 0:
                self.set_title((lang.titleMessages if self.html.count > 1 else \
                                lang.titleMessage) % self.message.count)
            else:
                self.set_title(lang.titleLoggedIn % self.main.username)
    
    def check_refresh(self):
        if self.is_ready():
            self.refresh_button.set_sensitive(True)
            
            # Check for goMessage
            if self.text.go_send_message != None:
                self.set_mode(MODE_MESSAGES)
                
            self.update_status()
    
    def check_read(self):
        if self.mode == MODE_MESSAGES:
            self.read_button.set_sensitive(
                             self.message.last_id > self.message.init_id)
        
        elif self.mode == MODE_TWEETS:
            self.read_button.set_sensitive(
                             self.html.last_id > self.html.init_id)
            
        else:
            self.read_button.set_sensitive(False)
    
    def set_mode(self, mode):
        if mode == None:
            self.mode = MODE_TWEETS
        else:
            self.mode = mode
        
        if self.mode == MODE_MESSAGES:
            self.message_button.set_active(True)
            
        else:
            self.on_mode()
    
    def is_ready(self):
        return not self.main.is_updating and \
                   self.message.loaded == HTML_LOADED and \
                   self.html.loaded == HTML_LOADED
    
    
    # Message Dialogs ----------------------------------------------------------
    # --------------------------------------------------------------------------
    def enter_password(self):
        self.main.api_temp_password = None
        dialog.PasswordDialog(self, lang.passwordTitle,
                                lang.passwordQuestion % self.main.username)
    
    def ask_for_retweet(self, name, yes, noo):
        dialog.MessageDialog(self, MESSAGE_QUESTION,
                        lang.retweetQuestion,
                        lang.retweetTitle % name,
                        yes_callback = yes, no_callback = noo)
    
    def show_retweet_info(self, name):
        dialog.MessageDialog(self, MESSAGE_INFO,
                        lang.retweetInfo % name,
                        lang.retweetInfoTitle)
    
    
    # Error & Warning ----------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_error(self, error):
        if self.main.was_sending:
            self.show_input()
            
            # Select Textbox?
            if not self.main.was_retweeting or \
                (self.main.retweet_text != UNSET_TEXT or \
                self.main.reply_user != UNSET_TEXT or \
                self.main.reply_id != UNSET_ID_NUM):
                self.text.grab_focus()
                
        try:
            code = error.response.status
            if error.reason.startswith("Share sharing"):
                code = -2
                
        except:
            try:
                if error.reason.startswith("HTTP Error "):
                    code = int(error.reason[11:14])
                
                elif type(error) == exceptions.IOError:
                    code = -1
                    
                else:
                    code = 0
                
            except:
                code = 0
        
        # Ratelimit error
        if (code == 400 and not self.main.was_sending) or \
           (code == 403 and self.main.was_sending):
            
            self.refresh_button.set_sensitive(False)
            rate_error = self.main.reconnect()
            
        elif (code == 400 and self.main.was_sending) or \
             (code == 403 and not self.main.was_sending):
            
            code = 500
            rate_error = ""
            
        else:
            rate_error = ""
        
        # 404's
        if self.main.was_sending and code == 404:
            code = -3
            
        self.main.was_sending = False
        self.main.was_retweeting = False
        
        # Show Warning on url error or error message for anything else
        if code == -1 or code == 500 or code == 502 or code == 503:
            
            # Show only one warning at a time to prevent dialog cluttering
            if not self.main.request_warning_shown:
                self.main.request_warning_shown = True
                
                def unset():
                    self.main.request_warning_shown = False
                    
                dialog.MessageDialog(self, MESSAGE_WARNING,
                    lang.warningURL, lang.warningTitle,
                    ok_callback = unset)
                
        else:
            description = {
                -3 : lang.errorUserNotFound,
                -2 : lang.errorAlreadyRetweeted,
                0 : lang.errorInternal % str(error),
                404 : lang.errorLogin % self.main.username,
                401 : lang.errorLogin % self.main.username,
                403 : rate_error,
                400 : rate_error,
                500 : lang.errorTwitter,
                502 : lang.errorDown,
                503 : lang.errorOverload
            }[code]
            dialog.MessageDialog(self, MESSAGE_ERROR, description,
                                 lang.errorTitle)
        
        self.update_status()
    
    def show_warning(self, limit):
        dialog.MessageDialog(self, MESSAGE_WARNING, lang.warningText % limit,
                                lang.warningTitle)
    
    
    # Handlers -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_refresh(self, *args):
        if self.mode == MODE_MESSAGES:
            self.main.updater.refresh_messages = True
        else:
            self.main.updater.refresh_now = True
    
    def on_history(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(lambda: self.message.clear())
            
        else:
            gobject.idle_add(lambda: self.html.clear())
    
    def on_read(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(lambda: self.message.read())
            
        else:
            gobject.idle_add(lambda: self.html.read())
    
    def on_mode(self, *args):
        if self.message_button.get_active():
            self.mode = MODE_MESSAGES
        else: # TODO add case for searchbutton
            self.mode = MODE_TWEETS
        
        if self.mode == MODE_MESSAGES:
            self.history_button.set_tooltip_text(lang.toolHistoryMessage)
            self.read_button.set_tooltip_text(lang.toolReadMessage)
            self.refresh_button.set_tooltip_text(lang.toolRefreshMessage)
            self.html_scroll.hide()
            self.message_scroll.show()
            self.message.grab_focus()
            self.read_button.set_sensitive(
                             self.message.last_id > self.message.init_id)
            
            self.history_button.set_sensitive(self.message.history_loaded)
            
            if self.message.loaded == HTML_LOADING:
                self.show_progress()
            
            elif self.message.loaded == HTML_LOADED:
                self.show_input()
        
        elif self.mode == MODE_TWEETS:
            self.history_button.set_tooltip_text(lang.toolHistory)
            self.read_button.set_tooltip_text(lang.toolRead)
            self.refresh_button.set_tooltip_text(lang.toolRefresh)
            self.message_scroll.hide()
            self.html_scroll.show()
            self.html.grab_focus()
            self.read_button.set_sensitive(
                             self.html.last_id > self.html.init_id)
            
            self.history_button.set_sensitive(self.html.history_loaded)
            
            if self.html.loaded == HTML_LOADING:
                self.show_progress()
            
            elif self.html.loaded == HTML_LOADED:
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
    
    def draw_event(self, *args):
        self.disconnect(self.init_event)
        gobject.idle_add(lambda: self.main.on_init())

