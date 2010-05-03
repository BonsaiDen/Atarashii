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


# Settings Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from dialog import Dialog
from settings_dialog_sub import SettingsPages, SettingsSaves
from lang import LANG as lang

from constants import UNSET_USERNAME, UNSET_COLUMN, FONT_SIZES, AVATAR_SIZES
from constants import ST_CONNECT, ST_LOGIN_COMPLETE


# This thing is most likely the worst part of Atarashii ------------------------
# At some point I'll need to spend a whole day cleaning this up ----------------
class SettingsDialog(Dialog, SettingsPages, SettingsSaves):
    resource = 'settings.glade'
    instance = None
    
    def __init__(self, parent):
        Dialog.__init__(self, parent, False, False, True)
        self.parent = parent
        self.blocked = False
        self.username_dialog = None
        self.question_dialog = None
        self.saved = False
        self.oldusername = self.main.username
        self.settings.check_autostart()
        self.dlg.set_title(lang.settings_title)
        
        # Tabs
        self.get('users').set_label(lang.settings_tab_accounts)
        self.get('general').set_label(lang.settings_tab_general)
        self.get('atarashii').set_label(lang.settings_tab_atarashii)
        self.get('syncing').set_label(lang.settings_tab_syncing)
        self.get('notifications').set_label(lang.settings_tab_notifications)
        self.get('theme').set_label(lang.settings_tab_theme)
        
        # Pages
        self.page_accounts(self.settings)
        self.page_atarashii(self.settings)
        self.page_syncing(self.settings)
        self.page_theme(self.settings)
        self.page_notify_sounds(self.settings)
        
        # Activate
        if (not self.main.status(ST_LOGIN_COMPLETE) \
           and self.main.username != UNSET_USERNAME) \
           or self.main.status(ST_CONNECT):
            
            self.activate(False)
        
        # Events
        self.close_button.set_label(lang.settings_button)
        self.close_button.connect('clicked', self.on_save)
        
        cancel_button = self.get('cancelbutton')
        cancel_button.set_label(lang.settings_button_cancel)
        cancel_button.connect('clicked', self.on_close)
        gobject.idle_add(self.accounts.grab_focus)
        self.dlg.set_size_request(-1, -1)
    
    def on_save(self, *args):
        if not self.save_syncing(self.settings):
            return False
        
        
        self.save_atarashii(self.settings)
        self.save_theme(self.settings)
        self.save_notify_sounds(self.settings)
        self.saved = True
        self.main.save_mode()
        self.settings.css()
        
        # Save Settings
        self.main.save_settings(False)
        self.gui.tray.update_account_menu()
        self.on_close()
    
    def on_close(self, *args):
        if self.blocked:
            return False
        
        if self.file_chooser is not None:
            self.file_chooser.close()
        
        if not self.saved:
            if self.get_active_account() == -1 \
               or not self.oldusername in self.settings.get_accounts():
                
                self.main.logout()
            
            if FONT_SIZES[self.fonts.get_active()] != self.old_font_size \
               or AVATAR_SIZES[self.avatars.get_active()] \
                  != self.old_avatar_size \
               or self.color_ids[self.themes.get_active()] \
                  != self.old_color_theme:
                
                self.settings.css()
                gobject.idle_add(self.gui.tweet.update_css)
                gobject.idle_add(self.gui.message.update_css)
                gobject.idle_add(self.gui.profile.update_css)
        
        self.__class__.instance = None
        self.gui.settings_dialog = None
        self.dlg.hide()
    
    
    # Helpers ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def activate(self, mode):
        if self.accounts is not None:
            self.accounts.set_sensitive(mode)
            self.add.set_sensitive(mode)
            if mode:
                self.account_changed()
            
            else:
                self.edit.set_sensitive(mode)
                self.delete.set_sensitive(mode)
    
    def unblock(self):
        self.blocked = False
    
    def hideall(self, sub_only=False):
        if not sub_only:
            self.gui.settings_dialog = None
            self.dlg.hide()
            if self.file_chooser is not None:
                self.file_chooser.close()
        
        if self.username_dialog is not None:
            self.username_dialog.on_close()
        
        if self.question_dialog is not None:
            self.blocked = False
            self.question_dialog.destroy()
            self.question_dialog = None
    
    def update_css(self, *args):
        self.settings.css(FONT_SIZES[self.fonts.get_active()],
                          AVATAR_SIZES[self.avatars.get_active()],
                          self.color_ids[self.themes.get_active()])
        
        gobject.idle_add(self.gui.tweet.update_css)
        gobject.idle_add(self.gui.message.update_css)
        gobject.idle_add(self.gui.profile.update_css)
    
    def create_boxlist(self, item, values, default, callback=None):
        item = self.get(item)
        item_list = gtk.ListStore(str)
        cell = gtk.CellRendererText()
        item.pack_start(cell, True)
        item.add_attribute(cell, 'text', 0)
        item.set_model(item_list)
        
        if not default in values:
            values.append(default)
            values.sort()
        
        for i, k in enumerate(values):
            item_list.append((k,))
            if k == default:
                item.set_active(i)
        
        if callback is not None:
            item.connect('changed', callback)
        
        return item
    
    
    # Users --------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def get_active_account(self):
        i = self.accounts.get_selection().get_selected_rows()[1]
        if i is None or len(i) == 0:
            return -1
        
        return i[0][0]
    
    def select_account(self, num):
        self.accounts.get_selection().select_path((num,))
        self.account_changed()
    
    def create_account_list(self, name=None):
        self.user_accounts = self.settings.get_accounts()
        self.accounts_list = gtk.ListStore(str, str, str, str)
        selected = -1
        for num, user in enumerate(self.user_accounts):
            self.accounts_list.append(self.get_account_entry(user))
            if user == name:
                selected = num
            
            elif name is None and user == self.main.username:
                selected = num
                
            elif self.main.username == UNSET_USERNAME and selected == -1:
                selected = num
        
        self.accounts.set_model(self.accounts_list)
        if selected != -1:
            self.select_account(selected)
        
        else:
            self.account_changed()
    
    def get_account_entry(self, name):
        tweets = self.settings['count_tweets_' + name]
        follower = self.settings['count_followers_' + name]
        following = self.settings['count_friends_' + name]
        
        if str(tweets) in ('', 'None'):
            tweets = UNSET_COLUMN
        
        if str(follower) in ('', 'None'):
            follower = UNSET_COLUMN
        
        if str(following) in ('', 'None'):
            following = UNSET_COLUMN
        
        return [name, str(tweets), str(follower), str(following)]
    
     # Setup Account List
    def account_changed(self, *args):
        i = self.get_active_account()
        self.edit.set_sensitive(i != -1)
        self.delete.set_sensitive(i != -1)
    
    
    # Editing ------------------------------------------------------------------
    def edit_account(self, username):
        name = self.user_accounts[self.get_active_account()]
        if name != username:
            ft_tmp = self.settings['firsttweet_' + name]
            lt_tmp = self.settings['lasttweet_' + name]
            fm_tmp = self.settings['firstmessage_' + name]
            lm_tmp = self.settings['lastmessage_' + name]
            lo_tmp = self.settings['mode_' + name]
            
            at_tmp = self.settings['count_tweets_' + name]
            af_tmp = self.settings['count_followers_' + name]
            ag_tmp = self.settings['count_friends_' + name]
            
            del self.settings['mode_' + name]
            del self.settings['account_' + name]
            del self.settings['firsttweet_' + name]
            del self.settings['lasttweet_' + name]
            del self.settings['firstmessage_' + name]
            del self.settings['lastmessage_' + name]
            del self.settings['xkey_' + name]
            del self.settings['xsecret_' + name]
            del self.settings['count_tweets_' + name]
            del self.settings['count_followers_' + name]
            del self.settings['count_friends_' + name]
            
            self.settings['mode_' + username] = lo_tmp
            self.settings['account_' + username] = UNSET_USERNAME
            self.settings['firsttweet_' + username] = ft_tmp
            self.settings['lasttweet_' + username] = lt_tmp
            self.settings['firstmessage_' + username] = fm_tmp
            self.settings['lastmessage_' + username] = lm_tmp
            self.settings['count_tweets_' + username] = at_tmp
            self.settings['count_followers_' + username] = af_tmp
            self.settings['count_friends_' + username] = ag_tmp
            
            # Edit active account?
            if self.main.username == name:
                self.main.username = username
                self.main.syncer.reset()
                self.main.logout()
            
            # update menu
            self.main.gui.tray.update_account_menu()
            self.settings.save()
            self.create_account_list(username)
    
    
    # Create -------------------------------------------------------------------
    def create_account(self, username):
        self.settings['account_' + username] = UNSET_USERNAME
        
        # update menu
        self.main.gui.tray.update_account_menu()
        self.settings.save()
        self.create_account_list(username)
        if len(self.user_accounts) == 1:
            self.select_account(0)
    
    
    # Delete -------------------------------------------------------------------
    def delete_account(self):
        self.blocked = False
        name = self.user_accounts[self.get_active_account()]
        del self.settings['mode_' + name]
        del self.settings['account_' + name]
        del self.settings['firsttweet_' + name]
        del self.settings['lasttweet_' + name]
        del self.settings['firstmessage_' + name]
        del self.settings['lastmessage_' + name]
        del self.settings['xkey_' + name]
        del self.settings['xsecret_' + name]
        del self.settings['count_tweets_' + name]
        del self.settings['count_followers_' + name]
        del self.settings['count_friends_' + name]
        
        self.settings.delete_userlist(name)
        
        # Delete active account?
        if self.main.username == name:
            self.main.username = UNSET_USERNAME
            self.main.logout()
        
        # update menu
        self.main.gui.tray.update_account_menu()
        self.settings.save()
        self.create_account_list()

