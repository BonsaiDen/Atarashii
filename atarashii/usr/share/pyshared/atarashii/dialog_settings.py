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

import os

from dialog import Dialog, MessageDialog
from sounds import THEME_SOUNDS, THEME_DIR
from utils import URLShorter, URLExpander
from lang import lang

from constants import UNSET_USERNAME, UNSET_SOUND, UNSET_SETTING, SYNC_KEY_CHARS
from constants import ST_CONNECT, ST_LOGIN_COMPLETE
from constants import MESSAGE_QUESTION, MESSAGE_ERROR
from constants import SHORTS_LIST, USERNAME_CHARS, FONT_DEFAULT, FONT_SIZES, \
                      AVATAR_DEFAULT, AVATAR_SIZES, THEME_DEFAULT, CONTINUE_LIST


# This thing is most likely the worst part of Atarashii ------------------------
# At some point I'll need to spend a whole day cleaning this up ----------------
class SettingsDialog(Dialog):
    resource = 'settings.glade'
    instance = None
    
    def activate(self, mode):
        if self.drop is not None:
            self.drop.set_sensitive(mode)
            self.add.set_sensitive(mode)
            if mode:
                self.drop_changed()
            
            else:
                self.edit.set_sensitive(mode)
                self.delete.set_sensitive(mode)
    
    def __init__(self, parent):
        Dialog.__init__(self, parent, False, False)
        self.dlg.set_transient_for(parent)
        self.parent = parent
        self.blocked = False
        self.username_dialog = None
        
        # Check for autostart
        self.main.settings.check_autostart()
        
        # Stuff
        self.saved = False
        self.dlg.set_title(lang.settings_title)
        self.close_button.set_label(lang.settings_button)
        cancel_button = self.get('cancelbutton')
        cancel_button.set_label(lang.settings_buttonCancel)
        
        # Tabs
        self.get('users').set_label(lang.settings_tab_accounts)
        self.get('general').set_label(lang.settings_tab_general)
        self.get('atarashii').set_label(lang.settings_tab_atarashii)
        self.get('syncing').set_label(lang.settings_tab_syncing)
        self.get('notifications').set_label(lang.settings_tab_notifications)
        self.get('theme').set_label(lang.settings_tab_theme)
        
        
        # Accounts -------------------------------------------------------------
        self.add = add = self.get('add')
        add.set_label(lang.settings_add)
        self.edit = edit = self.get('edit')
        edit.set_label(lang.settings_edit)
        self.delete = delete = self.get('delete')
        delete.set_label(lang.settings_delete)
        
        # Listview
        self.user_accounts = []
        self.accounts_list = None
        self.drop = drop = gtk.TreeView()
        drop.get_selection().set_mode(gtk.SELECTION_BROWSE)
        column = gtk.TreeViewColumn('')
        drop.set_headers_visible(False)
        drop.append_column(column)
        cell = gtk.CellRendererText()
        column.pack_start(cell, True)
        column.add_attribute(cell, 'text', 0)
        self.get('treewindow').add(drop)
        drop.show()
        drop.connect('cursor-changed', self.drop_changed)
        self.create_drop_list()
        self.drop_changed()
        
        # Edit Action
        def edit_dialog(*args):
            self.blocked = True
            name = self.user_accounts[self.get_drop_active()]
            AccountDialog(self, name, lang.account_edit, self.edit_account)
        
        edit.connect('clicked', edit_dialog)
        
        # Add Action
        def create_dialog(*args):
            self.blocked = True
            AccountDialog(self, '', lang.account_create, self.create_account)
        
        add.connect('clicked', create_dialog)
        
        # Delete Action
        def delete_dialog(*args):
            self.blocked = True
            name = self.user_accounts[self.get_drop_active()]
            MessageDialog(self.dlg, MESSAGE_QUESTION,
                            lang.account_delete_description % name,
                            lang.account_delete,
                            yes_callback = self.delete_account,
                            no_callback = self.unblock)
        
        delete.connect('clicked', delete_dialog)
        
        
        # Syncing --------------------------------------------------------------
        def sync_toggle(*args):
            self.sync_editbox.set_property('visible', True)
            self.sync_entrybox.set_property('visible', False)
            self.get('syncoptions').set_sensitive(self.sync_box.get_active())
        
        self.sync_desc = self.get('syncdesc')
        self.sync_box = self.get('syncbox')
        self.sync_box.set_label(lang.sync_checkbutton)
        self.sync_box.connect('toggled', sync_toggle)
        self.sync_change = self.get('syncbuttonchange')
        self.sync_entry = self.get('syncentry')
        self.sync_new = self.get('syncbuttonnew')
        self.sync_ok = self.get('syncbuttonok')
        self.sync_cancel = self.get('syncbuttoncancel')
        self.sync_editbox = self.get('synceditbox')
        self.sync_entrybox = self.get('syncentrybox')
        
        self.get('syncenterlabel').set_label(lang.sync_key_enter)
        self.sync_new.set_label(lang.sync_new)
        self.sync_change.set_label(lang.sync_change)
        self.sync_ok.set_label(lang.sync_ok)
        self.sync_cancel.set_label(lang.sync_cancel)
        self.sync_key_user_set = False
        self.sync_box.set_active(self.settings.is_true('syncing', False))
        sync_toggle()
        
        self.sync_box.set_sensitive(False)
        self.get('syncoptions').set_sensitive(False)
        
        self.sync_label = self.get('synclabel')
        self.sync_desc.set_label(lang.sync_key_loading)
        self.sync_label.set_label('')
        
        # Setup syncing GUI
        def init_sync():
            if not self.main.syncer.get_key():
                self.syncing_key = None
                if self.settings.is_true('syncing', False):
                    self.sync_desc.set_label(lang.sync_key_error)
                    self.sync_label.set_label(lang.sync_key_failed)
                    self.sync_box.set_sensitive(True)
                    
                    self.get('syncoptions').set_sensitive(False)
                    self.get('tabs').set_current_page(1)
                    self.get('general_tabs').set_current_page(1)
                
                else:
                    self.sync_desc.set_label(lang.sync_key_no)
                    self.sync_label.set_label('')
                    self.get('syncoptions').set_sensitive(True)
                    self.sync_box.set_sensitive(True)
                
                sync_toggle()
                self.settings['syncing'] = False
                self.sync_box.set_active(False)
            
            else:
                self.get('syncoptions').set_sensitive(True)
                self.sync_box.set_sensitive(True)
                self.syncing_key = self.settings['synckey']
                self.sync_desc.set_label(lang.sync_key_current)
                self.sync_label.set_label(lang.sync_key_label \
                                         % self.syncing_key)
        
        gobject.timeout_add(100, init_sync)
        
        def pre_retrieve_key(*args):
            self.dlg.set_sensitive(False)
            self.dlg.queue_draw()
            gobject.idle_add(retrieve_key)
        
        def retrieve_key():
            key = self.main.syncer.retrieve_new_key()
            if key is not None:
                self.syncing_key = key
                self.sync_desc.set_label(lang.sync_key_current)
                self.sync_label.set_label(lang.sync_key_label \
                                         % self.syncing_key)
                
                self.sync_desc.set_label(lang.sync_key_changed)
                self.sync_key_user_set = False
                self.sync_change.set_sensitive(True)
            
            else:
                self.sync_desc.set_label(lang.sync_key_error)
                self.sync_label.set_label(lang.sync_key_failed)
            
            self.sync_new.set_sensitive(False)
            self.dlg.set_sensitive(True)
        
        self.sync_new.connect('clicked', pre_retrieve_key)
        
        def sync_change(*args):
            self.sync_editbox.set_property('visible', False)
            self.sync_entrybox.set_property('visible', True)
            self.sync_entry.set_text(self.syncing_key)
        
        def sync_cancel_key(*args):
            self.sync_editbox.set_property('visible', True)
            self.sync_entrybox.set_property('visible', False)
        
        def sync_ok_key(*args):
            key = self.sync_entry.get_text().strip()
            if len(key) != 22:
                return False
            
            if key != self.settings['synckey']:
                self.sync_desc.set_label(lang.sync_key_changed)
                self.sync_key_user_set = True
            
            elif key == self.settings['synckey']:
                self.sync_desc.set_label(lang.sync_key_current)
                self.sync_key_user_set = False
            
            self.syncing_key = key
            self.sync_label.set_label(lang.sync_key_label \
                                      % self.syncing_key)
            
            self.sync_editbox.set_property('visible', True)
            self.sync_entrybox.set_property('visible', False)
        
        def sync_entry_change(*args):
            text = self.sync_entry.get_text().strip()
            text = (''.join([i for i in text if i in SYNC_KEY_CHARS]))
            self.sync_entry.set_text(text)
            if len(text) != 22:
                self.sync_entry.modify_base(gtk.STATE_NORMAL,
                                gtk.gdk.Color(255 * 255, 190 * 255, 190 * 255))
            
            else:
                self.sync_entry.modify_base(gtk.STATE_NORMAL,
                                            self.gui.text.default_bg)
        
        self.sync_entry.connect('changed', sync_entry_change)
        self.sync_change.connect('clicked', sync_change)
        self.sync_cancel.connect('clicked', sync_cancel_key)
        self.sync_ok.connect('clicked', sync_ok_key)
        
        
        # General --------------------------------------------------------------
        autostart = self.get('autostart')
        taskbar = self.get('taskbar')
        tray = self.get('tray')
        info_sound = self.get('infosound')
        
        autostart.set_label(lang.settings_autostart)
        taskbar.set_label(lang.settings_taskbar)
        tray.set_label(lang.settings_tray)
        info_sound.set_label(lang.settings_info_sound)
        
        autostart.set_active(self.settings.is_true('autostart', False))
        taskbar.set_active(self.settings.is_true('taskbar'))
        tray.set_active(self.settings.is_true('tray', False))
        info_sound.set_active(self.settings.is_true('infosound', True))
        
        
        # Soundfiles -----------------------------------------------------------
        self.get('snd_tweets').set_label(lang.settings_file_tweets)
        self.get('snd_reply').set_label(lang.settings_file_replies)
        self.get('snd_messages').set_label(lang.settings_file_messages)
        
        self.sounds = ['tweets', 'reply', 'messages']
        default_sound = THEME_SOUNDS.get('message-new-instant', UNSET_SOUND)
        
        def get_sound(key):
            if self.settings.isset('sound_' + key, True):
                snd = str(self.settings['sound_' + key]).strip()
                return None if snd in (UNSET_SETTING, 'None') else snd
            
            else:
                return default_sound
        
        soundfiles = {
            'tweets': self.settings.get('sound_tweets', default_sound),
            'reply': self.settings.get('sound_reply', default_sound),
            'messages': self.settings.get('sound_messages', default_sound)
        }
        
        def set_sound(snd, snd_file):
            self.get('file_' + snd).set_label(os.path.basename(snd_file))
            self.get('button_' + snd + '_del').set_sensitive(True)
            soundfiles[snd] = snd_file
        
        def del_sound(button, snd):
            self.get('file_' + snd).set_label(lang.settings_file_none)
            soundfiles[snd] = UNSET_SOUND
            button.set_sensitive(False)
        
        self.file_chooser = None
        
        def select_file(button, snd):
            self.file_chooser = SoundChooser(self)
            self.file_chooser.open_file(get_sound(snd), snd, set_sound)
        
        for snd in self.sounds:
            self.get('button_' + snd).connect('clicked', select_file, snd)
            del_button = self.get('button_' + snd + '_del')
            del_button.connect('clicked', del_sound, snd)
            snd_file = get_sound(snd)
            snd_file = os.path.basename(snd_file) if snd_file is not None \
                       else lang.settings_file_none
            
            del_button.set_sensitive(snd_file != lang.settings_file_none)
            self.get('file_' + snd).set_label(snd_file)
        
        
        # Notification ---------------------------------------------------------
        notify = self.get('notify')
        overlay = self.get('notify_overlay')
        sound = self.get('sound')
        notify.set_label(lang.settings_notifications_enable)
        overlay.set_label(lang.settings_notifications_overlay)
        sound.set_label(lang.settings_notifications_sound)
        
        notify.set_active(self.settings.is_true('notify'))
        overlay.set_active(self.settings.is_true('notify_overlay', True))
        sound.set_active(self.settings.is_true('sound'))
        notify.set_sensitive(True)
        
        def toggle2(*args):
            self.get('soundfiles').set_sensitive(sound.get_active())
        
        def toggle(*args):
            overlay.set_sensitive(notify.get_active())
            sound.set_sensitive(notify.get_active())
            self.get('soundfiles').set_sensitive(notify.get_active() \
                                                 and sound.get_active())
        
        toggle()
        notify.connect('toggled', toggle)
        sound.connect('toggled', toggle2)
        
        
        # Shortener ------------------------------------------------------------
        self.get('shortener').set_label(lang.settings_shortener)
        short_names = [lang.settings_shortener_off] + SHORTS_LIST
        short_selected = self.settings['shortener']
        if short_selected == 'off':
            short_selected = lang.settings_shortener_off
        
        shorts = self.create_boxlist('shorts', short_names, short_selected)
        
        
        # Continues ------------------------------------------------------------
        self.get('continue').set_label(lang.settings_continue)
        conts = zip(CONTINUE_LIST, lang.settings_continue_names)
        cont_names = ['%s (%s)' % (i, e) for i, e in conts]
        continues = self.create_boxlist('continues', cont_names,
                                        cont_names[self.settings['continue']])
        
        
        # Sizes ----------------------------------------------------------------
        self.get('fontsize').set_label(lang.settings_font_size)
        self.old_font_size = self.settings.get('fontsize', FONT_DEFAULT)
        self.fonts = self.create_boxlist('fontbox', FONT_SIZES,
                                    self.old_font_size,
                                    self.update_css)
        
        self.get('avatarsize').set_label(lang.settings_avatar_size)
        self.old_avatar_size = self.settings.get('avatarsize', AVATAR_DEFAULT)
        self.avatars = self.create_boxlist('avatarbox', AVATAR_SIZES,
                                           self.old_avatar_size,
                                           self.update_css)
        
        
        # Theme ----------------------------------------------------------------
        self.settings.load_color_themes()
        self.get('colortheme').set_label(lang.settings_color_theme)
        self.old_color_theme = self.settings.get('color_theme', THEME_DEFAULT)
        self.color_ids = sorted(self.settings.color_themes.keys())
        self.color_names = []
        for i in self.color_ids:
            key = 'title_' + lang.code
            name = self.settings.color_themes[i][key] \
                   if key in self.settings.color_themes[i] \
                   else self.settings.color_themes[i]['title_en']
            
            self.color_names.append(name)
        
        self.themes = self.create_boxlist('colorthemebox', self.color_names,
                self.color_names[self.color_ids.index(self.old_color_theme)],
                self.update_css)
        
        
        # Save -----------------------------------------------------------------
        self.oldusername = self.main.username
        
        def save(*args):
            if self.syncing_key is not None \
               and self.sync_box.get_active():
                
                # Check if this key exists if the user set it
                if self.settings['synckey'] != self.syncing_key:
                    if self.sync_key_user_set:
                        if not self.main.syncer.check_key(self.syncing_key):
                            MessageDialog(self.dlg, MESSAGE_ERROR,
                                          lang.sync_user_error,
                                          lang.sync_user_error_title)
                            
                            return False
                    
                    # Save key
                    self.settings['synckey'] = self.syncing_key
                    self.main.syncer.key = self.settings['synckey']
            
            # Save all settings
            if self.settings['synckey'] is not None:
                self.settings['syncing'] = self.sync_box.get_active()
            
            self.saved = True
            
            
            # Notifaction and Sounds -------------------------------------------
            for k, v in soundfiles.iteritems():
                self.settings['sound_' + k] = v
            
            self.settings['notify'] = notify.get_active()
            self.settings['notify_overlay'] = overlay.get_active()
            self.settings['sound'] = sound.get_active()
            self.settings['tray'] = tray.get_active()
            self.settings['infosound'] = info_sound.get_active()
            
            
            # Shortener --------------------------------------------------------
            old_short = self.settings['shortener']
            selected_short = shorts.get_active()
            if selected_short != 0:
                self.settings['shortener'] = SHORTS_LIST[selected_short - 1]
            
            else:
                self.settings['shortener'] = 'off'
            
            if old_short != self.settings['shortener']:
                URLShorter.reset()
                URLExpander.reset()
            
            
            # Continue ---------------------------------------------------------
            self.settings['continue'] = continues.get_active()
            
            
            # Themes -----------------------------------------------------------
            self.settings['fontsize'] = FONT_SIZES[self.fonts.get_active()]
            self.settings['avatarsize'] = AVATAR_SIZES[
                                          self.avatars.get_active()]
            
            self.settings['color_theme'] = self.color_ids[
                                           self.themes.get_active()]
            
            self.settings.set_autostart(autostart.get_active())
            self.gui.show_in_taskbar(taskbar.get_active())
            
            # Save GUI Mode
            self.main.save_mode()
            
            # Update CSS
            self.settings.css()
            
            # Set new Username
            if self.get_drop_active() == -1 \
               or not self.oldusername in self.main.settings.get_accounts():
                
                self.main.logout()
            
            # Save Settings
            self.main.save_settings(False)
            self.gui.tray.update_account_menu()
            self.on_close()
        
        if not self.main.status(ST_LOGIN_COMPLETE) \
           and self.main.username != UNSET_USERNAME:
            
            active = False
        
        elif self.main.status(ST_CONNECT):
            active = False
        
        else:
            active = True
        
        self.activate(active)
        
        self.close_button.connect('clicked', save)
        cancel_button.connect('clicked', self.on_close)
        gobject.idle_add(self.drop.grab_focus)
        self.dlg.set_size_request(-1, -1)
    
    def unblock(self):
        self.blocked = False
    
    def on_close(self, *args):
        if self.blocked:
            return False
        
        if self.file_chooser is not None:
            self.file_chooser.close()
        
        if not self.saved:
            if self.get_drop_active() == -1 \
               or not self.oldusername in self.main.settings.get_accounts():
                
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
    
    def hideall(self):
        self.dlg.hide()
        if self.file_chooser is not None:
            self.file_chooser.close()
        
        if self.username_dialog is not None:
            self.username_dialog.on_close()
    
    
    # CSS ----------------------------------------------------------------------
    def update_css(self, *args):
        self.settings.css(FONT_SIZES[self.fonts.get_active()],
                          AVATAR_SIZES[self.avatars.get_active()],
                          self.color_ids[self.themes.get_active()])
        
        gobject.idle_add(self.gui.tweet.update_css)
        gobject.idle_add(self.gui.message.update_css)
        gobject.idle_add(self.gui.profile.update_css)
    
    
    # Generate listboxes -------------------------------------------------------
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
    
    
    # Generate Account List ----------------------------------------------------
    def get_drop_active(self):
        i = self.drop.get_selection().get_selected_rows()[1]
        if i is None or len(i) == 0:
            return -1
        
        return i[0][0]
    
    def select_drop(self, num):
        self.drop.get_selection().select_path((num,))
        self.drop_changed()
    
    def create_drop_list(self, name=None):
        self.user_accounts = self.main.settings.get_accounts()
        self.accounts_list = gtk.ListStore(str)
        selected = -1
        for num, user in enumerate(self.user_accounts):
            self.accounts_list.append([user])
            if user == name:
                selected = num
            
            elif name is None and user == self.main.username:
                selected = num
        
        self.drop.set_model(self.accounts_list)
        if selected != -1:
            self.select_drop(selected)
        
        else:
            self.drop_changed()
    
     # Setup Account List
    def drop_changed(self, *args):
        i = self.get_drop_active()
        self.edit.set_sensitive(i != -1)
        self.delete.set_sensitive(i != -1)
    
    
    # Edit a User Account ------------------------------------------------------
    def edit_account(self, username):
        name = self.user_accounts[self.get_drop_active()]
        if name != username:
            ft_tmp = self.main.settings['firsttweet_' + name]
            lt_tmp = self.main.settings['lasttweet_' + name]
            fm_tmp = self.main.settings['firstmessage_' + name]
            lm_tmp = self.main.settings['lastmessage_' + name]
            lo_tmp = self.main.settings['mode_' + name]
            
            del self.main.settings['mode_' + name]
            del self.main.settings['account_' + name]
            del self.main.settings['firsttweet_' + name]
            del self.main.settings['lasttweet_' + name]
            del self.main.settings['firstmessage_' + name]
            del self.main.settings['lastmessage_' + name]
            del self.main.settings['xkey_' + name]
            del self.main.settings['xsecret_' + name]
            
            self.main.settings['mode_' + username] = lo_tmp
            self.main.settings['account_' + username] = UNSET_USERNAME
            self.main.settings['firsttweet_' + username] = ft_tmp
            self.main.settings['lasttweet_' + username] = lt_tmp
            self.main.settings['firstmessage_' + username] = fm_tmp
            self.main.settings['lastmessage_' + username] = lm_tmp
            
            # Edit active account?
            if self.main.username == name:
                self.main.username = username
                self.main.syncer.reset()
                self.main.logout()
            
            # update menu
            self.main.gui.tray.update_account_menu()
            self.main.settings.save()
            self.create_drop_list(username)
    
    def create_account(self, username):
        self.main.settings['account_' + username] = UNSET_USERNAME
        
        # update menu
        self.main.gui.tray.update_account_menu()
        self.main.settings.save()
        self.create_drop_list()
        if len(self.user_accounts) == 1:
            self.select_drop(0)
    
    def delete_account(self):
        self.blocked = False
        name = self.user_accounts[self.get_drop_active()]
        del self.main.settings['mode_' + name]
        del self.main.settings['account_' + name]
        del self.main.settings['firsttweet_' + name]
        del self.main.settings['lasttweet_' + name]
        del self.main.settings['firstmessage_' + name]
        del self.main.settings['lastmessage_' + name]
        del self.main.settings['xkey_' + name]
        del self.main.settings['xsecret_' + name]
        
        # Delete active account?
        if self.main.username == name:
            self.main.username = UNSET_USERNAME
            self.main.logout()
        
        # update menu
        self.main.gui.tray.update_account_menu()
        self.main.settings.save()
        self.create_drop_list()


