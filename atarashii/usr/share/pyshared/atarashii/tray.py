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

from language import LANG as lang


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
        self.tooltip_markup = ''
        
        # Create Tray Icon
        gtk.StatusIcon.__init__(self)
        self.set_from_file(gui.main.get_image())
        self.set_visible(True)
        
        # FIXME This breaks in older gtk versions
        try:
            self.set_has_tooltip(True)
        
        # Try something else...
        except Exception:
            try:
                self.set_tooltip_text('...')
            
            # Didn't work either, last chance...
            except Exception:
                self.set_tooltip_text('WTF!')
        
        self.connect('activate', self.on_activate)
        self.connect('query-tooltip', self.on_tooltip)
        
        # Create Tray Menu
        self.menu = gtk.Menu()
        
        # Do we have a recent version of gtk?
        # This fixes a crash for version of gtk that don't have
        # gtk.ImageMenuItem.set_label()
        self.new_gtk_version = True
        try:
            menu_item = gtk.ImageMenuItem()
            menu_item.set_label('')
            
        except AttributeError:
            self.new_gtk_version = False
        
        # Refresh
        self.refresh_menu = self.add_menu(lang.menu_update, gtk.STOCK_REFRESH,
                                          self.gui.on_refresh)
            
        # Readall
        self.read_menu = self.add_menu(lang.menu_read, gtk.STOCK_OK,
                                       self.gui.on_read_all)
        
        # Settings
        self.settings_menu = self.add_menu(lang.menu_settings,
                                           gtk.STOCK_PREFERENCES,
                                           lambda *args:
                                           self.gui.on_settings(None, True))
    
        # About
        self.add_menu(lang.menu_about, gtk.STOCK_ABOUT,
                      lambda *args: self.gui.on_about(None, True))
        
        # Separator
        self.menu.append(gtk.SeparatorMenuItem())
        
        # Quit
        self.add_menu(lang.menu_quit, gtk.STOCK_QUIT, self.gui.on_quit)
        
        # Popup
        self.connect('popup-menu', self.on_popup, self.menu)
    
    
    def add_menu(self, text, image, callback):
        if self.new_gtk_version:
            item = gtk.ImageMenuItem(image)
            item.set_label(text)
            
        else:
            item = gtk.MenuItem(text)
        
        item.connect('activate', callback)
        self.menu.append(item)
        return item
    
    
    # Tooltip ------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def set_tooltip(self, status, twt = 0, msg = 0):
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
        
        self.tooltip_changed = True
    
    def set_tooltip_error(self, status, icon):
        self.tooltip_markup = '<span size="large"><b>%s</b></span>\n%s' \
                              % (lang.tray_title, status)
        
        self.tooltip_icon = icon
        self.tooltip_changed = True
    
    
    # Events -------------------------------------------------------------------
    # --------------------------------------------------------------------------
    def on_tooltip(self, icon, pos_x, pos_y, key, tip, *args):
        if self.tooltip_changed:
            if self.tooltip_icon != None:
                self.tooltip_img.set_from_stock(self.tooltip_icon, 6)
            
            elif self.tooltip_buf != None:
                self.tooltip_img.set_from_pixbuf(self.tooltip_buf)
            
            self.tooltip_label.set_markup(self.tooltip_markup)
            self.tooltip_icon = None
            self.tooltip_changed = False
        
        tip.set_custom(self.tooltip)
        return True
    
    def on_popup(self, widget, button, time, data = None):
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)
    
    def on_activate(self, *args):
        # Show GUI if started in tray
        if not self.gui.is_shown:
            self.gui.show_gui()
            return
        
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
            screen = self.gui.get_screen()
            pos = self.gui.get_position()
            pos = [pos[0], pos[1]]
            while pos[0] < 0:
                pos[0] += screen.get_width()
            
            while pos[0] > screen.get_width():
                pos[0] -= screen.get_width()
            
            while pos[1] < 0:
                pos[1] += screen.get_height()
            
            while pos[1] > screen.get_height():
                pos[1] -= screen.get_height()
            
            self.gui.main.settings['position'] = str(pos)
            self.gui.window_position = pos
            
            if self.on_screen() and not iconified:
                self.gui.hide()
            
            else:
                pos = self.gui.window_position
                self.gui.move(pos[0], pos[1])
                gobject.timeout_add(10, self.force_focus)
    
    def force_focus(self):
        self.gui.grab_focus()
        self.gui.present()
        return not self.gui.is_active()
    
    def on_screen(self):
        screen = self.gui.get_screen()
        size = self.gui.size_request()
        position = self.gui.get_position()
        if position[0] < 0 - size[0] or position[0] > screen.get_width() \
           or position[1] < 0 - size[1] or position[1] > screen.get_height():
           
            return False
            
        else:
            return True

