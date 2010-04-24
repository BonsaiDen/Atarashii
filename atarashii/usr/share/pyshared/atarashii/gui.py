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


from gui_events import GUIEventHandler
from gui_helpers import GUIHelpers
from utils import escape
from language import LANG as lang

from constants import CRASH_LOG_FILE
from constants import ST_CONNECT, ST_LOGIN_ERROR, ST_LOGIN_SUCCESSFUL, \
                      ST_DELETE, ST_UPDATE, ST_SEND, ST_RECONNECT, ST_HISTORY, \
                      ST_LOGIN_COMPLETE, ST_NETWORK_FAILED, ST_TRAY_WARNING

from constants import MODE_MESSAGES, MODE_TWEETS, UNSET_ID_NUM, HTML_LOADING, \
                      UNSET_USERNAME, MESSAGE_WARNING, MESSAGE_QUESTION, \
                      UNSET_TIMEOUT, HTML_UNSET_ID, MESSAGE_ERROR, \
                      MESSAGE_WARNING, BUTTON_REFRESH, BUTTON_READ, \
                      BUTTON_HISTORY

from constants import ERR_TWEET_NOT_FOUND, ERR_MESSAGE_NOT_FOUND, \
                      ERR_ALREADY_RETWEETED, ERR_TWEET_DUPLICATED, \
                      ERR_USER_NOT_FOUND, ERR_RATE_RECONNECT, \
                      ERR_RATE_LIMIT, ERR_NETWORK_FAILED, \
                      ERR_NETWORK_TWITTER_FAILED, ERR_USER_NOT_FOLLOW

