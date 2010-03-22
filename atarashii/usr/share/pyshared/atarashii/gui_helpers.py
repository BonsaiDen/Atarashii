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


# GUI / Events -----------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')

from utils import escape

from language import LANG as lang

from constants import ST_SEND, ST_CONNECT, ST_LOGIN_SUCCESSFUL, \
                      ST_LOGIN_COMPLETE, ST_UPDATE

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_LOADED, UNSET_TEXT, \
                      UNSET_LABEL

class GUIHelpers:
    def __init__(self):
        pass
    
    # Info Label ---------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_label(self):
        if self.main.status(ST_SEND):
            return
        
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
    
    def set_label_text(self, info, label_text, label_extra = None):
        if label_extra:
            self.info_label.set_markup(info \
                                       % (escape(label_text),
                                          escape(label_extra)))
        
        else:
            self.info_label.set_markup(info % escape(label_text))
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_app_title(self):
        if self.main.username == UNSET_TEXT \
           or (not self.main.status(ST_LOGIN_SUCCESSFUL) \
           and not self.main.status(ST_CONNECT)):
            self.set_title(lang.title)
        
        elif self.mode == MODE_MESSAGES:
            if self.html.count > 0:
                self.set_title((lang.title_tweets if self.html.count > 1 \
                                else lang.title_tweet) % self.html.count)
            
            else:
                self.set_title(lang.title_logged_in % self.main.username)
        
        elif self.mode == MODE_TWEETS:
            if self.message.count > 0:
                self.set_title((lang.title_messages if self.html.count > 1 \
                                else lang.title_message) % self.message.count)
            
            else:
                self.set_title(lang.title_logged_in % self.main.username)
        
        # Tray Tooltip
        if not self.main.status(ST_CONNECT) \
           and self.main.status(ST_LOGIN_COMPLETE):
           
            if self.main.username == UNSET_TEXT \
               or (not self.main.status(ST_LOGIN_SUCCESSFUL) \
               and not self.main.status(ST_CONNECT)):
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
        return self.message.load_state == HTML_LOADED \
               and self.html.load_state == HTML_LOADED
    
    def show_in_taskbar(self, mode):
        self.main.settings['taskbar'] = mode
        self.set_property('skip-taskbar-hint', not mode)

    # Fix tooltips that would stay on screen when switching workspaces
    # This doesn't work 100% of the time, but it's better than nothing
    def fix_tooltips(self, *args):
        if self.mode == MODE_TWEETS:
            self.html.fake_move((-1.0, -1.0), True)
         
        elif self.mode == MODE_MESSAGES:
            self.message.fake_move((-1.0, -1.0), True)
        
        else: # TODO implement search
            pass

