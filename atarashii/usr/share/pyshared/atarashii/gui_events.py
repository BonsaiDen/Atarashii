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
import dialog_settings

from constants import MODE_MESSAGES, MODE_TWEETS, HTML_LOADING, HTML_LOADED, \
                      BUTTON_REFRESH, BUTTON_HISTORY


class GUIEventHandler:
    
    # Events -------------------------------------------------------------------
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
    
    
    # Handlers -----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_refresh(self, *args):
        self.set_refresh_update(False, status = False)
        if self.mode == MODE_MESSAGES:
            self.main.updater.unwait(messages = True)
        
        else:
            self.main.updater.unwait(tweets = True)
    
    def on_refresh_all(self, button, menu=None):
        self.set_refresh_update(False, status = False)
        self.main.updater.unwait(tweets = True, messages = True)
    
    def on_refresh_update(self, *args):
        if self.multi_state == BUTTON_REFRESH:
            self.on_refresh()
        
        elif self.multi_state == BUTTON_HISTORY:
            self.on_history()
        
        else:
            self.on_read()
    
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
            self.html_scroll.hide()
            self.message_scroll.show()
            self.message.focus_me()
            self.message.fix_scroll()
            self.set_refresh_update(True)
            
            if self.message.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.message.load_state == HTML_LOADED:
                self.show_input()
        
        elif self.mode == MODE_TWEETS:
            self.message_scroll.hide()
            self.html_scroll.show()
            self.html.focus_me()
            self.html.fix_scroll()
            self.set_refresh_update(True)
            
            if self.html.load_state == HTML_LOADING:
                self.show_progress()
            
            elif self.html.load_state == HTML_LOADED:
                self.show_input()
        
        else: # TODO implement search here
            pass
        
        self.set_app_title()
        self.text.check_mode()
        self.text.loose_focus()
        
        if self.is_shown:
            self.main.save_settings(True)
    
    def on_settings(self, button, menu):
        if not self.settings_toggle:
            self.settings_toggle = True
            if self.settings_button.get_active() and not self.settings_dialog:
                self.settings_dialog = dialog_settings.SettingsDialog(self)
            
            elif menu and not self.settings_dialog:
                self.settings_dialog = dialog_settings.SettingsDialog(self)
                self.settings_button.set_active(True)
            
            elif menu and self.settings_dialog:
                self.settings_dialog.on_close()
                self.settings_button.set_active(False)
            
            elif self.settings_dialog:
                self.settings_dialog.on_close()
            
            self.settings_toggle = False
    
    def on_about(self, button, menu):
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
    
    def on_quit(self, widget=None, data=None):
        if data:
            data.set_visible(False)
        
        self.main.quit()

