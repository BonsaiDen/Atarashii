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

from lang import lang
from notify import CAN_NOTIFY
from constants import *

class Dialog:
    resource = ""
    instance = None

    def __init__(self, gui, close = True):
        self.gui = gui
        self.main = gui.main
        self.settings = gui.main.settings
        
        if self.__class__.instance == None:
            self.gt = gtk.Builder()
            self.gt.add_from_file(gui.main.getResource(self.__class__.resource))
            self.dlg = self.get("dialog")
            self.dlg.set_property("skip-taskbar-hint", True)
            self.dlg.set_transient_for(gui)        
            
            self.dlg.connect("delete_event", self.onClose)
            self.closeButton = self.get("closebutton")
            
            if close:
                self.closeButton.connect("clicked", self.onClose)
            
            self.__class__.instance = self.dlg
            self.dlg.show_all()
            self.onInit()
            
            self.closeButton.grab_focus()
            
        else:
            gobject.idle_add(lambda: self.__class__.instance.present())
    
    def onInit(self):
        pass
    
    def onClose(self, *args):
        self.__class__.instance = None
        self.dlg.hide()
        
    def get(self, widget):
        return self.gt.get_object(widget)



# Password Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
class PasswordDialog(Dialog):
    resource = "password.glade"
    instance = None
    
    def __init__(self, parent, title, info):
        Dialog.__init__(self, parent, False)
        self.dlg.set_transient_for(parent)
        self.parent = parent
        self.dlg.set_title(title)
        self.get("password").grab_focus()
        self.get("info").set_label(info)
    
    def onInit(self):
        self.closeButton.set_label(lang.passwordButton)
        cancelButton = self.get("cancelbutton")
        cancelButton.set_label(lang.passwordButtonCancel)
                
        def save(*args):
            password = self.get("password").get_text().strip()
            if password == "":
                self.get("password").grab_focus()        
            
            else:
                self.main.apiTempPassword = password
                self.onClose()
        
        def abort(*args):
            self.main.apiTempPassword = ""
            self.onClose()
        
        def key(widget, event, *args):
            if event.keyval == gtk.keysyms.Return:
                save()
        
        self.get("password").connect("key-press-event", key)
        self.closeButton.connect("clicked", save)
        cancelButton.connect("clicked", abort)


# About Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class AboutDialog(Dialog):
    resource = "about.glade"
    instance = None
    
    def onInit(self):
        self.dlg.set_title(lang.aboutTitle)
        self.closeButton.set_label(lang.aboutOKButton)
        self.get("title").set_markup(
        '<span size="x-large"><b>Atarashii %s</b></span>' % self.main.version)
        self.get("image").set_from_file(self.main.getImage())
    
        # License toggling
        info = self.get("infobox")
        text = self.get("textwindow")
        license = self.get("license")
        license.set_label(lang.aboutLicenseButton)
        
        def toggle(widget, *args):
            if widget.get_property("active"):
                text.show()
                info.hide()
            
            else:
                info.show()
                text.hide()
        
        text.hide()
        license.connect("toggled", toggle)
        
    def onClose(self, *args):
        self.__class__.instance = None
        self.gui.aboutDialog = None
        self.gui.aboutButton.set_active(False)
        self.dlg.hide()


