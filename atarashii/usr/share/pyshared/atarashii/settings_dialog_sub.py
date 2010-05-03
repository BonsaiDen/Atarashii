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


# Settings Dialog Pages and Savers ---------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import os

from dialog import MessageDialog
from settings_dialog_extra import AccountDialog, SoundChooser

from sounds import THEME_SOUNDS
from utils import URLShorter, URLExpander, filter_chars
from lang import LANG as lang

from constants import MESSAGE_QUESTION, MESSAGE_ERROR
from constants import SHORTS_LIST, CONTINUE_LIST, SYNC_KEY_CHARS
from constants import UNSET_SOUND, UNSET_SETTING, UNSET_LABEL, UNSET_USERNAME
from constants import FONT_DEFAULT, FONT_SIZES, AVATAR_DEFAULT, AVATAR_SIZES, \
                      THEME_DEFAULT


class SettingsSaves(object):
    def save_atarashii(self, settings):
        settings['infosound'] = self.info_sound.get_active()
        settings['continue'] = self.continues.get_active()
        settings['tray'] = self.tray.get_active()
        settings.set_autostart(self.autostart.get_active())
        self.gui.show_in_taskbar(self.taskbar.get_active())
        
        old_short = settings['shortener']
        selected_short = self.shorts.get_active()
        if selected_short != 0:
            settings['shortener'] = SHORTS_LIST[selected_short - 1]
        
        else:
            settings['shortener'] = 'off'
        
        if old_short != self.settings['shortener']:
            URLShorter.reset()
            URLExpander.reset()
    
    def save_syncing(self, settings):
        if self.syncing_key is not None and self.sync_box.get_active():
            
            # Check if this key exists if the user set it
            if settings['synckey'] != self.syncing_key:
                if self.sync_key_user_set:
                    if not self.main.syncer.check_key(self.syncing_key):
                        MessageDialog(self.dlg, MESSAGE_ERROR,
                                      lang.sync_user_error,
                                      lang.sync_user_error_title)
                        
                        return False
                
                # Save key
                settings['synckey'] = self.syncing_key
                self.main.syncer.key = settings['synckey']
        
        # Save all settings
        if settings['synckey'] is not None:
            settings['syncing'] = self.sync_box.get_active()
        
        return True
    
    def save_theme(self, settings):
        settings['fontsize'] = FONT_SIZES[self.fonts.get_active()]
        settings['avatarsize'] = AVATAR_SIZES[self.avatars.get_active()]
        settings['color_theme'] = self.color_ids[self.themes.get_active()]
    
    def save_notify_sounds(self, settings):
        for k, v in self.soundfiles.iteritems():
            settings['sound_' + k] = v
        
        settings['notify'] = self.notify.get_active()
        settings['notify_overlay'] = self.overlay.get_active()
        settings['notify_network'] = self.notify_network.get_active()
        settings['sound'] = self.sound.get_active()


