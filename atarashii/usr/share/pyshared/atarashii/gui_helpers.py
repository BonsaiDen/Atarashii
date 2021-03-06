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


# GUI / Helpers ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from utils import escape, strip_tags
from lang import LANG as lang

from constants import ST_SEND, ST_CONNECT, ST_LOGIN_SUCCESSFUL, \
                      ST_LOGIN_COMPLETE, ST_UPDATE, ST_NETWORK_FAILED, \
                      ST_LOGIN_ERROR

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_LOADED, MESSAGE_ERROR, \
                      MODE_PROFILE

from constants import UNSET_TEXT, UNSET_STRING, UNSET_LABEL, UNSET_USERNAME, \
                      UNSET_TIMEOUT


class GUIHelpers(object):
    def set_label(self):
        if self.main.status(ST_SEND):
            return False
        
        # Don't show in profile mode
        if self.mode == MODE_PROFILE:
            self.info_label.set_markup(UNSET_LABEL)
            self.info_label.hide()
        
        # Unset
        elif self.main.reply_user == UNSET_USERNAME \
           and self.main.retweet_user == UNSET_USERNAME \
           and self.main.message_user == UNSET_USERNAME \
           and self.main.edit_text == UNSET_TEXT:
            
            self.info_label.set_markup(UNSET_LABEL)
            self.info_label.hide()
        
        # Edit
        elif self.main.edit_text != UNSET_TEXT:
            if self.main.edit_reply_user != UNSET_USERNAME:
                self.set_label_text(lang.label_edit_reply,
                                    self.main.edit_reply_user,
                                    self.main.edit_text)
            
            else:
                self.set_label_text(lang.label_edit, self.main.edit_text)
            
            self.info_label.show()
        
        # RT
        elif self.main.retweet_user != UNSET_USERNAME:
            self.set_label_text(lang.label_retweet, self.main.retweet_user)
            self.info_label.show()
        
        # Reply
        elif self.main.reply_text != UNSET_TEXT:
            self.set_label_text(lang.label_reply_text, self.main.reply_text)
            self.info_label.show()
        
        elif self.main.reply_user != UNSET_USERNAME:
            self.set_label_text(lang.label_reply, self.main.reply_user)
            self.info_label.show()
        
        # Messages
        elif self.main.message_text != UNSET_TEXT:
            self.set_label_text(lang.label_message_text, self.main.message_text)
            self.info_label.show()
        
        elif self.main.message_user != UNSET_USERNAME:
            self.set_label_text(lang.label_message, self.main.message_user)
            self.info_label.show()
    
    def set_label_text(self, info, label_text, label_extra=None):
        label_text = label_text.replace('\n', '').replace('\r', '')
        
        if label_extra:
            self.info_label.set_markup(info % (escape(label_text),
                                               escape(label_extra)))
        
        else:
            self.info_label.set_markup(info % escape(label_text))
    
    
    # App Title / Tabs / Tray Icon updating ------------------------------------
    def update_app(self, view_mode=False):
        if self.main.username == UNSET_USERNAME \
           or not self.main.any_status(ST_LOGIN_SUCCESSFUL, ST_CONNECT):
            
            self.set_title(lang.title)
        
        elif self.main.status(ST_CONNECT):
            self.set_title(lang.title_logging_in % self.main.username)
        
        # Tray Tooltip
        if not self.main.status(ST_CONNECT) \
           and self.main.status(ST_LOGIN_COMPLETE):
            
            if self.main.username == UNSET_USERNAME \
               or not self.main.any_status(ST_LOGIN_SUCCESSFUL, ST_CONNECT):
                self.tray.set_tooltip(lang.tray_logged_out)
            
            elif self.mode == MODE_MESSAGES:
                self.tray.set_tooltip(lang.tray_logged_in % self.main.username,
                                      self.tweet.count, self.message.count)
            
            elif self.mode == MODE_TWEETS:
                self.tray.set_tooltip(lang.tray_logged_in % self.main.username,
                                      self.tweet.count, self.message.count)
        
        elif self.main.status(ST_CONNECT):
            self.tray.set_tooltip(lang.tray_logging_in % self.main.username,
                                  self.tweet.count, self.message.count)
        
        elif not view_mode \
             and not self.main.any_status(ST_NETWORK_FAILED, ST_LOGIN_ERROR):
            
            self.tray.set_tooltip(lang.tray_logged_out)
        
        # Set Tabs
        label = lang.tabs_tweets_new % self.tweet.count \
                if self.tweet.count > 0 else lang.tabs_tweets
        
        self.tab_tweets.set_label('<b>%s</b>' % label \
                                  if self.mode == MODE_TWEETS else label)
        
        label = lang.tabs_messages_new % self.message.count \
                if self.message.count > 0 else lang.tabs_messages
        
        self.tab_messages.set_label('<b>%s</b>' % label \
                                    if self.mode == MODE_MESSAGES else label)
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_mode(self, mode):
        if mode == self.mode:
            return False
        
        if mode is None:
            self.mode = MODE_TWEETS
        
        else:
            self.mode = mode
        
        if self.mode == MODE_MESSAGES:
            self.main.stop_profile(True)
            self.tabs.set_current_page(1)
            self.on_mode()
        
        elif self.mode == MODE_TWEETS:
            self.main.stop_profile(True)
            self.tabs.set_current_page(0)
            self.on_mode()
        
        elif self.mode == MODE_PROFILE:
            self.on_mode()
    
    def is_ready(self):
        return not self.main.status(ST_UPDATE) and self.load_state()
    
    def load_state(self):
        return self.message.load_state == HTML_LOADED \
               and self.tweet.load_state == HTML_LOADED
    
    def get_view_height(self):
        if self.mode == MODE_TWEETS:
            view = self.tweet
        
        elif self.mode == MODE_MESSAGES:
            view = self.message
        
        elif self.mode == MODE_PROFILE:
            view = self.profile
        
        size = view.get_allocation()
        return size[3] - size[0]
    
    
    # Visible helpers ----------------------------------------------------------
    def get_normalized_position(self):
        screen = self.get_screen()
        pos = self.get_position()
        return (pos[0] % screen.get_width(), pos[1] % screen.get_height())
    
    def on_screen(self):
        screen = self.get_screen()
        size = self.size_request()
        position = self.get_position()
        if position[0] < 0 - size[0] or position[0] > screen.get_width() \
           or position[1] < 0 - size[1] or position[1] > screen.get_height():
            
            return False
        
        else:
            return True
    
    def show_in_taskbar(self, mode):
        self.settings['taskbar'] = mode
        self.set_property('skip-taskbar-hint', not mode)
    
    def notifcation(self, typ, msg):
        if self.settings.is_true('notify'):
            typ = 'dialog-error' if typ == MESSAGE_ERROR else 'dialog-warning'
            self.main.notifier.add(('Atarashii', strip_tags(msg),
                                     typ, 'theme:' + typ))
    
    def multi_border(self, mode):
        base_color = self.get_style().bg[gtk.STATE_NORMAL]
        if not mode:
            self.multi_container.modify_bg(gtk.STATE_NORMAL, base_color)
            return False
        
        # Crazy color blending!
        col1 = base_color.to_string()[1:]
        col2 = self.tweet.get_style().dark[gtk.STATE_NORMAL].to_string()[1:]
        col1 = (col1[0:4], col1[4:8], col1[8:12])
        col2 = (col2[0:4], col2[4:8], col2[8:12])
        col3 = [0, 0, 0]
        
        # Aplhablend the two colors since there is no way to get the lighter
        # border color of the scrollbar
        for i in xrange(3):
            col3[i] = int(int((1 - 0.5) * int(col2[i], 16) \
                                          + 0.5 * int(col1[i], 16)))
        
        col = '#' + UNSET_STRING.join([hex(i)[2:] for i in col3])
        self.multi_container.modify_bg(gtk.STATE_NORMAL,
                                       gtk.gdk.color_parse(col))
    
    def fix_tabs_height(self):
        if self.mode == MODE_MESSAGES:
            tab_height = self.tab_messages.get_allocation()[3]
        
        else:
            tab_height = self.tab_tweets.get_allocation()[3]
        
        self.tabs.set_size_request(-1, tab_height + 9)
    
    
    # Hacked Helpers -----------------------------------------------------------
    def force_present(self):
        pos = self.get_normalized_position()
        self.move(pos[0], pos[1])
        
        # Try to focus the window... this fails fairly often...
        screen = self.get_screen()
        for i in screen.get_toplevel_windows():
            i.focus(False)
        
        self.get_window().raise_()
        self.present()
        self.get_window().focus(True)
        self.activate_tries = 0
        gobject.timeout_add(5, self.check_active)
    
    def check_active(self):
        if not self.is_active():
            self.activate_tries += 1
            self.get_window().raise_()
            self.present()
            self.get_window().focus(True)
            if self.activate_tries < 10:
                return True
    
    def fix_tooltips(self, *args):
        if self.mode == MODE_TWEETS:
            self.tweet.fake_move((-1.0, -1.0))
        
        elif self.mode == MODE_MESSAGES:
            self.message.fake_move((-1.0, -1.0))
        
        # TODO implement search
        else:
            pass
    
    def is_text_mode(self):
        if self.text.get_text().lstrip() != 'ohlookcolorfulrainbows!':
            return True
        
        toggled = self.settings.is_true('unicorns', False)
        self.settings['unicorns'] = not toggled
        self.main.user_picture_time_delta = UNSET_TIMEOUT
        self.main.updater.unwait(images=True)
        self.text.set_text(UNSET_TEXT)
        gobject.idle_add(self.text.unfocus)
        if not toggled:
            self.info_button.show('Oh look! Unicorns!', None, None, 5000)

