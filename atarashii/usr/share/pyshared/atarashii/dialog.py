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


# Dialogs ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import time

from language import LANG as lang
from constants import ST_LOGIN_SUCCESSFUL

from constants import MESSAGE_ERROR, MESSAGE_WARNING, MESSAGE_QUESTION, \
                      MESSAGE_INFO, UNSET_TEXT, UNSET_TIMEOUT


class Dialog:
    resource = ""
    instance = None
    
    def __init__(self, gui, close = True, init = True):
        self.gui = gui
        self.main = gui.main
        self.settings = gui.main.settings
        
        if self.__class__.instance == None:
            self.gtb = gtk.Builder()
            self.gtb.add_from_file(
                 gui.main.get_resource(self.__class__.resource))
            self.dlg = self.get("dialog")
            self.dlg.set_property("skip-taskbar-hint", True)
            self.dlg.set_transient_for(gui)
            
            self.dlg.connect("delete_event", self.on_close)
            self.close_button = self.get("closebutton")
            
            if close:
                self.close_button.connect("clicked", self.on_close)
            
            self.__class__.instance = self.dlg
            self.dlg.show_all()
            if init:
                self.on_init()
            
            self.close_button.grab_focus()
        
        else:
            gobject.idle_add(self.__class__.instance.present)
    
    def on_init(self):
        pass
    
    def on_close(self, *args):
        self.__class__.instance = None
        self.dlg.hide()
    
    def get(self, widget):
        return self.gtb.get_object(widget)


# Password Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
class PasswordDialog(Dialog):
    resource = "password.glade"
    instance = None
    
    def __init__(self, parent, title, info):
        Dialog.__init__(self, parent, False, False)
        self.dlg.set_transient_for(parent)
        self.parent = parent
        self.dlg.set_title(title)
        
        self.get("info").set_markup(info)
        
        self.password = self.get("password")
        self.password.grab_focus()
        
        self.close_button.set_label(lang.password_button)
        self.cancel_button = self.get("cancelbutton")
        self.cancel_button.set_label(lang.password_button_cancel)
        
        self.error = self.get("error")
        self.default_bg = self.password.get_style().base[gtk.STATE_NORMAL]
        
        self.error.hide()
        self.error_shown = False
        self.error.set_label(lang.password_too_short)
        
        def save(*args):
            password = self.password.get_text().strip()
            if len(password) < 6:
                self.error_shown = True
                self.error.show()
                self.password.modify_base(gtk.STATE_NORMAL,
                         gtk.gdk.Color(255 * 255, 200 * 255, 200 * 255))
                
                self.password.grab_focus()
            
            else:
                self.main.api_temp_password = password
                self.on_close()
        
        
        def abort(*args):
            self.main.api_temp_password = ""
            self.on_close()
        
        def key(widget, event, *args):
            if self.error_shown:
                if len(self.password.get_text().strip()) >= 6:
                    self.password.modify_base(gtk.STATE_NORMAL,
                                                    self.default_bg)
                    self.error.hide()
                    self.error_shown = False
            
            if event.keyval in (gtk.keysyms.Return, gtk.keysyms.KP_Enter):
                save()
        
        self.password.connect("key-press-event", key)
        self.close_button.connect("clicked", save)
        self.cancel_button.connect("clicked", abort)


# About Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class AboutDialog(Dialog):
    resource = "about.glade"
    instance = None
    
    def on_init(self):
        self.dlg.set_title(lang.about_title)
        self.close_button.set_label(lang.about_okbutton)
        self.get("title").set_markup(
        '<span size="x-large"><b>Atarashii %s</b></span>' % self.main.version)
        self.get("image").set_from_file(self.main.get_image())
    
    def on_close(self, *args):
        self.__class__.instance = None
        self.gui.about_dialog = None
        self.gui.about_button.set_active(False)
        self.dlg.hide()