class SettingsPages(object):
    def page_accounts(self, settings):
        self.add = self.get('add')
        self.add.set_label(lang.settings_add)
        self.edit = self.get('edit')
        self.edit.set_label(lang.settings_edit)
        self.delete = self.get('delete')
        self.delete.set_label(lang.settings_delete)
        
        # Listview
        self.user_accounts = []
        self.accounts_list = None
        
        # Setup box
        self.drop = drop = gtk.TreeView()
        drop.get_selection().set_mode(gtk.SELECTION_BROWSE)
        
        def column(title, pos, expand=False):
            column = gtk.TreeViewColumn(UNSET_LABEL)
            column.set_title(title)
            column.set_property('expand', expand)
            cell = gtk.CellRendererText()
            column.pack_start(cell, True)
            column.add_attribute(cell, 'text', pos)
            return column
        
        drop.append_column(column('Name', 0, True))
        drop.append_column(column('Tweets', 1))
        drop.append_column(column('Follower', 2))
        drop.append_column(column('Following', 3))
        self.get('treewindow').add(drop)
        drop.show()
        
        # Init contents
        drop.connect('cursor-changed', self.drop_changed)
        self.create_drop_list()
        self.drop_changed()
        
        # Edit Action
        def edit_dialog(*args):
            self.blocked = True
            name = self.user_accounts[self.get_drop_active()]
            AccountDialog(self, name, lang.account_edit, self.edit_account)
        
        self.edit.connect('clicked', edit_dialog)
        
        # Add Action
        def create_dialog(*args):
            self.blocked = True
            AccountDialog(self, UNSET_USERNAME, lang.account_create,
                          self.create_account)
        
        self.add.connect('clicked', create_dialog)
        
        # Delete Action
        def delete_dialog(*args):
            self.blocked = True
            name = self.user_accounts[self.get_drop_active()]
            self.question_dialog = MessageDialog(self.dlg, MESSAGE_QUESTION,
                                       lang.account_delete_description % name,
                                       lang.account_delete,
                                       yes_callback = self.delete_account,
                                       no_callback = self.unblock)
        
        self.delete.connect('clicked', delete_dialog)
    
    
    # Atarashii ----------------------------------------------------------------
    # --------------------------------------------------------------------------
    def page_atarashii(self, settings):
        
        # get
        self.autostart = self.get('autostart')
        self.taskbar = self.get('taskbar')
        self.tray = self.get('tray')
        self.info_sound = self.get('infosound')
        
        # labels
        self.autostart.set_label(lang.settings_autostart)
        self.taskbar.set_label(lang.settings_taskbar)
        self.tray.set_label(lang.settings_tray)
        self.info_sound.set_label(lang.settings_info_sound)
        
        # set
        self.autostart.set_active(settings.is_true('autostart', False))
        self.taskbar.set_active(settings.is_true('taskbar'))
        self.tray.set_active(settings.is_true('tray', False))
        self.info_sound.set_active(settings.is_true('infosound', True))
        
        # Shortener
        self.get('shortener').set_label(lang.settings_shortener)
        short_names = [lang.settings_shortener_off] + SHORTS_LIST
        short_selected = settings['shortener']
        if short_selected == 'off':
            short_selected = lang.settings_shortener_off
        
        self.shorts = self.create_boxlist('shorts', short_names, short_selected)
        
        # Continues
        self.get('continue').set_label(lang.settings_continue)
        conts = zip(CONTINUE_LIST, lang.settings_continue_names)
        cont_names = ['%s (%s)' % (i, e) for i, e in conts]
        self.continues = self.create_boxlist('continues', cont_names,
                                        cont_names[settings['continue']])
    
    
    # Syncing ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def page_syncing(self, settings):
        self.sync_key_user_set = False
        
        # GUI
        self.sync_box = self.get('syncbox')
        desc = self.get('syncdesc')
        change = self.get('syncbuttonchange')
        entry = self.get('syncentry')
        new = self.get('syncbuttonnew')
        ook = self.get('syncbuttonok')
        cancel = self.get('syncbuttoncancel')
        editbox = self.get('synceditbox')
        entrybox = self.get('syncentrybox')
        label = self.get('synclabel')
        label.set_label(UNSET_LABEL)
        
        # Labels
        self.sync_box.set_label(lang.sync_checkbutton)
        self.get('syncenterlabel').set_label(lang.sync_key_enter)
        desc.set_label(lang.sync_key_loading)
        new.set_label(lang.sync_new)
        change.set_label(lang.sync_change)
        ook.set_label(lang.sync_ok)
        cancel.set_label(lang.sync_cancel)
        
        # Active
        self.sync_box.set_active(settings.is_true('syncing', False))
        self.sync_box.set_sensitive(False)
        self.get('syncoptions').set_sensitive(False)
        
        # Setup syncing GUI
        def init_sync():
            if not self.main.syncer.get_key():
                self.syncing_key = None
                if settings.is_true('syncing', False):
                    desc.set_label(lang.sync_key_error)
                    label.set_label(lang.sync_key_failed)
                    
                    self.sync_box.set_sensitive(True)
                    self.get('syncoptions').set_sensitive(False)
                    
                    self.get('tabs').set_current_page(1)
                    self.get('general_tabs').set_current_page(1)
                
                else:
                    desc.set_label(lang.sync_key_no)
                    label.set_label(UNSET_LABEL)
                    
                    self.get('syncoptions').set_sensitive(True)
                    self.sync_box.set_sensitive(True)
                
                sync_toggle()
                settings['syncing'] = False
                self.sync_box.set_active(False)
            
            else:
                self.get('syncoptions').set_sensitive(True)
                self.sync_box.set_sensitive(True)
                self.syncing_key = settings['synckey']
                desc.set_label(lang.sync_key_current)
                label.set_label(lang.sync_key_label % self.syncing_key)
        
        def pre_retrieve_key(*args):
            self.dlg.set_sensitive(False)
            self.dlg.queue_draw()
            gobject.idle_add(retrieve_key)
        
        def retrieve_key():
            key = self.main.syncer.retrieve_new_key()
            if key is not None:
                self.syncing_key = key
                self.sync_key_user_set = False
                
                desc.set_label(lang.sync_key_current)
                label.set_label(lang.sync_key_label  % self.syncing_key)
                desc.set_label(lang.sync_key_changed)
                
                change.set_sensitive(True)
            
            else:
                desc.set_label(lang.sync_key_error)
                label.set_label(lang.sync_key_failed)
            
            new.set_sensitive(False)
            self.dlg.set_sensitive(True)
        
        new.connect('clicked', pre_retrieve_key)
        
        def sync_change(*args):
            editbox.set_property('visible', False)
            entrybox.set_property('visible', True)
            entry.set_text(self.syncing_key)
        
        def sync_cancel_key(*args):
            editbox.set_property('visible', True)
            entrybox.set_property('visible', False)
        
        def sync_ok_key(*args):
            key = entry.get_text().strip()
            if len(key) != 22:
                return False
            
            if key != settings['synckey']:
                desc.set_label(lang.sync_key_changed)
                self.sync_key_user_set = True
            
            elif key == settings['synckey']:
                desc.set_label(lang.sync_key_current)
                self.sync_key_user_set = False
            
            self.syncing_key = key
            label.set_label(lang.sync_key_label % self.syncing_key)
            editbox.set_property('visible', True)
            entrybox.set_property('visible', False)
        
        def sync_entry_change(*args):
            text = entry.get_text().strip()
            entry.set_text(filter_chars(text, SYNC_KEY_CHARS))
            if len(text) != 22:
                entry.modify_base(gtk.STATE_NORMAL,
                                gtk.gdk.Color(255 * 255, 190 * 255, 190 * 255))
            
            else:
                entry.modify_base(gtk.STATE_NORMAL, self.gui.text.default_bg)
        
        def sync_toggle(*args):
            editbox.set_property('visible', True)
            entrybox.set_property('visible', False)
            self.get('syncoptions').set_sensitive(self.sync_box.get_active())
        
        self.sync_box.connect('toggled', sync_toggle)
        entry.connect('changed', sync_entry_change)
        change.connect('clicked', sync_change)
        cancel.connect('clicked', sync_cancel_key)
        ook.connect('clicked', sync_ok_key)
        sync_toggle()
        gobject.timeout_add(100, init_sync)
    
    
    # Themes -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def page_theme(self, settings):
        settings.load_color_themes()
        self.get('colortheme').set_label(lang.settings_color_theme)
        self.old_color_theme = settings.get('color_theme', THEME_DEFAULT)
        self.color_ids = sorted(settings.color_themes.keys())
        self.color_names = []
        for i in self.color_ids:
            key = 'title_' + lang.code
            name = settings.color_themes[i][key] \
                   if key in settings.color_themes[i] \
                   else settings.color_themes[i]['title_en']
            
            self.color_names.append(name)
        
        self.themes = self.create_boxlist('colorthemebox', self.color_names,
                self.color_names[self.color_ids.index(self.old_color_theme)],
                self.update_css)
        
        # Sizes
        self.get('fontsize').set_label(lang.settings_font_size)
        self.old_font_size = settings.get('fontsize', FONT_DEFAULT)
        self.fonts = self.create_boxlist('fontbox', FONT_SIZES,
                                         self.old_font_size,
                                         self.update_css)
        
        self.get('avatarsize').set_label(lang.settings_avatar_size)
        self.old_avatar_size = settings.get('avatarsize', AVATAR_DEFAULT)
        self.avatars = self.create_boxlist('avatarbox', AVATAR_SIZES,
                                           self.old_avatar_size,
                                           self.update_css)
    
    
    # Notifications and Sounds -------------------------------------------------
    # --------------------------------------------------------------------------
    def page_notify_sounds(self, settings):
        self.get('snd_tweets').set_label(lang.settings_file_tweets)
        self.get('snd_reply').set_label(lang.settings_file_replies)
        self.get('snd_messages').set_label(lang.settings_file_messages)
        
        default_sound = THEME_SOUNDS.get('message-new-instant', UNSET_SOUND)
        
        def get_sound(key):
            if settings.isset('sound_' + key, True):
                snd = str(settings['sound_' + key]).strip()
                return None if snd in (UNSET_SETTING, 'None') else snd
            
            else:
                return default_sound
        
        self.soundfiles = {
            'tweets': settings.get('sound_tweets', default_sound),
            'reply': settings.get('sound_reply', default_sound),
            'messages': settings.get('sound_messages', default_sound)
        }
        
        def set_sound(snd, snd_file):
            self.get('file_' + snd).set_label(os.path.basename(snd_file))
            self.get('button_' + snd + '_del').set_sensitive(True)
            self.soundfiles[snd] = snd_file
        
        def del_sound(button, snd):
            self.get('file_' + snd).set_label(lang.settings_file_none)
            self.soundfiles[snd] = UNSET_SOUND
            button.set_sensitive(False)
        
        self.file_chooser = None
        
        def select_file(button, snd):
            self.file_chooser = SoundChooser(self)
            self.file_chooser.open_file(get_sound(snd), snd, set_sound)
        
        for snd in  ['tweets', 'reply', 'messages']:
            self.get('button_' + snd).connect('clicked', select_file, snd)
            del_button = self.get('button_' + snd + '_del')
            del_button.connect('clicked', del_sound, snd)
            snd_file = get_sound(snd)
            snd_file = os.path.basename(snd_file) if snd_file is not None \
                       else lang.settings_file_none
            
            del_button.set_sensitive(snd_file != lang.settings_file_none)
            self.get('file_' + snd).set_label(snd_file)
        
        
        # Notification
        self.notify = self.get('notify')
        self.notify_network = self.get('notify_network')
        self.overlay = self.get('notify_overlay')
        self.sound = self.get('sound')
        self.notify.set_label(lang.settings_notifications_enable)
        self.notify_network.set_label(lang.settings_notifications_network)
        self.overlay.set_label(lang.settings_notifications_overlay)
        self.sound.set_label(lang.settings_notifications_sound)
        
        self.notify.set_active(settings.is_true('notify'))
        self.overlay.set_active(settings.is_true('notify_overlay', True))
        self.notify_network.set_active(settings.is_true('notify_network', True))
        self.sound.set_active(settings.is_true('sound'))
        self.notify.set_sensitive(True)
        
        def toggle2(*args):
            self.get('soundfiles').set_sensitive(self.sound.get_active())
        
        def toggle(*args):
            self.notify_network.set_sensitive(self.notify.get_active())
            self.overlay.set_sensitive(self.notify.get_active())
            self.sound.set_sensitive(self.notify.get_active())
            self.get('soundfiles').set_sensitive(self.notify.get_active() \
                                                 and self.sound.get_active())
        
        toggle()
        self.notify.connect('toggled', toggle)
        self.sound.connect('toggled', toggle2)

