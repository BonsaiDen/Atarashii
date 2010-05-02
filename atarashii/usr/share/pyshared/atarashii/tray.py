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


# Tray Icon --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from utils import menu_escape
from lang import LANG as lang

from constants import UNSET_TOOLTIP, UNSET_USERNAME, UNSET_LABEL
from constants import ST_TRAY_WARNING


class TrayIcon(gtk.StatusIcon):
    def __init__(self, gui):
        self.gui = gui
        self.main = gui.main
        
        # Tooltip
        gtb = gtk.Builder()
        gtb.add_from_file(self.main.get_resource('tooltip.glade'))
        self.tooltip = gtb.get_object('tooltip')
        self.tooltip_label = gtb.get_object('label')
        self.tooltip_img = gtb.get_object('image')
        self.tooltip_img_file = None
        self.tooltip.show_all()
        
        self.tooltip_changed = False
        self.tooltip_icon = None
        self.tooltip_buf = None
        self.tooltip_markup = UNSET_TOOLTIP
        
        # Create Tray Icon
        self.fake_window = None
        gtk.StatusIcon.__init__(self)
        self.set_from_file(self.main.get_image())
        self.set_visible(True)
        
        # FIXME This breaks in older gtk versions
        try:
            self.set_has_tooltip(True)
        
        # Try something else...
        except AttributeError:
            try:
                self.set_tooltip('...')
            
            # Didn't work either, last chance...
            except AttributeError:
                try:
                    self.set_tooltip_text('WTF!')
                
                # OK no tooltips...
                except AttributeError:
                    pass
        
        self.connect('activate', self.on_activate)
        self.connect('query-tooltip', self.on_tooltip)
        
        # Create Tray Menu
        self.accel = gtk.AccelGroup()
        self.gui.add_accel_group(self.accel)
        self.menu = gtk.Menu()
        
        # Refresh
        self.refresh_menu = self.add_menu(lang.menu_update, gtk.STOCK_REFRESH,
                                          'r', self.gui.on_refresh_all)
        
        # Readall
        self.read_menu = self.add_menu(lang.menu_read, gtk.STOCK_OK, 'm',
                                       self.gui.on_read_all)
        
        # Accounts
        self.account_menu_item = self.add_menu(lang.menu_accounts,
                                               gtk.STOCK_DIALOG_AUTHENTICATION)
        
        self.account_menu = gtk.Menu()
        self.account_menu_item.set_submenu(self.account_menu)
        
        # Separator
        self.menu.append(gtk.SeparatorMenuItem())
        
        # Settings
        self.add_menu(lang.menu_settings, gtk.STOCK_PREFERENCES, 'p',
                                          lambda *args:
                                          self.gui.on_settings(None, True))
        
        # About
        self.add_menu(lang.menu_about, gtk.STOCK_ABOUT, None,
                      lambda *args: self.gui.on_about(None, True))
        
        # Separator
        self.menu.append(gtk.SeparatorMenuItem())
        
        # Quit
        self.add_menu(lang.menu_quit, gtk.STOCK_QUIT, 'q', self.gui.on_quit)
        
        # Popup
        self.menu.show_all()
        self.update_account_menu()
        self.connect('popup-menu', self.on_popup)
    
    
    # Menus --------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def add_menu(self, text, image, accel_key=None, callback=None):
        try:
            item = gtk.ImageMenuItem(image)
            item.set_label(text)
        
        except AttributeError:
            item = gtk.MenuItem(text)
        
        # Add accelerator
        if accel_key is not None:
            item.add_accelerator('activate', self.accel, ord(accel_key),
                                 gtk.gdk.CONTROL_MASK, gtk.ACCEL_VISIBLE)
        
        if callback is not None:
            item.connect('activate', callback)
        
        self.menu.append(item)
        return item
    
    def update_account_menu(self):
        for i in self.account_menu.get_children():
            self.account_menu.remove(i)
        
        self.logout_item = gtk.MenuItem(lang.menu_logout, ord('o'))
        self.logout_item.add_accelerator('activate', self.accel, ord('o'),
                                         gtk.gdk.CONTROL_MASK,
                                         gtk.ACCEL_VISIBLE)
        
        self.logout_item.connect('activate', self.main.logout)
        
        self.secure_logout_item = gtk.MenuItem(lang.menu_secure_logout)
        self.secure_logout_item.add_accelerator('activate', self.accel,
                                ord('o'),
                                gtk.gdk.CONTROL_MASK | gtk.gdk.SHIFT_MASK,
                                gtk.ACCEL_VISIBLE)
        
        self.secure_logout_item.connect('activate', self.main.secure_logout)
        
        self.account_menu.append(self.logout_item)
        self.account_menu.append(self.secure_logout_item)
        self.account_menu.append(gtk.SeparatorMenuItem())
        
        group = None
        self.selected_account = None
        account_list = self.main.settings.get_accounts()
        for i in account_list:
            item = gtk.RadioMenuItem(group, menu_escape(i))
            if group is None:
                group = item
            
            item.connect('toggled', self.on_account_select, i)
            self.account_menu.append(item)
            
            # Select
            if i == self.main.username:
                self.selected_account = item
        
        self.activate_menu(True)
        self.account_menu.show_all()
        if self.selected_account is not None:
            self.selected_account.set_active(True)
    
    def activate_menu(self, mode):
        if self.gui.settings_dialog is not None:
            self.gui.settings_dialog.activate(mode)
        
        if len(self.account_menu.get_children()) == 0:
            self.account_menu_item.set_sensitive(False)
            mode = False
        
        self.logout_item.set_sensitive(mode)
        self.secure_logout_item.set_sensitive(mode)
        if self.main.username == UNSET_USERNAME:
            self.logout_item.set_sensitive(False)
            self.secure_logout_item.set_sensitive(False)
        
        if self.selected_account is not None:
            self.selected_account.set_active(False)
        
        for pos, item in enumerate(self.account_menu.get_children()):
            if pos > 1:
                item.set_sensitive(mode)
    
    def toggle_menu(self, mode):
        for i in self.menu.get_children():
            i.set_sensitive(mode)
    
    def on_account_select(self, item, username):
        if username != self.main.username and item.get_active():
            if self.gui.settings_dialog is not None:
                self.gui.settings_dialog.hideall(True)
            
            self.selected_account = item
            self.activate_menu(False)
            self.main.login(username)
    
    
    # Tooltip ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_tooltip(self, status, twt=0, msg=0):
        if self.main.status(ST_TRAY_WARNING):
            return False
        
        text = []
        if twt > 0:
            text.append((lang.tray_tweets if twt > 1 \
                         else lang.tray_tweet) % twt)
        
        if msg > 0:
            text.append((lang.tray_messages if msg > 1 \
                         else lang.tray_message) % msg)
        
        self.tooltip_markup = '<span size="large"><b>%s</b></span>\n%s\n%s' \
                              % (lang.tray_title, status, '\n'.join(text))
        
        img = self.main.get_user_picture()
        if img != self.tooltip_img_file:
            self.tooltip_buf = gtk.gdk.pixbuf_new_from_file_at_size(img, 48, 48)
            self.tooltip_img_file = img
        
        if twt + msg > 0:
            self.set_from_pixbuf(self.render_stock_overlay(gtk.STOCK_OK))
        
        else:
            self.set_from_file(self.main.get_image())
        
        self.tooltip_icon = None
        self.tooltip_changed = True
    
    def set_tooltip_error(self, status, icon):
        self.tooltip_markup = '<span size="large"><b>%s</b></span>\n%s' \
                              % (lang.tray_title, status)
        
        self.tooltip_icon = icon
        self.set_from_pixbuf(self.render_stock_overlay(icon))
        self.tooltip_changed = True
    
    def render_stock_overlay(self, stock):
        # Get icons
        pixbuf = self.gui.render_icon(stock, gtk.ICON_SIZE_DIALOG)
        size = int(pixbuf.get_width() * 1.6)
        icon = gtk.gdk.pixbuf_new_from_file_at_size(self.main.get_image(),
                                                 size, size)
        
        # If the GUI isn't visible we need to create a fake window for colors
        # and stuff
        window = self.gui.window
        if window is None:
            if not self.fake_window:
                self.fake_window = gtk.Window()
                self.fake_window.show()
                self.fake_window.hide()
            
            context = self.fake_window.get_style().bg_gc[gtk.STATE_NORMAL]
            window = self.fake_window.window
        
        else:
            context = self.gui.get_style().bg_gc[gtk.STATE_NORMAL]
        
        # Create a pixmap and clear it
        pixmap = gtk.gdk.Pixmap(window, size, size)
        pixmap.draw_rectangle(context, True, 0, 0, size, size)
        
        # Draw the icons
        pixmap.draw_pixbuf(None, icon, 0, 0, 0, 0)
        pixmap.draw_pixbuf(None, pixbuf, 0, 0, size - pixbuf.get_width(),
                                               size - pixbuf.get_height())
        
        # Convert the thing back to a pixbuf
        buf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, size, size)
        buf.get_from_drawable(pixmap, window.get_colormap(), 0, 0, 0, 0,
                              size, size)
        
        return buf
    
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_tooltip(self, icon, pos_x, pos_y, key, tip, *args):
        if self.tooltip_changed:
            if self.tooltip_icon is not None:
                self.tooltip_img.set_from_stock(self.tooltip_icon,
                                                gtk.ICON_SIZE_DIALOG)
            
            elif self.tooltip_buf is not None:
                self.tooltip_img.set_from_pixbuf(self.tooltip_buf)
            
            self.tooltip_label.set_markup(self.tooltip_markup)
            self.tooltip_icon = None
            self.tooltip_changed = False
        
        tip.set_custom(self.tooltip)
        return True
    
    def on_popup(self, tray, button, time):
        if button == 3:
            rect = self.get_geometry()[1]
            root_pos = (int(rect[0]), int(rect[1] + rect[3]), True)
            gobject.idle_add(self.menu.popup, None, None, lambda *arg: root_pos,
                             button, time)
    
    def on_activate(self, *args):
        # Show GUI if started in tray
        if not self.gui.is_shown:
            self.gui.show_gui()
            return False
        
        # Toggle minimized
        if self.gui.minimized:
            self.gui.deiconify()
            iconified = True
        
        else:
            iconified = False
        
        # Show!
        if not self.gui.get_property('visible'):
            self.gui.present()
            pos = self.gui.window_position
            self.gui.move(pos[0], pos[1])
            gobject.idle_add(self.gui.grab_focus)
        
        # Hide or move to other screen
        else:
            pos = self.gui.get_normalized_position()
            self.gui.main.settings['position'] = str(pos)
            self.gui.window_position = pos
            if self.gui.on_screen() and not iconified and self.gui.is_active():
                self.gui.hide()
            
            else:
                self.gui.force_present()