# Settings Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
class SettingsDialog(Dialog):
    resource = "settings.glade"
    instance = None
    
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
        cancel_button = self.get("cancelbutton")
        cancel_button.set_label(lang.settings_buttonCancel)
        
        # Accounts
        add = self.get("add")
        add.set_label(lang.settings_add)
        self.edit = edit = self.get("edit")
        edit.set_label(lang.settings_edit)
        self.delete = delete = self.get("delete")
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
        self.get("treewindow").add(drop)
        drop.show()
        drop.connect("cursor-changed", self.drop_changed)
        self.create_drop_list()
        self.drop_changed()

        
        # Edit Action
        def edit_dialog(*args):
            name = self.user_accounts[self.get_drop_active()]
            AccountDialog(self, name, lang.account_edit, self.edit_account)
        
        edit.connect("clicked", edit_dialog)
        
        # Add Action
        def create_dialog(*args):
            AccountDialog(self, "", lang.account_create, self.create_account)
        
        add.connect("clicked", create_dialog)
        
        # Delete Action
        def delete_dialog(*args):
            name = self.user_accounts[self.get_drop_active()]
            MessageDialog(self.dlg, MESSAGE_QUESTION,
                            lang.account_delete_description % name,
                            lang.account_delete,
                            yes_callback = self.delete_account)
        
        delete.connect("clicked", delete_dialog)
        
        # Notifications
        self.get("notifications").set_text(lang.settings_notifications)
        notify = self.get("notify")
        sound = self.get("sound")
        notify.set_label(lang.settings_notify)
        sound.set_label(lang.settings_sound)
        
        # General
        self.get("general").set_text(lang.settings_general)
        autostart = self.get("autostart")
        taskbar = self.get("taskbar")
        tray = self.get("tray")
        
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
        def choosen(chooser, code):
            if code != gtk.RESPONSE_OK:
                file_chooser.set_filename(str(self.settings['soundfile']))
        
        file_widget = gtk.FileChooserButton(file_chooser)
        self.get("notifybox").pack_end(file_widget)
        file_widget.show()
        file_chooser.connect("response", choosen)
        file_chooser.set_title(lang.settings_file)
        if str(self.settings['soundfile']) in ("", "None"):
            file_chooser.set_current_folder("/usr/share/sounds")
        
        else:
            file_chooser.set_filename(str(self.settings['soundfile']))  
        
        # File Filter
        file_filter = gtk.FileFilter()
        file_filter.set_name(lang.settings_file_filter)
        file_filter.add_pattern("*.mp3")
        file_filter.add_pattern("*.wav")
        file_filter.add_pattern("*.ogg")
        file_chooser.add_filter(file_filter)  
        file_chooser.set_filter(file_filter)
        
        # Fix bug with the file filter no beeing selected
        def select_file(chooser):
            if file_chooser.get_filter() == None:
                file_chooser.set_filter(file_filter)
        
        file_chooser.connect("selection-changed", select_file)
        
        
        # Notification Setting -------------------------------------------------
        notify.set_active(self.settings.is_true("notify"))
        sound.set_active(self.settings.is_true("sound"))
        notify.set_sensitive(True)
        
        def toggle2():
            file_widget.set_sensitive(sound.get_active())
        
        def toggle():
            sound.set_sensitive(notify.get_active())
            file_widget.set_sensitive(
                        notify.get_active() and sound.get_active())
        
        toggle()
        notify.connect("toggled", lambda *a: toggle())
        sound.connect("toggled", lambda *a: toggle2())
        
        
        # Save -----------------------------------------------------------------
        oldusername = self.main.username
        def save(*args):
            self.saved = True
            self.settings['soundfile'] = str(file_widget.get_filename())
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
                username = ""
            
            # Save Settings
            self.main.save_settings(False)
            if username == "":
                self.main.username = ""
                self.settings['username'] = ""
                self.main.logout()
            
            elif username != oldusername \
                or not self.main.status(ST_LOGIN_SUCCESSFUL):
                
                self.main.login(username)
            
            self.on_close()
        
        
        self.close_button.connect("clicked", save)
        cancel_button.connect("clicked", self.on_close)
        gobject.idle_add(self.drop.grab_focus)
    
    def on_close(self, *args):
        if not self.saved:
            if self.get_drop_active() == -1:
                self.main.username = ""
                self.settings['username'] = ""
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
            self.main.settings['account_' + username] = ""
            self.main.settings['firsttweet_' + username] = ft_tmp
            self.main.settings['lasttweet_' + username] = lt_tmp
            self.main.settings['firstmessage_' + username] = fm_tmp
            self.main.settings['lastmessage_' + username] = lm_tmp
            
            if self.main.username == name:
                self.main.username = self.main.settings['username'] = username
            
            self.main.settings.save()
            self.create_drop_list(username)
    
    def create_account(self, username):
        self.main.settings['account_' + username] = ""
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
            self.main.username = self.main.settings['username'] = ""
        
        self.create_drop_list()


