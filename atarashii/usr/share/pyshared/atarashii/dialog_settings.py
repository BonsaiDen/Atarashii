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

from language import LANG as lang
from dialog import Dialog, MessageDialog

from constants import ST_LOGIN_SUCCESSFUL, ST_CONNECT
from constants import MESSAGE_QUESTION


class SettingsDialog(Dialog):
    resource = 'settings.glade'
    instance = None
    
    def activate(self, mode):
        if self.drop != None:
            self.drop.set_sensitive(mode)
            self.add.set_sensitive(mode)
            self.edit.set_sensitive(mode)
            self.delete.set_sensitive(mode)
    
    def __init__(self, parent):
        Dialog.__init__(self, parent, True, False)
        self.dlg.set_transient_for(parent)
        self.parent = parent
        
        # Check for autostart
        self.main.settings.check_autostart()
        
        # Stuff
        self.saved = False
        self.dlg.set_title(lang.settings_title)
        self.close_button.set_label(lang.settings_button)
        cancel_button = self.get('cancelbutton')
        cancel_button.set_label(lang.settings_buttonCancel)
        
        # Accounts
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
        column = gtk.TreeViewColumn(lang.settings_accounts)
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
            name = self.user_accounts[self.get_drop_active()]
            AccountDialog(self, name, lang.account_edit, self.edit_account)
        
        edit.connect('clicked', edit_dialog)
        
        # Add Action
        def create_dialog(*args):
            AccountDialog(self, '', lang.account_create, self.create_account)
        
        add.connect('clicked', create_dialog)
        
        # Delete Action
        def delete_dialog(*args):
            name = self.user_accounts[self.get_drop_active()]
            MessageDialog(self.dlg, MESSAGE_QUESTION,
                            lang.account_delete_description % name,
                            lang.account_delete,
                            yes_callback = self.delete_account)
        
        delete.connect('clicked', delete_dialog)
        
        # Notifications
        self.get('notifications').set_text(lang.settings_notifications)
        notify = self.get('notify')
        sound = self.get('sound')
        notify.set_label(lang.settings_notify)
        sound.set_label(lang.settings_sound)
        
        # General
        self.get('general').set_text(lang.settings_general)
        autostart = self.get('autostart')
        taskbar = self.get('taskbar')
        tray = self.get('tray')
        
        autostart.set_label(lang.settings_autostart)
        taskbar.set_label(lang.settings_taskbar)
        tray.set_label(lang.settings_tray)
        
        autostart.set_active(self.settings.is_true('autostart', False))
        taskbar.set_active(self.settings.is_true('taskbar'))
        tray.set_active(self.settings.is_true('tray', False))
        
        
        # Sound File Chooser, create it here to fix some bugs ------------------
        # ----------------------------------------------------------------------
        file_chooser = gtk.FileChooserDialog(None, self.dlg,
                                         action = gtk.FILE_CHOOSER_ACTION_OPEN,
                                         buttons = (lang.settings_file_cancel,
                                         gtk.RESPONSE_CANCEL,
                                         lang.settings_file_ok,
                                         gtk.RESPONSE_OK))
        
        
        # Fix a bug were the button would be empty if the dialog is canceled
        # for the first time
        self.tmp_file = str(self.settings['soundfile'])
        def choosen(chooser, code):
            if code != gtk.RESPONSE_OK:
                file_chooser.set_filename(str(self.settings['soundfile']))
            
            else:
                self.tmp_file = str(file_chooser.get_filename())
        
        file_widget = gtk.FileChooserButton(file_chooser)
        self.get('notifybox').pack_end(file_widget)
        file_widget.show()
        file_chooser.connect('response', choosen)
        file_chooser.set_title(lang.settings_file)
        if str(self.settings['soundfile']) in ('', 'None'):
            file_chooser.set_current_folder('/usr/share/sounds')
        
        else:
            file_chooser.set_filename(str(self.settings['soundfile']))  
        
        # File Filter
        file_filter = gtk.FileFilter()
        file_filter.set_name(lang.settings_file_filter)
        file_filter.add_pattern('*.mp3')
        file_filter.add_pattern('*.wav')
        file_filter.add_pattern('*.ogg')
        file_chooser.add_filter(file_filter)  
        file_chooser.set_filter(file_filter)
        self.file_chooser = file_chooser
        
        # Fix bug with the file filter no beeing selected
        def select_file(chooser):
            if file_chooser.get_filter() == None:
                file_chooser.set_filter(file_filter)
        
        file_chooser.connect('selection-changed', select_file)
        
        
        # Notification Setting -------------------------------------------------
        notify.set_active(self.settings.is_true('notify'))
        sound.set_active(self.settings.is_true('sound'))
        notify.set_sensitive(True)
        
        def toggle2():
            file_widget.set_sensitive(sound.get_active())
        
        def toggle():
            sound.set_sensitive(notify.get_active())
            file_widget.set_sensitive(
                        notify.get_active() and sound.get_active())
        
        toggle()
        notify.connect('toggled', lambda *a: toggle())
        sound.connect('toggled', lambda *a: toggle2())
        
        
        # Save -----------------------------------------------------------------
        oldusername = self.main.username
        def save(*args):
            self.saved = True
            self.settings['soundfile'] = self.tmp_file
            
            self.settings['notify'] = notify.get_active()
            self.settings['sound'] = sound.get_active()
            self.settings['tray'] = tray.get_active()
            
            self.settings.set_autostart(autostart.get_active())
            self.gui.show_in_taskbar(taskbar.get_active())
            
            # Save GUI Mode
            self.main.save_mode()
            
            # Set new Username
            if self.get_drop_active() != -1:
                username = self.user_accounts[self.get_drop_active()]
            
            else:
                username = ''
            
            # Save Settings
            self.main.save_settings(False)
            if username == '':
                self.main.username = ''
                self.settings['username'] = ''
                self.main.logout()
            
            elif username != oldusername \
                or not self.main.status(ST_LOGIN_SUCCESSFUL):
                
                self.activate(False)
                self.main.login(username)
            
            self.on_close()
        
        
        self.activate(not self.main.status(ST_CONNECT))
        self.close_button.connect('clicked', save)
        cancel_button.connect('clicked', self.on_close)
        gobject.idle_add(self.drop.grab_focus)
    
    def on_close(self, *args):
        self.file_chooser.hide()
        if not self.saved:
            if self.get_drop_active() == -1:
                self.main.username = ''
                self.settings['username'] = ''
                self.main.logout()
        
        self.__class__.instance = None
        self.gui.settings_dialog = None
        self.gui.settings_button.set_active(False)
        self.dlg.hide()
    
    # Generate Account List ----------------------------------------------------
    def get_drop_active(self):
        i = self.drop.get_selection().get_selected_rows()[1]
        if i == None or len(i) == 0:
            return -1
        
        return i[0][0]
    
    def select_drop(self, num):
        self.drop.get_selection().select_path((num,))
        self.drop_changed()

    def create_drop_list(self, name = None):
        self.user_accounts = self.main.settings.get_accounts()
        self.accounts_list = gtk.ListStore(str)
        selected = -1
        for num, user in enumerate(self.user_accounts):
            self.accounts_list.append([user])
            if user == name:
                selected = num
            
            elif name == None and user == self.main.username:
                selected = num
        
        self.drop.set_model(self.accounts_list)
        if selected != -1:
            self.select_drop(selected)
        
        else:
            self.drop_changed()
            
     # Setup Account List
    def drop_changed(self, *args):
        i = self.get_drop_active()
        if i != -1:
            self.edit.set_sensitive(True)
            self.delete.set_sensitive(True)
        
        else:
            self.edit.set_sensitive(False)
            self.delete.set_sensitive(False)
    
    
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
            self.main.settings['account_' + username] = ''
            self.main.settings['firsttweet_' + username] = ft_tmp
            self.main.settings['lasttweet_' + username] = lt_tmp
            self.main.settings['firstmessage_' + username] = fm_tmp
            self.main.settings['lastmessage_' + username] = lm_tmp
            
            if self.main.username == name:
                self.main.username = self.main.settings['username'] = username
            
            self.main.settings.save()
            self.create_drop_list(username)
    
    def create_account(self, username):
        self.main.settings['account_' + username] = ''
        self.main.username = username
        self.create_drop_list()
        if len(self.user_accounts) == 1:
            self.select_drop(0)
    
    def delete_account(self):
        name = self.user_accounts[self.get_drop_active()]
        del self.main.settings['mode_' + name]
        del self.main.settings['account_' + name]
        del self.main.settings['firsttweet_' + name]
        del self.main.settings['lasttweet_' + name]
        del self.main.settings['firstmessage_' + name]
        del self.main.settings['lastmessage_' + name]
        del self.main.settings['xkey_' + name]
        del self.main.settings['xsecret_' + name]
        if self.main.username == name:
            self.main.username = self.main.settings['username'] = ''
        
        self.create_drop_list()


# Account Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class AccountDialog(Dialog):
    resource = 'account.glade'
    instance = None
    
    def __init__(self, parent, username, title, callback):
        Dialog.__init__(self, parent.gui, False)
        self.dlg.set_transient_for(parent.dlg)
        self.parent = parent
        self.callback = callback
        self.dlg.set_title(title)
        self.username = username
        self.get('username').set_text(username)
        self.get('username').grab_focus()
    
    def on_init(self):
        self.close_button.set_label(lang.account_button)
        cancel_button = self.get('cancelbutton')
        cancel_button.set_label(lang.account_button_cancel)
        
        self.get('user').set_text(lang.account_username)
        
        
        def save(*args):
            username = self.get('username').get_text().strip()
            if username == '':
                self.get('username').grab_focus()
            
            elif username in self.parent.user_accounts \
                 and username != self.username:
                self.get('username').grab_focus()
            
            else:
                self.callback(username)
                self.on_close()
        
        self.close_button.connect('clicked', save)
        cancel_button.connect('clicked', self.on_close)
