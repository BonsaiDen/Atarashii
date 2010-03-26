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

from constants import MESSAGE_ERROR, MESSAGE_WARNING, MESSAGE_QUESTION, \
                      MESSAGE_INFO, UNSET_TEXT, UNSET_TIMEOUT


class Dialog:
    resource = ''
    instance = None
    
    def __init__(self, gui, close = True, init = True):
        self.gui = gui
        self.main = gui.main
        self.settings = gui.main.settings
        
        if self.__class__.instance == None:
            self.gtb = gtk.Builder()
            self.gtb.add_from_file(
                 gui.main.get_resource(self.__class__.resource))
            
            self.dlg = self.get('dialog')
            self.dlg.set_property('skip-taskbar-hint', True)
            self.dlg.set_transient_for(gui)
            
            self.dlg.connect('delete_event', self.on_close)
            self.close_button = self.get('closebutton')
            
            if close:
                self.close_button.connect('clicked', self.on_close)
            
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
    resource = 'password.glade'
    instance = None
    
    def __init__(self, parent, title, info):
        Dialog.__init__(self, parent, False, False)
        self.dlg.set_transient_for(parent)
        self.parent = parent
        self.dlg.set_title(title)
        
        self.get('info').set_markup(info)
        
        self.password = self.get('password')
        self.password.grab_focus()
        
        self.close_button.set_label(lang.password_button)
        self.cancel_button = self.get('cancelbutton')
        self.cancel_button.set_label(lang.password_button_cancel)
        
        self.error = self.get('error')
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
            self.main.api_temp_password = ''
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
        
        self.password.connect('key-press-event', key)
        self.close_button.connect('clicked', save)
        self.cancel_button.connect('clicked', abort)


# About Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class AboutDialog(Dialog):
    resource = 'about.glade'
    instance = None
    
    def on_init(self):
        self.dlg.set_title(lang.about_title)
        self.close_button.set_label(lang.about_okbutton)
        if self.main.debug:
            title = '<span size="x-large"><b>%s</b></span>'
        
        else:
            title = '<span size="x-large"><b>Atarashii %s</b></span>'
        
        self.get('title').set_markup(title % self.main.version)
        self.get('image').set_from_file(self.main.get_image())
    
    def on_close(self, *args):
        self.__class__.instance = None
        self.gui.about_dialog = None
        self.gui.about_button.set_active(False)
        self.dlg.hide()


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
                          icon, buttons, '')
        
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
        self.button = gui.gtb.get_object(dtype + '_button')
        self.label = gui.gtb.get_object(dtype + '_label')
        self.image = gui.gtb.get_object(dtype + '_image')
        self.button.connect('clicked', self.show_dialog)
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
                              MESSAGE_WARNING if self.dtype == 'warning' \
                              else MESSAGE_ERROR,
                              time.strftime(self.template, date) + \
                              self.information,
                              self.title, close_callback = self.hide)

