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
                      UNSET_TIMEOUT, HTML_UNSET_ID, MESSAGE_ERROR, \
                      MESSAGE_WARNING, BUTTON_REFRESH, BUTTON_READ, \
                      BUTTON_HISTORY


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
        gtb.add_from_file(main.get_resource('main.glade'))
        frame = gtb.get_object('frame')
        self.add(frame)
        gtb.get_object('content').set_border_width(2)
        
        # Link Components
        self.multi_button = gtb.get_object('refresh')
        self.multi_button.connect('clicked', self.on_refresh_update)
        self.multi_button.set_tooltip_text(lang.tool_refresh)
        self.multi_state = BUTTON_REFRESH
        
        self.message_button = gtb.get_object('message')
        self.message_button.connect('clicked', self.on_mode)
        self.message_button.set_tooltip_text(lang.tool_mode)
        
        # Settings Button
        self.settings_button = gtb.get_object('settings')
        self.settings_button.connect('toggled', self.on_settings, False)
        
        self.settings_button.set_tooltip_text(lang.tool_settings)
        self.settings_toggle = False
        
        # About Button
        self.about_button = gtb.get_object('about')
        self.about_button.connect('toggled', self.on_about, False)
        
        self.about_button.set_tooltip_text(lang.tool_about)
        self.about_toggle = False
        
        self.quit_button = gtb.get_object('quit')
        self.quit_button.connect('clicked', self.on_quit)
        self.quit_button.set_tooltip_text(lang.tool_quit)
        
        # Info Label
        self.info_label = gtb.get_object('label')
        
        # Text Input
        self.text_scroll = gtb.get_object('textscroll')
        self.text = text.TextInput(self)
        self.text_scroll.add(self.text)
        
        # HTML
        self.html_scroll = gtb.get_object('htmlscroll')
        self.html = html.HTML(self.main, self)
        self.html_scroll.add(self.html)
        self.html_scroll.set_shadow_type(gtk.SHADOW_IN)
        self.html.splash()
        
        # Messages
        self.message_scroll = gtb.get_object('messagescroll')
        self.message = message.HTML(self.main, self)
        self.message_scroll.add(self.message)
        self.message_scroll.set_shadow_type(gtk.SHADOW_IN)
        self.message.splash()
        
        # Bars
        self.toolbar = gtb.get_object('toolbar')
        self.progress = gtb.get_object('progressbar')
        self.status = gtb.get_object('statusbar')
        
        # Warning Button
        self.warning_button = dialog.ButtonDialog(self, 'warning',
                                     lang.warning_template, lang.warning_title)
        
        # Error Button
        self.error_button = dialog.ButtonDialog(self, 'error',
                                     lang.error_template, lang.error_title)
        
        
        # Restore Position & Size ----------------------------------------------
        if main.settings.isset('position'):
            self.window_position = main.settings['position'][1:-1].split(',')
            self.move(int(self.window_position[0]),
                      int(self.window_position[1]))
        
        if main.settings.isset('size'):
            size = main.settings['size'][1:-1].split(',')
            self.resize(int(size[0]), int(size[1]))
        
        else:
            self.resize(280, 400)
        
        # Tray
        self.tray = tray.TrayIcon(self)
        
        # Events
        self.connect('delete_event', self.delete_event)
        self.connect('destroy', self.destroy_event)
        self.connect('window-state-event', self.state_event)
        self.connect('focus-out-event', self.fix_tooltips)
        
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
        
        
        # Accelerators ---------------------------------------------------------
        acc = gtk.AccelGroup()
        self.add_accel_group(acc)
        acc.connect_group(gtk.keysyms.t, gtk.gdk.CONTROL_MASK,
                          0, self.text.start_tweet)
        
        acc.connect_group(gtk.keysyms.d, gtk.gdk.CONTROL_MASK,
                          0, self.text.start_message)
        
        # Show GUI
        if not main.settings.is_true('tray', False) \
           or main.settings.is_true('crashed', False): # show after crash
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
        if self.main.settings.is_true('crashed', False):
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
        self.set_refresh_update(True)
        self.message_button.set_sensitive(self.main.status(ST_LOGIN_SUCCESSFUL))
    
    def show_progress(self):
        def progress_activity():
            self.progress.pulse()
            return self.main.status(ST_SEND) \
                   or self.main.status(ST_DELETE) \
                   or self.main.status(ST_CONNECT) \
                   or self.main.status(ST_HISTORY) \
                   or (self.mode == MODE_MESSAGES \
                   and self.message.load_state == HTML_LOADING) \
                   or (self.mode == MODE_TWEETS \
                   and self.html.load_state == HTML_LOADING)
            
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
        self.set_refresh_update(False)
        self.message_button.set_sensitive(False)
        self.warning_button.hide()
        self.error_button.hide()
    
    
    # Refresh / Read / History Button ------------------------------------------
    # --------------------------------------------------------------------------
    def set_refresh_update(self, mode, refresh_mode = None, status = True,
                           no_read = False):
        
        # History mode ---------------------------------------------------------
        if self.mode == MODE_MESSAGES and self.message.history_loaded:
            info = lang.tool_history_message
        
        elif self.mode == MODE_TWEETS and self.html.history_loaded:
            info = lang.tool_history
        
        else:
            info = None
            
        if info != None:
            self.multi_state = BUTTON_HISTORY
            self.multi_button.set_tooltip_text(info)
            self.multi_button.set_stock_id(gtk.STOCK_GOTO_TOP)
            self.multi_button.set_sensitive(True)
            if status:
                self.update_status()
            
            return
        
        
        # Toggle to read mode --------------------------------------------------
        if self.mode == MODE_MESSAGES and not no_read:
            read_mode = self.message.last_id > self.message.init_id
            
        elif self.mode == MODE_TWEETS and not no_read:
            read_mode = self.html.last_id > self.html.init_id
        
        else:
            read_mode = False
                
        # Set Sensitive
        self.multi_button.set_sensitive(read_mode)
        self.tray.read_menu.set_sensitive(read_mode)
        
        # Set icon and mode
        if info == None and read_mode:
            
            self.multi_state = BUTTON_READ
            self.multi_button.set_stock_id(gtk.STOCK_OK)
            
            
            # Set Tooltip
            if self.mode == MODE_TWEETS:
                self.multi_button.set_tooltip_text(lang.tool_read)
            
            elif self.mode == MODE_MESSAGES:
                self.multi_button.set_tooltip_text( lang.tool_read_message)
            
            if status:
                self.update_status()
            
            return
        
        # Toggle to refresh mode -----------------------------------------------
        if refresh_mode != None:
            mode = refresh_mode
    
        if not self.is_ready():
            mode = False
    
        # Set icon and mode
        self.multi_state = BUTTON_REFRESH
        self.multi_button.set_stock_id(gtk.STOCK_REFRESH)
    
        # Set Sensitive
        self.multi_button.set_sensitive(mode)
        self.tray.refresh_menu.set_sensitive(mode)
        
        # Set Tooltip
        if self.mode == MODE_TWEETS:
            self.multi_button.set_tooltip_text(lang.tool_refresh)
        
        elif self.mode == MODE_MESSAGES:
            self.multi_button.set_tooltip_text(lang.tool_refresh_message)
        
        # Check for message/tweet switch
        if self.is_ready():
            if self.text.go_send_message != None:
                self.set_mode(MODE_MESSAGES)
            
            elif self.text.go_send_tweet != None:
                self.set_mode(MODE_TWEETS)
            
            if status:
                self.update_status()

    
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
            self.set_status(lang.status_load_history \
                            if self.html.load_history_id != HTML_UNSET_ID \
                            else lang.status_load_message_history)
                    
        elif self.main.status(ST_CONNECT):
            self.set_status(lang.status_connecting % self.main.username)
        
        elif self.main.status(ST_LOGIN_ERROR):
            self.set_status(lang.status_error)
        
        elif not self.main.status(ST_LOGIN_SUCCESSFUL):
            self.set_status(lang.status_logout)
        
        elif self.main.status(ST_SEND) or self.main.status(ST_DELETE):
            pass
        
        elif self.main.status(ST_UPDATE):
            self.set_refresh_update(False, None, False)
            self.set_status(lang.status_update)
        
        elif self.main.refresh_time == UNSET_TIMEOUT \
             or  (self.mode == MODE_MESSAGES \
             and self.message.load_state == HTML_LOADING) \
             or (self.mode == MODE_TWEETS \
             and self.html.load_state == HTML_LOADING):
            
            self.set_status(lang.status_connected)
        
        elif (not self.text.is_typing or not self.text.has_focus) \
              and not self.main.status(ST_SEND):
            
            wait = self.main.refresh_timeout - \
                (calendar.timegm(time.gmtime()) - self.main.refresh_time)
            
            if wait == 0:
                self.set_refresh_update(False, None, False)
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
        dialog.MessageDialog(self, MESSAGE_INFO, lang.delete_info_tweet \
                             if tweet != UNSET_ID_NUM \
                             else lang.delete_info_message,
                             lang.delete_info_title)
    
    def show_favorite_error(self, name, mode):
        dialog.MessageDialog(self, MESSAGE_WARNING,
                             lang.error_favorite_on % lang.name(name) \
                             if mode else lang.error_favorite_off \
                             % lang.name(name), lang.error_title)
                    
    def show_crash_report(self):
        code = self.main.settings['crash_reason']
        
        # Python error, link to the traceback file
        if code == "70": #str(EX_SOFTWARE)
            from settings import CRASH_LOG_FILE
            info = lang.error_crashed_python % CRASH_LOG_FILE
            title = lang.error_crashed__python_title
        
        # Other errors, just display the code since that's all we got
        else:
            title = lang.error_crashed_title
            info = lang.error_crashed % code
        
        dialog.MessageDialog(self, MESSAGE_WARNING, lang.error_general + info,
                             title)
    
    
    # Show Error Dialog --------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_error(self, code, error_code, error_errno, rate_error):
        if code in (-9, -5, 503):
            if code == 503:# overload warning
                info = lang.warning_overload
                button = lang.warning_button_overload
                
            else: # twitter/network lost
                info = lang.warning_network_timeout if code == -9 \
                       else lang.warning_network
                
                button = lang.warning_button_network
                self.tray.set_tooltip_error(
                            (lang.tray_logged_in  % self.main.username) \
                            + '\n' + lang.tray_warning_network,
                            gtk.STOCK_DIALOG_WARNING)
            
            self.warning_button.show(button, info)
        
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
                
            self.error_button.show(button, info)
        
        # Show Error Dialog ----------------------------------------------------
        else:
            # Update Tray Icon
            if code in (-4, -7, 401, 404):
                self.tray.set_tooltip_error({
                    -4 : lang.tray_warning_network,
                    -7 : lang.tray_error_rate,
                    404 : lang.tray_error_login % self.main.username,
                    401 : lang.tray_error_login % self.main.username,
                }[code], gtk.STOCK_DIALOG_ERROR if code != -4 \
                         else gtk.STOCK_DIALOG_WARNING)
            
            # Clear already deleted tweets
            if self.main.delete_tweet_id != UNSET_ID_NUM:
                gobject.idle_add(self.html.remove, self.main.delete_tweet_id)
                
            elif self.main.delete_message_id != UNSET_ID_NUM:
                gobject.idle_add(self.message.remove,
                                 self.main.delete_message_id)
            
            self.main.delete_tweet_id = UNSET_ID_NUM
            self.main.delete_message_id = UNSET_ID_NUM
            
            # Show GUI if minimized to tray
            gobject.idle_add(self.force_show)
            
            description = {
                -13 : lang.error_message_not_found,
                -12 : lang.error_tweet_not_found,
                -11 : lang.error_duplicate,
                -9 : lang.error_network_timeout,
                -4 : lang.error_network,
                -3 : lang.error_user_not_found % self.main.message_user,
                -2 : lang.error_already_retweeted,
                -7 : rate_error,
                401 : lang.error_login % self.main.username,
                404 : lang.error_login % self.main.username
            }[code]
            dialog.MessageDialog(self, MESSAGE_ERROR if code != -4 \
                                 else MESSAGE_WARNING, description,
                                 lang.error_title)
        
        self.update_status()