from constants import HT_400_BAD_REQUEST, HT_401_UNAUTHORIZED, \
                      HT_404_NOT_FOUND, HT_500_INTERNAL_SERVER_ERROR, \
                      HT_502_BAD_GATEWAY, HT_503_SERVICE_UNAVAILABLE


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
        
        # Multi Button
        self.is_on_multi_button = False
        self.multi_container = gtb.get_object('multi_container')
        self.multi_image = gtb.get_object('multi_image')
        self.multi_button = gtb.get_object('multi')
        self.multi_button.connect('enter-notify-event',
                                   self.on_multi_move, True)
        
        self.multi_button.connect('leave-notify-event', self.on_multi_move)
        self.multi_button.connect('button-press-event', self.on_multi_press)
        self.multi_button.connect('button-release-event', self.on_multi_release)
        self.multi_button.set_tooltip_text(lang.multi_refresh)
        self.multi_state = BUTTON_REFRESH
        
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
        
        # Tabs
        self.tabsbox = gtb.get_object('tabsbox')
        self.tabs = gtb.get_object('pages')
        self.tab_tweets = gtb.get_object('tab_tweets')
        self.tab_messages = gtb.get_object('tab_messages')
        self.tabs.connect('switch-page', self.on_tabs)
        self.tabs.set_property('can-focus', False)
        self.tab_tweets.set_property('can-focus', False)
        self.tab_messages.set_property('can-focus', False)
        
        # Bars
        self.toolbar = gtb.get_object('toolbar')
        self.progress = gtb.get_object('progressbar')
        self.status = gtb.get_object('statusbar')
        
        # Warning Button
        self.warning_button = dialog.ButtonDialog(self, 'warning',
                                                  lang.warning_template,
                                                  lang.warning_title)
        
        # Error Button
        self.error_button = dialog.ButtonDialog(self, 'error',
                                                lang.error_template,
                                                lang.error_title)
        
        # Info Button
        self.info_button = dialog.ButtonDialog(self, 'information',
                                               lang.info_template,
                                               lang.info_title)
        
        # Loading Button
        self.load_button = dialog.ButtonDialog(self, 'load', '', '',
                                               True, self.main.stop_profile)
        
        # Fix a few resize problems
        self.current_size = (0, 0)
        self.connect('size-allocate', self.resize_event)
        
        # Profile
        self.profile_box = gtb.get_object('profilebox')
        self.profile_bio = gtb.get_object('profilebio')
        self.profile_info = gtb.get_object('profileinfo')
        self.profile_image = gtb.get_object('profileimage')
        self.profile_name = gtb.get_object('profilename')
        self.profile_status = gtb.get_object('profilestatus')
        gtb.get_object('profileclose').connect('clicked', self.hide_profile)
        
        
        # Restore Position & Size ----------------------------------------------
        if main.settings.isset('position'):
            self.window_position = main.settings['position'][1:-1].split(',')
            self.move(int(self.window_position[0]),
                      int(self.window_position[1]))
        
        if main.settings.isset('size'):
            size = main.settings['size'][1:-1].split(',')
            self.resize(int(size[0]), int(size[1]))
        
        else:
            self.resize(280, HT_400_BAD_REQUEST)
        
        # Dialogs
        self.about_dialog = None
        self.settings_dialog = None
        
        # Tray
        self.activate_tries = 0
        self.tray = tray.TrayIcon(self)
        
        # Events
        self.connect('delete_event', self.delete_event)
        self.connect('destroy', self.destroy_event)
        self.connect('window-state-event', self.state_event)
        self.connect('focus-out-event', self.fix_tooltips)
        
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
        
        acc.connect_group(gtk.keysyms.t, gtk.gdk.MOD1_MASK,
                          0, lambda *args: self.on_tabs(None, None, 0))
        
        acc.connect_group(gtk.keysyms.d, gtk.gdk.MOD1_MASK,
                          0, lambda *args: self.on_tabs(None, None, 1))
        
        # Show GUI
        if not main.settings.is_true('tray', False) \
           or main.settings.is_true('crashed', False): # show after crash
            self.show_gui()
        
        else:
            gtk.gdk.notify_startup_complete()
        
        gobject.idle_add(self.main.on_init)
    
    
    # Initial Show -------------------------------------------------------------
    def show_gui(self):
        self.show_all()
        
        # Fix tabs
        tab_height = self.tab_tweets.get_allocation()[3]
        self.tabs.set_size_request(-1, tab_height + 9)
        
        # Multi Button
        self.on_multi_move(None, None)
        
        # Hide Warning/Error Buttons
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
        
        self.is_shown = True
        gobject.idle_add(self.scroll_views)
    
    # Scroll the views when started in tray
    def scroll_views(self):
        if self.mode == MODE_TWEETS:
            self.html.loaded(None, None, True)
        
        elif self.mode == MODE_MESSAGES:
            self.message.loaded(None, None, True)
    
    def force_show(self):
        if not self.is_shown:
            self.show_gui()
    
    
    # GUI Switchers ------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_input(self, resize=True, focus=False):
        self.progress.hide()
        self.progress_visible = False
        self.text_scroll.show()
        if resize:
            self.text.resize()
        
        else:
            self.text.resize(1)
        
        self.text.set_sensitive(True)
        self.set_multi_button(True)
        if self.main.status(ST_LOGIN_SUCCESSFUL):
            self.tabsbox.show()
        
        self.tabs.set_sensitive(self.main.status(ST_LOGIN_SUCCESSFUL))
        
        # Force update of the statusbar
        gobject.idle_add(self.update_status, True)
        
        # Focus current view
        if focus and not self.text.has_typed:
            if self.mode == MODE_MESSAGES:
                self.message.focus_me()
            
            elif self.mode == MODE_TWEETS:
                self.html.focus_me()
            
            # TODO implement search
            else:
                pass
        
        # Refocus textbox if needed
        elif self.text.has_typed:
            self.text.focus()
            gobject.idle_add(self.text.grab_focus)
    
    def progress_activity(self):
        self.progress.pulse()
        if self.main.any_status(ST_SEND, ST_DELETE, ST_CONNECT, ST_HISTORY):
            return True
        
        elif self.mode == MODE_MESSAGES \
             and self.message.load_state == HTML_LOADING:
            
            return True
        
        elif self.mode == MODE_TWEETS and self.html.load_state == HTML_LOADING:
            return True
        
        else:
            return False
    
    def show_progress(self):
        self.progress.set_fraction(0.0)
        self.progress.show()
        self.info_label.hide()
        self.text_scroll.hide()
        if not self.progress_visible:
            gobject.timeout_add(100, self.progress_activity)
        
        self.progress_visible = True
    
    def hide_all(self, progress=True):
        if progress:
            self.progress.hide()
            self.progress_visible = False
        
        if not self.main.status(ST_LOGIN_SUCCESSFUL):
            self.tabsbox.hide()
        
        self.text_scroll.hide()
        self.set_multi_button(False, None, False, True)
        self.tabs.set_sensitive(False)
    
    
    # Profile ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def show_profile(self, user, friend):
        if not self.main.profile_pending:
            return False
        
        self.main.profile_current_user = user.screen_name
        self.load_button.hide()
        
        # Image / Name / Tweets
        img_file = self.main.updater.get_image(None, False, user)
        buf = gtk.gdk.pixbuf_new_from_file_at_size(img_file, 48, 48)
        self.profile_image.set_from_pixbuf(buf)
        
        url = ('<a href="http://twitter.com/%s">'
               + lang.profile_link + '</a>') % user.screen_name
        
        self.profile_name.set_label(lang.profile_name % (user.screen_name, url))
        self.profile_info.set_label(lang.profile_info \
                                    % (user.name, user.statuses_count,
                                       user.followers_count,
                                       user.friends_count))
        
        # Detailed information
        details = []
        if user.url is not None and user.url.strip() != '':
            details.append(lang.profile_website % (escape(user.url),
                                                   escape(user.url)))
        
        if user.location is not None and user.location.strip() != '':
            details.append(lang.profile_location % escape(user.location))
        
        if user.description is not None and user.description.strip() != '':
            details.append(lang.profile_description % escape(user.description))
        
        self.profile_bio.set_label('\n'.join(details))
        
        if len(details) == 0:
            self.profile_bio.hide()
        
        else:
            self.profile_bio.show()
        
        # Status
        if friend[0].following and friend[0].followed_by:
            status = lang.profile_status_both
        
        elif friend[0].following:
            status = lang.profile_status_following
        
        elif friend[0].followed_by:
            status = lang.profile_status_followed
        
        elif friend[0].blocking:
            status = lang.profile_status_blocked
        
        else:
            status = None
        
        if status is not None:
            self.profile_status.set_label(status)
            self.profile_status.show()
        
        else:
            self.profile_status.hide()
        
        self.profile_box.show()
    
    def hide_profile(self, *args):
        self.main.profile_current_user = UNSET_USERNAME
        self.profile_box.hide()
    
    
    # Refresh / Read / History Button ------------------------------------------
    # --------------------------------------------------------------------------
    def set_multi_button(self, mode, refresh_mode=None, status=True,
                         no_read=False):
        
        # History mode
        if self.mode == MODE_MESSAGES and self.message.history_loaded:
            history_info = lang.multi_history_message
            history_mode = True
        
        elif self.mode == MODE_TWEETS and self.html.history_loaded:
            history_info = lang.multi_history
            history_mode = True
        
        else:
            history_info = None
            history_mode = False
        
        # Read mode
        if self.mode == MODE_MESSAGES:
            read_mode = self.message.count > 0
            read_icon = read_mode
        
        elif self.mode == MODE_TWEETS:
            read_mode = self.html.count > 0
            read_icon = read_mode
        
        else:
            read_mode = False
            read_icon = False
        
        # Refresh mode
        if refresh_mode is not None:
            mode = refresh_mode
        
        if not self.is_ready() or read_mode or history_info is not None:
            mode = False
        
        if self.main.status(ST_UPDATE) or no_read:
            history_mode = False
            read_mode = False
            mode = False
        
        # Sensitivity
        self.tray.read_menu.set_sensitive(read_mode)
        self.tray.refresh_menu.set_sensitive(mode)
        
        # Icon
        if history_info is not None:
            multi_icon = gtk.STOCK_GOTO_TOP
            self.multi_button.set_tooltip_text(history_info)
        
        elif read_icon:
            multi_icon = gtk.STOCK_OK
            if self.mode == MODE_TWEETS:
                self.multi_button.set_tooltip_text(lang.multi_read)
            
            elif self.mode == MODE_MESSAGES:
                self.multi_button.set_tooltip_text(lang.multi_read_message)
        
        else:
            multi_icon = gtk.STOCK_REFRESH
            if self.mode == MODE_TWEETS:
                self.multi_button.set_tooltip_text(lang.multi_refresh)
            
            elif self.mode == MODE_MESSAGES:
                self.multi_button.set_tooltip_text(lang.multi_refresh_message)
        
        self.multi_image.set_from_stock(multi_icon, gtk.ICON_SIZE_MENU)
        
        # Status
        if status:
            self.update_status()
        
        # Set History
        if history_info is not None:
            self.multi_state = BUTTON_HISTORY
            self.multi_button.set_sensitive(history_mode)
        
        # Set Read
        elif read_mode:
            self.multi_state = BUTTON_READ
            self.multi_button.set_sensitive(read_mode)
        
        # Set Refresh
        else:
            self.multi_state = BUTTON_REFRESH
            self.multi_button.set_sensitive(mode)
        
        # Hide?
        if self.main.username == UNSET_USERNAME \
           or not self.main.status(ST_LOGIN_SUCCESSFUL):
            
            self.multi_button.hide()
        
        else:
            self.multi_button.show()
        
        # Check for message/tweet switch
        if self.is_ready():
            if self.text.message_to_send is not None:
                self.set_mode(MODE_MESSAGES)
            
            elif self.text.tweet_to_send is not None:
                self.set_mode(MODE_TWEETS)
    
    
    # Statusbar ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def update_status(self, once=False):
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
        
        elif self.main.any_status(ST_SEND, ST_DELETE):
            pass
        
        elif self.main.status(ST_UPDATE):
            self.set_multi_button(False, None, False, True)
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
            
            if wait < 0:
                wait = 0
            
            if wait == 0:
                self.set_multi_button(False, None, False, True)
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
        self.info_button.show(lang.delete_button_tweet \
                             if tweet != UNSET_ID_NUM \
                             else lang.delete_button_message,
                             None, None, 5000)
    
    def show_retweet_info(self, name):
        self.info_button.show(lang.retweet_button, None, None, 5000)
    
    def show_follow_info(self, mode, name):
        self.info_button.show(lang.follow_button % name if mode \
                              else lang.unfollow_button % name,
                              None, None, 5000)
    
    def show_follow_error(self, mode, name):
        dialog.MessageDialog(self, MESSAGE_ERROR,
                             lang.error_follow % name if mode \
                             else lang.error_unfollow % name, lang.error_title)
    
    def show_profile_error(self, name):
        dialog.MessageDialog(self, MESSAGE_ERROR,
                             lang.profile_error % lang.name(name),
                             lang.error_title)
    
    def ask_for_block_spam(self, user, yes, noo):
        dialog.MessageDialog(self, MESSAGE_QUESTION,
                        lang.block_user_spam % user,
                        lang.block_title,
                        yes_callback = yes, no_callback = noo)
    
    def show_block_info(self, mode, name, spam):
        blocked = lang.block_button_spam % name if spam \
                  else lang.block_button % name
        
        self.info_button.show(blocked if mode \
                              else lang.unblock_button % name,
                              None, None, 5000)
    
    def show_block_error(self, mode, name):
        dialog.MessageDialog(self, MESSAGE_ERROR,
                             lang.error_block % name if mode \
                             else lang.error_unblock % name, lang.error_title)
    
    def show_favorite_error(self, mode, name):
        dialog.MessageDialog(self, MESSAGE_ERROR,
                             lang.error_favorite_on % lang.name(name) \
                             if mode else lang.error_favorite_off \
                             % lang.name(name), lang.error_title)
    
    def show_crash_report(self):
        code = self.main.settings['crash_reason']
        
        # Python error, link to the traceback file
        if code == '70': #str(EX_SOFTWARE)
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
        # Is Atarashii visible?
        is_visible = self.is_shown and self.on_screen()
        
        if self.show_box(code, rate_error, is_visible):
            return False
        
        else:
            
            # Clear already deleted tweets
            if self.main.delete_tweet_id != UNSET_ID_NUM:
                gobject.idle_add(self.html.remove, self.main.delete_tweet_id)
            
            elif self.main.delete_message_id != UNSET_ID_NUM:
                gobject.idle_add(self.message.remove,
                                 self.main.delete_message_id)
            
            self.main.delete_tweet_id = UNSET_ID_NUM
            self.main.delete_message_id = UNSET_ID_NUM
            
            description = {
                ERR_MESSAGE_NOT_FOUND: lang.error_message_not_found,
                ERR_TWEET_NOT_FOUND: lang.error_tweet_not_found,
                ERR_TWEET_DUPLICATED: lang.error_duplicate,
                ERR_NETWORK_TWITTER_FAILED: lang.error_network_timeout,
                ERR_NETWORK_FAILED: lang.error_network,
                ERR_USER_NOT_FOUND: lang.error_user_not_found \
                                       % self.main.message_user,
                
                ERR_USER_NOT_FOLLOW: lang.error_user_not_follow,
                
                ERR_ALREADY_RETWEETED: lang.error_already_retweeted,
                ERR_RATE_RECONNECT: rate_error,
                HT_401_UNAUTHORIZED: lang.error_login % self.main.last_username,
                HT_404_NOT_FOUND: lang.error_login % self.main.last_username
            }[code]
            dialog.MessageDialog(self, MESSAGE_WARNING \
                                 if code == ERR_NETWORK_FAILED \
                                 else MESSAGE_ERROR, description,
                                 lang.error_title)
        
        self.update_status()
    
    
    # Show Error/Warning Boxes -------------------------------------------------
    def show_box(self, code, rate_error, is_visible):
    
        # Tray icon
        if code in (ERR_NETWORK_FAILED, ERR_NETWORK_TWITTER_FAILED,
                    ERR_RATE_RECONNECT, HT_404_NOT_FOUND, HT_401_UNAUTHORIZED,
                    HT_503_SERVICE_UNAVAILABLE):
            
            login = lang.tray_logged_in % self.main.last_username \
                    if self.main.status(ST_LOGIN_COMPLETE) \
                    else lang.tray_error_login % self.main.last_username
            
            msg = {
                ERR_NETWORK_FAILED: login + '\n' + lang.tray_warning_network,
                
                ERR_NETWORK_TWITTER_FAILED:
                    login + '\n' + lang.tray_warning_timeout \
                    if self.main.status(ST_LOGIN_COMPLETE) \
                    else login + '\n' + lang.tray_warning_twitter,
                
                ERR_RATE_RECONNECT: login + '\n' + lang.tray_error_rate,
                HT_404_NOT_FOUND:
                    login,
                
                HT_401_UNAUTHORIZED:
                    login,
                
                HT_503_SERVICE_UNAVAILABLE:
                    login + '\n' + lang.tray_warning_overload
            }[code]
            
            # Show GUI if not shown so the user does notices the message
            if not self.is_shown:
                gobject.idle_add(self.show_gui)
            
            # Update tray tooltip
            self.main.set_status(ST_TRAY_WARNING)
            icon = gtk.STOCK_DIALOG_WARNING if code in (ERR_NETWORK_FAILED,
                                            ERR_NETWORK_TWITTER_FAILED,
                                            HT_503_SERVICE_UNAVAILABLE) else \
                                            gtk.STOCK_DIALOG_ERROR
            
            gobject.idle_add(self.tray.set_tooltip_error, msg, icon)
        
        # Warning popups
        if code in (ERR_NETWORK_TWITTER_FAILED, ERR_NETWORK_FAILED,
                      HT_503_SERVICE_UNAVAILABLE):
            
            msg = lang.tray_logged_in % self.main.last_username + '\n'
            
            # overload warning
            if code == HT_503_SERVICE_UNAVAILABLE:
                info = lang.warning_overload
                button = lang.warning_button_overload
                self.notifcation(MESSAGE_WARNING, lang.tray_warning_overload)
                self.warning_button.show(button, info)
            
            # twitter lost / network lost / network failed
            else:
                if code == ERR_NETWORK_TWITTER_FAILED:
                    if self.main.status(ST_LOGIN_COMPLETE):
                        info = lang.warning_network_timeout
                    
                    else:
                        info = lang.warning_network_twitter
                
                elif code == ERR_NETWORK_FAILED:
                    info = lang.warning_network
                
                button = lang.warning_button_network
                if not self.main.status(ST_NETWORK_FAILED):
                    self.notifcation(MESSAGE_WARNING, lang.tray_warning_network)
                    self.main.set_status(ST_NETWORK_FAILED)
                
                # Don't override send errors and other stuff with 'unimportant'
                # network warnings
                if not self.warning_button.is_visible:
                    self.warning_button.show(button, info)
            
            return True
        
        # Error popups
        elif code in (HT_500_INTERNAL_SERVER_ERROR, HT_502_BAD_GATEWAY,
                      ERR_RATE_LIMIT):
            
            msg = lang.tray_logged_in % self.main.last_username + '\n'
            if code != ERR_RATE_LIMIT:
                
                # internal twitter error
                if code == HT_500_INTERNAL_SERVER_ERROR:
                    button = lang.error_button_twitter
                    info = lang.error_twitter
                    simple = lang.tray_error_twitter
                
                # Twitter down
                else:
                    button = lang.error_button_down
                    info = lang.error_down
                    simple = lang.tray_error_down
            
            # Rate limit exceeded
            else:
                info = rate_error
                button = lang.error_button_rate_limit
                simple = lang.tray_error_rate_limit
            
            self.error_button.show(button, info)
            self.notifcation(MESSAGE_ERROR, simple)
            return True