# Settings Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
class SettingsDialog(Dialog):
    resource = "settings.glade"
    instance = None
    
    def onInit(self):
        self.dlg.set_title(lang.settingsTitle)
        self.closeButton.set_label(lang.settingsButton)
        cancelButton = self.get("cancelbutton")
        cancelButton.set_label(lang.settingsButtonCancel)

        # Accounts
        self.get("accounts").set_text(lang.settingsAccounts)
        add = self.get("add")
        add.set_label(lang.settingsAdd)
        edit = self.get("edit")
        edit.set_label(lang.settingsEdit)
        delete = self.get("delete")
        delete.set_label(lang.settingsDelete)
        
        # Setup Account List
        def dropChanged(*args):
            i = drop.get_active()
            if i != -1:
                edit.set_sensitive(True)
                delete.set_sensitive(True)
                    
            else:
                edit.set_sensitive(False)
                delete.set_sensitive(False)

        self.drop = drop = self.get("dropbox")
        drop.connect("changed", dropChanged)
        cell = gtk.CellRendererText()
        self.drop.pack_start(cell, True)
        self.drop.add_attribute(cell, 'text', 0)
        self.createDropList()
        dropChanged()


        # Edit Action
        def editDialog(*args):
            name = self.userAccounts[drop.get_active()]
            AccountDialog(self, name, lang.accountEdit, self.editAccount)
        
        edit.connect("clicked", editDialog)
        
        # Add Action
        def createDialog(*args):
            AccountDialog(self, "", lang.accountCreate, self.createAccount)
        
        add.connect("clicked", createDialog)
        
        # Delete Action
        def deleteDialog(*args):
            name = self.userAccounts[drop.get_active()]
            MessageDialog(self.dlg, MESSAGE_QUESTION,
                            lang.accountDeleteDescription % name,
                            lang.accountDelete,
                            yesCallback = self.deleteAccount)
        
        delete.connect("clicked", deleteDialog)


        # Notifications
        self.get("notifications").set_text(lang.settingsNotifications)
        notify = self.get("notify")
        sound = self.get("sound")
        notify.set_label(lang.settingsNotify)
        sound.set_label(lang.settingsSound)
        
        
        # Sound File
        fileWidget = self.get("soundfile")
        fileFilter = gtk.FileFilter()
        fileFilter.set_name(lang.settingsFileFilter)
        fileFilter.add_pattern("*.mp3")
        fileFilter.add_pattern("*.wav")
        fileFilter.add_pattern("*.ogg")
        fileWidget.add_filter(fileFilter)
        fileWidget.set_title(lang.settingsFile)
        fileWidget.set_filename(str(self.settings['soundfile']))
        
        
        # Notification Setting
        notify.set_active(self.settings.isTrue("notify"))
        sound.set_active(self.settings.isTrue("sound"))
        notify.set_sensitive(CAN_NOTIFY)
        
        def toggle2():
            fileWidget.set_sensitive(sound.get_active())
        
        def toggle():
            sound.set_sensitive(notify.get_active() and CAN_NOTIFY)
            fileWidget.set_sensitive(notify.get_active() and sound.get_active())
        
        toggle()
        notify.connect("toggled", lambda *a: toggle())
        sound.connect("toggled", lambda *a: toggle2())
        
        # Retweet settings
        self.get("retweets").set_text(lang.settingsRetweets)
        retweet = self.get("retweet_ask")
        askRT = self.get("retweet_ask")
        newRT = self.get("retweet_new")
        oldRT = self.get("retweet_old")
        askRT.set_label(lang.settingsRetweetsAsk)
        newRT.set_label(lang.settingsRetweetsNew)
        oldRT.set_label(lang.settingsRetweetsOld)
        rt = self.settings['retweets']
        if rt == 0:
            askRT.set_active(True)
        
        elif rt == 1:
            newRT.set_active(True)
        
        elif rt == 2:
            oldRT.set_active(True)
        
        
        # Save -----------------------------------------------------------------
        oldusername = self.main.username
        olduserpass = self.settings["password_" + self.main.username]
        def save(*args):
            self.settings['soundfile'] = str(fileWidget.get_filename())
            self.settings['notify'] = notify.get_active()
            self.settings['sound'] = sound.get_active()
            
            if askRT.get_active():
                rt = 0
                
            elif newRT.get_active():
                rt = 1
                
            elif oldRT.get_active():
                rt = 2    
            
            self.settings['retweets'] = rt
            
            # Save GUI Mode
            self.main.saveMode()
            
            # Set new Username
            if drop.get_active() != -1:
                self.main.username = self.userAccounts[drop.get_active()]
                self.settings['username'] = self.main.username
            
            # Save Settings
            self.main.saveSettings()
            if self.main.username == "":
                self.main.logout()
            
            elif self.main.username != oldusername or not self.main.loginStatus:
                self.main.login()
                        
            self.onClose()
        
        self.closeButton.connect("clicked", save)
        cancelButton.connect("clicked", self.onClose)
        
    def onClose(self, *args):
        self.__class__.instance = None
        self.gui.settingsDialog = None
        self.gui.settingsButton.set_active(False)
        self.dlg.hide()
        
    # Generate Account List
    def createDropList(self, name = None):
        self.userAccounts = self.main.settings.getAccounts()
        self.accountsList = gtk.ListStore(str)
        selected = -1
        for c, i in enumerate(self.userAccounts):
            self.accountsList.append([i])
            if i == name:
                selected = c
            elif name == None and i == self.main.username:
                selected = c
        
        self.drop.set_model(self.accountsList)
        self.drop.set_active(selected)
        
    # Edit a User Account
    def editAccount(self, username):
        name = self.userAccounts[self.drop.get_active()]
        if name != username:
            ft = self.main.settings['firsttweet_' + name]
            lt = self.main.settings['lasttweet_' + name]
            fm = self.main.settings['firstmessage_' + name]
            lm = self.main.settings['lastmessage_' + name]
            lo = self.main.settings['mode_' + name]
            
            del self.main.settings['mode_' + name]
            del self.main.settings['account_' + name]
            del self.main.settings['firsttweet_' + name]
            del self.main.settings['lasttweet_' + name]
            del self.main.settings['firstmessage_' + name]
            del self.main.settings['lastmessage_' + name]
            del self.main.settings['xkey_' + name]
            del self.main.settings['xsecret_' + name]
            
            self.main.settings['mode_' + username] = lo
            self.main.settings['account_' + username] = ""
            self.main.settings['firsttweet_' + username] = ft
            self.main.settings['lasttweet_' + username] = lt
            self.main.settings['firstmessage_' + username] = fm
            self.main.settings['lastmessage_' + username] = lm
            
            if self.main.username == name:
                self.main.username = self.main.settings['username'] = username
            
            self.main.settings.save()
            self.createDropList(username)
    
        
    def createAccount(self, username):
        self.main.settings['account_' + username] = ""
        self.createDropList()
        if len(self.userAccounts) == 1:
            self.drop.set_active(0)
    
    
    def deleteAccount(self):
        name = self.userAccounts[self.drop.get_active()]
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
            
        self.createDropList()


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
    
    def onInit(self):
        self.closeButton.set_label(lang.accountButton)
        cancelButton = self.get("cancelbutton")
        cancelButton.set_label(lang.accountButtonCancel)
        
        self.get("user").set_text(lang.accountUsername)
        
        def save(*args):
            username = self.get("username").get_text().strip()
            if username == "":
                self.get("username").grab_focus()
                        
            elif username in self.parent.userAccounts and \
                username != self.username:
                self.get("username").grab_focus()
            
            else:
                self.callback(username)
                self.onClose()
        
        self.closeButton.connect("clicked", save)
        cancelButton.connect("clicked", self.onClose)    


