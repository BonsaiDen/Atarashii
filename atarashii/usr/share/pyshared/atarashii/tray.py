#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Tray Icon --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject
from lang import lang


class TrayIcon(gtk.StatusIcon):
	def __init__(self, gui):
		self.gui = gui
		
		# Create Tray Icon
		gtk.StatusIcon.__init__(self)
		
		self.set_from_file(gui.main.getImage())
		self.set_tooltip("Atarashii")
		self.set_visible(True)
		self.connect("activate", self.onActivate)
		
		# Create Tray Menu
		menu = gtk.Menu()
		
		# Refresh
		menuItem = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
		menuItem.set_label(lang.menuUpdate)
		menuItem.connect('activate', self.gui.onRefresh, self)	
		menu.append(menuItem)
		
		# Settings
		menuItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
		menuItem.set_label(lang.menuSettings)
		menuItem.connect('activate', self.gui.onSettings, self)	
		menu.append(menuItem)
		
		# Abvout
		menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		menuItem.set_label(lang.menuAbout)
		menuItem.connect('activate', self.gui.onAbout, self)	
		menu.append(menuItem)
		
		# Separator
		menu.append(gtk.SeparatorMenuItem())
		
		# Quit
		menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menuItem.set_label(lang.menuExit)
		menuItem.connect('activate', self.gui.onQuit, self)	
		menu.append(menuItem)
		
		# Popup
		self.connect("popup-menu", self.onPopup, menu)	


	# Events -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def onPopup(self, widget, button, time, data = None):
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, None, 3, time)
	
 	def onActivate(self, *args):
 		if self.gui.minimized:
 			self.gui.deiconify()
 			iconified = True
 		
 		else:
 			iconified = False
 	
 		# Show!
		if not self.gui.get_property("visible"):
			self.gui.present()
			self.gui.move(*self.gui.windowPosition)
			gobject.idle_add(lambda: self.gui.grab_focus())
	
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
			self.gui.windowPosition = pos
			
			if self.gui.onScreen() and not iconified:
				self.gui.hide()
				
			else:
				self.gui.move(*self.gui.windowPosition)
				gobject.timeout_add(10, lambda: self.gui.forceFocus())
	

