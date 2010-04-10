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
from language import LANG as lang

from constants import ST_SEND, ST_CONNECT, ST_LOGIN_SUCCESSFUL, \
                      ST_LOGIN_COMPLETE, ST_UPDATE

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_LOADED, UNSET_TEXT, \
                      UNSET_LABEL, MESSAGE_ERROR, UNSET_USERNAME


class GUIHelpers(object):
    def set_label(self):
        if self.main.status(ST_SEND):
            return False
        
        # Unset
        if self.main.reply_user == UNSET_TEXT \
           and self.main.retweet_user == UNSET_TEXT \
           and self.main.message_user == UNSET_TEXT \
           and self.main.edit_text == UNSET_TEXT:
            
            self.info_label.set_markup(UNSET_LABEL)
            self.info_label.hide()
        
        # Edit
        elif self.main.edit_text != UNSET_TEXT:
            if self.main.edit_reply_user != UNSET_TEXT:
                self.set_label_text(lang.label_edit_reply,
                                    self.main.edit_reply_user,
                                    self.main.edit_text)
            
            else:
                self.set_label_text(lang.label_edit, self.main.edit_text)
            
            self.info_label.show()
        
        # RT
        elif self.main.retweet_user != UNSET_TEXT:
            self.set_label_text(lang.label_retweet, self.main.retweet_user)
            self.info_label.show()
        
        # Reply
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
    
    def set_label_text(self, info, label_text, label_extra=None):
        if label_extra:
            self.info_label.set_markup(info \
                                       % (escape(label_text),
                                          escape(label_extra)))
        
        else:
            self.info_label.set_markup(info % escape(label_text))
    
    # App Title ----------------------------------------------------------------
    def set_app_title(self):
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
                                      self.html.count, self.message.count)
            
            elif self.mode == MODE_TWEETS:
                self.tray.set_tooltip(lang.tray_logged_in % self.main.username,
                                      self.html.count, self.message.count)
        
        elif self.main.status(ST_CONNECT):
            self.tray.set_tooltip(lang.tray_logging_in % self.main.username)
        
        else:
            self.tray.set_tooltip(lang.tray_logged_out)
        
        # Set Tabs
        self.set_tabs()
    
    
    # Tabs ---------------------------------------------------------------------
    def set_tabs(self):
        label = lang.tabs_tweets_new % self.html.count \
                if self.html.count > 0 else lang.tabs_tweets
        
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
            self.tabs.set_current_page(1)
            self.on_mode()
        
        elif self.mode == MODE_TWEETS:
            self.tabs.set_current_page(0)
            self.on_mode()
    
    def is_ready(self):
        return not self.main.status(ST_UPDATE) and self.load_state()
    
    def load_state(self):
        return self.message.load_state == HTML_LOADED \
               and self.html.load_state == HTML_LOADED
    
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
    
    
    # Kitten HackAttack for presenting the window to the user ------------------
    # --------------------------------------------------------------------------
    def force_present(self):
        old_pos = self.get_position()
        pos = self.get_normalized_position()
        self.move(pos[0], pos[1])
        
        self.present()
        self.get_window().focus(True)
        self.activate_tries = 0
        gobject.timeout_add(5, self.check_active)

    def check_active(self):
        if not self.is_active():
            self.activate_tries += 1
            self.present()
            self.get_window().focus(True)
            if self.activate_tries < 10:
                return True
    
    # Fix tooltips that would stay on screen when switching workspaces
    # This doesn't work 100% of the time, but it's better than nothing
    # FIXME this is broken...
    def fix_tooltips(self, *args):
        if self.mode == MODE_TWEETS:
            self.html.fake_move((-1.0, -1.0))
        
        elif self.mode == MODE_MESSAGES:
            self.message.fake_move((-1.0, -1.0))
        
        # TODO implement search
        else:
            pass
    
    # Hack a border around the multi button
    def multi_border(self, mode):
        base_color = self.get_style().bg[gtk.STATE_NORMAL]
        if not mode:
            self.multi_container.modify_bg(gtk.STATE_NORMAL, base_color)
            return False
        
        # Crazy color blending!
        col1 = base_color.to_string()[1:]
        col2 = self.html.get_style().dark[gtk.STATE_NORMAL].to_string()[1:]
        col1 = (col1[0:4], col1[4:8], col1[8:12])
        col2 = (col2[0:4], col2[4:8], col2[8:12])
        col3 = [0, 0, 0]
        
        # Aplhalend the two colors since there is no way to get the lighter
        # border color of the scrollbar
        for i in xrange(3):
            col3[i] = int(int((1 - 0.5) * int(col2[i], 16) \
                                          + 0.5 * int(col1[i], 16)))
        
        col = gtk.gdk.color_parse('#' + ''.join([hex(i)[2:] for i in col3]))
        self.multi_container.modify_bg(gtk.STATE_NORMAL, col)
    
    # Toggle visibility of taskbar entry
    def show_in_taskbar(self, mode):
        self.main.settings['taskbar'] = mode
        self.set_property('skip-taskbar-hint', not mode)
    
    # Show a popup notification
    def notifcation(self, typ, msg):
        if self.main.settings.is_true('notify'):
            typ = 'dialog-error' if typ == MESSAGE_ERROR else 'dialog-warning'
            self.main.notifier.add(('Atarashii', strip_tags(msg),
                                     typ, 'theme:' + typ))