# Message Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class MessageDialog(gtk.MessageDialog):
    def __init__(self, parent, mt, message, title, okCallback = None,
                yesCallback = None, noCallback = None):
        
        if mt == MESSAGE_ERROR:
            gtk.MessageDialog.__init__(self, parent, 
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_ERROR, gtk.BUTTONS_OK, message)

        elif mt == MESSAGE_WARNING:
            gtk.MessageDialog.__init__(self, parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_WARNING, gtk.BUTTONS_OK, message)

        elif mt == MESSAGE_QUESTION:
            gtk.MessageDialog.__init__(self, parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_QUESTION, gtk.BUTTONS_YES_NO, message)

        elif mt == MESSAGE_INFO:
            gtk.MessageDialog.__init__(self, parent,
                        gtk.DIALOG_MODAL | gtk.DIALOG_DESTROY_WITH_PARENT,
                        gtk.MESSAGE_INFO, gtk.BUTTONS_OK, message)

        self.set_title(title)
        self.okCallback = okCallback
        self.yesCallback = yesCallback
        self.noCallback = noCallback
        self.set_default_response(gtk.RESPONSE_OK)
        self.connect('response', self.onClose)
        self.show_all()
        
    def onClose(self, dialog, response):
        self.destroy()
        if response == gtk.RESPONSE_OK and self.okCallback != None:
            self.okCallback()
        
        elif response == gtk.RESPONSE_YES and self.yesCallback != None:
            self.yesCallback()
        
        elif response == gtk.RESPONSE_NO and self.noCallback != None:
            self.noCallback()

