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
import gtk
import gobject

import dialog
import settings_dialog
from lang import LANG as lang

from constants import ST_UPDATE
from constants import MODE_MESSAGES, MODE_TWEETS, HTML_LOADING, HTML_LOADED, \
                      BUTTON_REFRESH, BUTTON_HISTORY, MODE_PROFILE


class GUIEventHandler(object):
    def delete_event(self, widget, event, data=None):
        self.window_position = self.get_position()
        self.settings['position'] = str(self.window_position)
        self.hide()
        return True
    
    def destroy_event(self, widget, data=None):
        self.window_position = self.get_position()
        self.settings['position'] = str(self.window_position)
        self.hide()
        return True
    
    def state_event(self, window, event):
        if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
            self.minimized = event.new_window_state & \
                                   gtk.gdk.WINDOW_STATE_ICONIFIED
    
    
    # Handlers -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_multi_move(self, button, event, mode=False):
        self.is_on_multi_button = False
        color = self.tabs.get_style().light[gtk.STATE_NORMAL] if mode \
                else self.get_style().bg[gtk.STATE_NORMAL]
        
        self.multi_button.modify_bg(gtk.STATE_NORMAL, color)
        self.multi_button.modify_bg(gtk.STATE_INSENSITIVE, color)
        self.multi_border(mode)
    
    def on_multi_press(self, button, event):
        self.is_on_multi_button = True
        self.multi_button.modify_bg(gtk.STATE_NORMAL,
                          self.multi_button.get_style().bg[gtk.STATE_ACTIVE])
    
    def on_multi_release(self, button, event):
        self.multi_button.modify_bg(gtk.STATE_NORMAL,
                          self.tabs.get_style().bg[gtk.STATE_NORMAL])
        
        if self.is_on_multi_button and not self.main.status(ST_UPDATE):
            self.is_on_multi_button = False
            if self.multi_state == BUTTON_REFRESH:
                self.on_refresh()
            
            elif self.multi_state == BUTTON_HISTORY:
                self.on_history()
            
            else:
                self.on_read()
    
    def on_refresh(self, *args):
        self.set_multi_button(False, status = False)
        if self.mode == MODE_MESSAGES:
            self.main.updater.unwait(messages = True)
        
        elif self.mode == MODE_TWEETS:
            self.main.updater.unwait(tweets = True)
    
    def on_refresh_all(self, button, menu=None):
        self.set_multi_button(False, status = False)
        self.main.updater.unwait(tweets = True, messages = True)
    
    def on_history(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(self.message.clear)
        
        else:
            gobject.idle_add(self.tweet.clear)
    
    def on_read(self, *args):
        if self.mode == MODE_MESSAGES:
            gobject.idle_add(self.message.read)
        
        else:
            gobject.idle_add(self.tweet.read)
    
    def on_read_all(self, *args):
        gobject.idle_add(self.message.read)
        gobject.idle_add(self.tweet.read)
    
    def on_tabs(self, tabs, page, page_num):
        if page_num == 0 and self.mode != MODE_TWEETS:
            self.set_mode(MODE_TWEETS)
        
        elif page_num == 1 and self.mode != MODE_MESSAGES:
            self.set_mode(MODE_MESSAGES)
        
        elif page_num == 2 and self.mode != MODE_PROFILE:
            self.set_mode(MODE_PROFILE)
    
    def on_mode(self, no_check=False, from_profile=False):
        if self.mode == MODE_MESSAGES:
            self.tabs.set_current_page(1)
            self.tweet_scroll.hide()
            self.profile_scroll.hide()
            self.message_scroll.show()
            if not from_profile:
                self.text.has_typed = False
            
            else:
                if self.text.has_typed:
                    self.text.grab_focus()
                
                self.text.check_typing()
            
            self.message.focus_me()
            self.message.fix_scroll()
            self.set_multi_button(True)
            
            if self.message.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.message.load_state == HTML_LOADED:
                self.show_input()
        
        elif self.mode == MODE_TWEETS:
            self.tabs.set_current_page(0)
            self.message_scroll.hide()
            self.profile_scroll.hide()
            self.tweet_scroll.show()
            if not from_profile:
                self.text.has_typed = False
            
            else:
                if self.text.has_typed:
                    self.text.grab_focus()
                
                self.text.check_typing()
            
            self.tweet.focus_me()
            self.tweet.fix_scroll()
            self.set_multi_button(True)
            
            if self.tweet.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.tweet.load_state == HTML_LOADED:
                self.show_input()
        
        elif self.mode == MODE_PROFILE:
            self.tabsbox.hide()
            self.message_scroll.hide()
            self.profile_scroll.show()
            self.tweet_scroll.hide()
            self.profile.focus_me()
            self.profile.check_scroll(0.0)
            self.set_multi_button(False)
            self.tabs.set_sensitive(False)
            no_check = True
            if self.profile.load_state == HTML_LOADING:
                self.profile.start()
                self.show_progress()
                self.progress_init(3, [lang.progress_user,
                                      lang.progress_status,
                                      lang.progress_tweets])
            
            elif self.profile.load_state == HTML_LOADED:
                self.profile.render()
                self.show_input()
        
        # TODO implement search here
        else:
            pass
        
        self.update_app()
        if not no_check:
            self.text.check_mode()
            self.text.loose_focus()
        
        if self.is_shown and not MODE_PROFILE and not from_profile:
            self.main.save_settings(True)
    
    def on_settings(self, button, menu):
        if menu and not self.settings_dialog:
            self.settings_dialog = settings_dialog.SettingsDialog(self)
        
        elif menu and self.settings_dialog:
            self.settings_dialog.on_close()
    
    def on_about(self, button, menu):
        if menu and not self.about_dialog:
            self.about_dialog = dialog.AboutDialog(self)
        
        elif menu and self.about_dialog:
            self.about_dialog.on_close()
    
    def on_quit(self, widget=None, data=None):
        if data:
            data.set_visible(False)
        
        self.main.quit()