# Account Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class AccountDialog(Dialog):
    resource = "account.glade"
    instance = None
    
    def __init__(self, parent, username, title, callback):
        Dialog.__init__(self, parent.gui, False)
        self.dlg.set_transient_for(parent.dlg)
        self.parent = parent
        self.callback = callback
        self.dlg.set_title(title)
        self.username = username
        self.get("username").set_text(username)
        self.get("username").grab_focus()
    
    def on_init(self):
        self.close_button.set_label(lang.account_button)
        cancel_button = self.get("cancelbutton")
        cancel_button.set_label(lang.account_button_cancel)
        
        self.get("user").set_text(lang.account_username)
        
        
        def save(*args):
            username = self.get("username").get_text().strip()
            if username == "":
                self.get("username").grab_focus()
            
            elif username in self.parent.user_accounts \
                 and username != self.username:
                self.get("username").grab_focus()
            
            else:
                self.callback(username)
                self.on_close()
        
        self.close_button.connect("clicked", save)
        cancel_button.connect("clicked", self.on_close)


# Message Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class MessageDialog(gtk.MessageDialog):
    def __init__(self, parent, msg_type, message, title, ok_callback = None,
                yes_callback = None, no_callback = None, close_callback = None):
        
        buttons = gtk.BUTTONS_OK
        if msg_type == MESSAGE_ERROR:
            icon = gtk.MESSAGE_ERROR
        
        elif msg_type == MESSAGE_WARNING:
            icon = gtk.MESSAGE_WARNING
        
        elif msg_type == MESSAGE_QUESTION:
            icon = gtk.MESSAGE_QUESTION
            buttons = gtk.BUTTONS_YES_NO
        
        elif msg_type == MESSAGE_INFO:
            icon = gtk.MESSAGE_INFO
        
        # Init
        gtk.MessageDialog.__init__(self, parent,
                          gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                          icon, buttons, "")
        
        self.set_markup(message)
        self.set_title(title)
        self.ok_callback = ok_callback
        self.yes_callback = yes_callback
        self.no_callback = no_callback
        self.close_callback = close_callback
        self.set_default_response(gtk.RESPONSE_OK)
        self.connect('response', self.on_close)
        self.show_all()
    
    def on_close(self, dialog, response):
        self.destroy()
        if response == gtk.RESPONSE_OK and self.ok_callback != None:
            self.ok_callback()
        
        elif response == gtk.RESPONSE_YES and self.yes_callback != None:
            self.yes_callback()
        
        elif response == gtk.RESPONSE_NO and self.no_callback != None:
            self.no_callback()

        if self.close_callback != None:
            self.close_callback()
        

# Button Dialog ----------------------------------------------------------------
# ------------------------------------------------------------------------------
class ButtonDialog:
    def __init__(self, gui, dtype, template, title):
        self.gui = gui
        self.box = gui.gtb.get_object(dtype)
        self.button = gui.gtb.get_object(dtype + "_button")
        self.label = gui.gtb.get_object(dtype + "_label")
        self.image = gui.gtb.get_object(dtype + "_image")
        self.button.connect("clicked", self.show_dialog)
        self.button.set_tooltip_text(lang.button_open)
        self.dtype = dtype
        self.dialog = None
        self.shown = False
        self.information = UNSET_TEXT
        self.time = UNSET_TIMEOUT
        
        self.title = title
        self.template = template
    
    def hide(self):
        if self.dialog != None:
            self.dialog.destroy()
            self.dialog = None
        
        self.box.hide()
    
    def show(self, button, info):
        self.information = info
        if self.dialog != None:
            self.dialog.destroy()
            self.dialog = None
        
        self.time = time.time()
        self.box.show()
        self.label.set_markup(button)
        
        # Show GUI if not shown so the user does notice the message
        if not self.gui.is_shown:
            gobject.idle_add(self.gui.show_gui)
    
    def show_dialog(self, *args):
        if self.dialog != None:
            self.dialog.destroy()
            self.dialog = None
        
        date = time.localtime(self.time)
        self.dialog = MessageDialog(self.gui,
                              MESSAGE_WARNING if self.dtype == "warning" \
                              else MESSAGE_ERROR,
                              time.strftime(self.template, date) + \
                              self.information,
                              self.title, close_callback = self.hide)

