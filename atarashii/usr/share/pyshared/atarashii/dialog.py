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

from sounds import play_sound
from lang import LANG as lang

from constants import MESSAGE_ERROR, MESSAGE_WARNING, MESSAGE_QUESTION, \
                      MESSAGE_INFO, UNSET_TEXT, UNSET_TIMEOUT, UNSET_PASSWORD, \
                      UNSET_RESOURCE, MESSAGE_INFO


class Dialog(object):
    resource = UNSET_RESOURCE
    instance = None
    
    def __init__(self, gui, close=True, init=True, on_gui=False):
        self.gui = gui
        self.main = gui.main
        self.settings = gui.main.settings
        
        if self.instance is None:
            self.gtb = gtk.Builder()
            self.gtb.add_from_file(
                 gui.main.get_resource(self.resource))
            
            self.dlg = self.get('dialog')
            self.dlg.set_property('skip-taskbar-hint', True)
            if on_gui:
                self.dlg.set_transient_for(gui)
            
            self.dlg.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
            
            self.dlg.connect('delete_event', self.on_close)
            self.close_button = self.get('closebutton')
            
            if close:
                self.close_button.connect('clicked', self.on_close)
            
            self.instance = self.dlg
            self.dlg.show_all()
            if init:
                self.on_init()
            
            self.close_button.grab_focus()
        
        else:
            gobject.idle_add(self.instance.present)
    
    def on_init(self):
        pass
    
    def on_close(self, *args):
        self.instance = None
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
    
    def on_close(self, *args):
        if self.main.api_temp_password is None:
            self.main.api_temp_password = UNSET_PASSWORD
        
        self.main.updater.password_wait.set()
        self.instance = None
        self.dlg.hide()


# About Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class AboutDialog(Dialog):
    resource = 'about.glade'
    instance = None
    
    def on_init(self):
        self.dlg.set_title(lang.about_title)
        self.close_button.set_label(lang.about_okbutton)
        self.kitten_button = self.get('kittenbutton')
        self.kitten_button.set_label(lang.about_kitten_button)
        self.get('title').set_markup(
                          '<span size="xx-large"><b>Atarashii %s</b></span>'
                          % self.main.version)
        
        self.get('description').set_markup(lang.about_description)
        
        if not gtk.IconTheme().has_icon('bonsaiden-atarashii'):
            self.get('image').set_from_file(self.main.get_image())
        
        self.get('subinfo').hide()
        
        def toggle(button, *args):
            if self.kitten_button.get_active():
                size = self.dlg.get_allocation()
                self.dlg.set_size_request(size[2], -1)
                self.kitten_button.set_label(lang.about_back_button)
                self.get('maininfo').hide()
                self.get('subinfo').show()
            
            else:
                self.kitten_button.set_label(lang.about_kitten_button)
                self.get('maininfo').show()
                self.get('subinfo').hide()
        
        self.get('kittens').set_markup(lang.about_kittens \
                                       % (self.main.kittens, self.main.secret))
        
        self.kitten_button.connect('toggled', toggle)
    
    def on_close(self, *args):
        self.instance = None
        self.gui.about_dialog = None
        self.dlg.hide()
        self.dlg.destroy()


# Message Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class MessageDialog(gtk.MessageDialog):
    def __init__(self, parent, msg_type, message, title, ok_callback=None,
                yes_callback=None, no_callback=None, close_callback=None):
        
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
        if response == gtk.RESPONSE_OK and self.ok_callback is not None:
            self.ok_callback()
        
        elif response == gtk.RESPONSE_YES and self.yes_callback is not None:
            self.yes_callback()
        
        elif response == gtk.RESPONSE_NO and self.no_callback is not None:
            self.no_callback()
        
        if self.close_callback is not None:
            self.close_callback()


# Button Dialog ----------------------------------------------------------------
# ------------------------------------------------------------------------------
class ButtonDialog(object):
    def __init__(self, gui, dtype, template, title, passive=False,
                 callback=None):
        
        self.gui = gui
        self.dialog = None
        self.dtype = dtype
        self.passive = passive
        
        # GUI
        self.box = gui.gtb.get_object(dtype)
        self.button = gui.gtb.get_object(dtype + '_button')
        self.label = gui.gtb.get_object(dtype + '_label')
        self.image = gui.gtb.get_object(dtype + '_image')
        self.button.connect('clicked', callback if self.passive \
                                                else self.show_dialog)
        
        # Data
        self.information = UNSET_TEXT
        self.default_title = title
        self.title = title
        self.template = template
        
        self.time = UNSET_TIMEOUT
        self.timer = None
        
        self.opened = False
        self.shown = False
        self.is_visible = False
    
    
    # Checkers -----------------------------------------------------------------
    def check_destroy(self):
        if self.dialog is not None:
            self.dialog.destroy()
            self.dialog = None
    
    def check_timer(self):
        if self.timer is not None:
            gobject.source_remove(self.timer)
            self.timer = None
    
    
    # Display ------------------------------------------------------------------
    def hide(self, timeout=UNSET_TIMEOUT):
        if timeout != UNSET_TIMEOUT:
            self.timer = gobject.timeout_add(timeout, self.hide)
            return False
        
        if self.opened:
            return False
        
        self.check_destroy()
        self.check_timer()
        self.is_visible = False
        self.box.hide()
    
    def show(self, button_label, info, title=None, timeout=UNSET_TIMEOUT,
             sound=False):
        
        self.check_destroy()
        
        # Data
        self.time = time.time()
        self.information = info
        self.title = self.default_title if title is None else title
        self.button.set_tooltip_text(lang.button_open if info is not None \
                                     else lang.button_remove)
        
        # Timer
        self.check_timer()
        if timeout != UNSET_TIMEOUT:
            self.timer = gobject.timeout_add(timeout, self.hide)
        
        # Show
        self.box.show()
        self.is_visible = True
        self.label.set_markup(button_label)
        
        # Play sound
        if self.gui.main.settings.is_true('infosound', True) \
           and ((info is None and not self.passive) or sound):
            
            play_sound(self.gui.main, 'theme:dialog-%s' % self.dtype)
        
        # Show GUI if not shown so the user does notices the message
        if not self.gui.is_shown:
            gobject.idle_add(self.gui.show_gui)
    
    def hide_dialog(self):
        self.opened = False
        self.gui.tray.toggle_menu(True)
        self.hide()
    
    def show_dialog(self, *args):
        self.check_destroy()
        self.check_timer()
        if self.information is None:
            self.hide()
            return False
        
        self.gui.tray.toggle_menu(False)
        self.opened = True
        info = time.strftime(self.template, time.localtime(self.time)) \
                             + self.information
        
        itype, msg = {
            'warning': (MESSAGE_WARNING, info),
            'error': (MESSAGE_ERROR, info),
            'information': (MESSAGE_INFO, self.information)
        }[self.dtype]
        self.dialog = MessageDialog(self.gui, itype, msg, self.title,
                                    close_callback = self.hide_dialog)