# Sound File Chooser -----------------------------------------------------------
# ------------------------------------------------------------------------------
class SoundChooser(object):
    def __init__(self, parent):
        self.parent = parent
        self.parent.blocked = True
        self.chooser = gtk.FileChooserDialog(None, parent.dlg,
                           action = gtk.FILE_CHOOSER_ACTION_OPEN,
                           buttons = (lang.settings_file_cancel,
                           gtk.RESPONSE_CANCEL,
                           lang.settings_file_ok,
                           gtk.RESPONSE_OK))
        
        self.chooser.set_modal(True)
        self.chooser.connect('response', self.choosen)
        self.chooser.set_title(lang.settings_file)
        self.chooser.connect('selection-changed', self.select_file)
        
        # File Filter
        self.filter = gtk.FileFilter()
        self.filter.set_name(lang.settings_file_filter \
                             + '(*.wav, *.ogg, *.flac)')
        
        self.filter.add_pattern('*.flac')
        self.filter.add_pattern('*.wav')
        self.filter.add_pattern('*.ogg')
        self.chooser.add_filter(self.filter)
        self.chooser.set_filter(self.filter)
    
    def close(self):
        self.parent.blocked = False
        self.chooser.destroy()
    
    def choosen(self, chooser, code):
        if code == gtk.RESPONSE_OK:
            gobject.idle_add(self.select_callback, self.select_snd,
                             str(self.chooser.get_filename()))
        
        self.close()
    
    def open_file(self, current_file, select_snd, select_callback):
        self.select_snd = select_snd
        self.select_callback = select_callback
        if current_file is None:
            self.chooser.set_current_folder(THEME_DIR)
        
        else:
            self.chooser.set_filename(current_file)
        
        self.chooser.show()
    
    # Fix bug with the file filter no beeing selected
    def select_file(self, chooser):
        if self.chooser.get_filter() is None:
            self.chooser.set_filter(self.filter)


