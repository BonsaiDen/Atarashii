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


# Subdialogs for the Settings Dialog -------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from dialog import Dialog
from sounds import THEME_DIR
from utils import filter_chars
from lang import LANG as lang

from constants import USERNAME_CHARS, UNSET_USERNAME


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
        self.user.set_text(filter_chars(text, USERNAME_CHARS))
    
    def on_close(self, *args):
        self.parent.username_dialog = None
        self.parent.blocked = False
        self.instance = None
        self.dlg.hide()