# Account Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class AccountDialog(Dialog):
    resource = 'account.glade'
    instance = None
    
    def __init__(self, parent, username, title, callback):
        Dialog.__init__(self, parent.gui, False)
        self.dlg.set_transient_for(parent.dlg)
        self.parent = parent
        self.parent.username_dialog = self
        self.callback = callback
        self.dlg.set_title(title)
        self.username = username
        self.user.set_text(username)
        self.user.grab_focus()
    
    def on_init(self):
        self.user = self.get('username')
        self.get('user').set_text(lang.account_username)
        self.user.connect('changed', self.on_changed)
        
        self.close_button.set_label(lang.account_button)
        cancel_button = self.get('cancelbutton')
        cancel_button.set_label(lang.account_button_cancel)
        
        def save(*args):
            username = self.user.get_text().strip()
            if username == UNSET_USERNAME:
                self.user.grab_focus()
            
            elif username in self.parent.user_accounts \
                 and username != self.username:
                
                self.user.grab_focus()
            
            else:
                self.callback(username)
                self.on_close()
        
        self.close_button.connect('clicked', save)
        cancel_button.connect('clicked', self.on_close)
    
    def on_changed(self, *args):
        text = self.user.get_text().strip()
        self.user.set_text(''.join([i for i in text if i in USERNAME_CHARS]))
    
    def on_close(self, *args):
        self.parent.username_dialog = None
        self.parent.blocked = False
        self.instance = None
        self.dlg.hide()

