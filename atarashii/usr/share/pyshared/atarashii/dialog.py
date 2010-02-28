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


# Dialogs ----------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

from lang import lang
from notify import canNotify

class Dialog:
	resource = ""
	instance = None

	def __init__(self, gui):
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
			self.closeButton.connect("clicked", self.onClose)
			self.__class__.instance = self.dlg
			self.dlg.show_all()
			self.onInit()
			
		else:
			gobject.idle_add(lambda: self.__class__.instance.present())
	
	def onInit(self):
		pass
	
	def onClose(self, *args):
		self.__class__.instance = None
		self.dlg.hide()
		
	def get(self, widget):
		return self.gt.get_object(widget)
		
		
	
# About Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class AboutDialog(Dialog):
	resource = "about.glade"
	instance = None
	
	def onInit(self):
		self.dlg.set_title(lang.aboutTitle)
		self.closeButton.set_label(lang.aboutOKButton)
		self.get("title").set_markup('<span size="x-large"><b>Atarashii %s</b></span>' % self.main.version)
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
		


# Settings Dialog --------------------------------------------------------------
# ------------------------------------------------------------------------------
class SettingsDialog(Dialog):
	resource = "settings.glade"
	instance = None
	
	def onInit(self):
		self.dlg.set_title(lang.settingsTitle)
		self.closeButton.set_label(lang.settingsButton)

		# Username / Password
		self.get("usernamelabel").set_text(lang.settingsUsername)
		self.get("passwordlabel").set_text(lang.settingsPassword)
		username = self.get("username")
		password = self.get("password")
		
		username.set_text(self.settings['username'])
		password.set_text(self.settings['password'])
			
		oldusername = self.settings['username']
		oldpassword = self.settings['password']
		
		
		# Notifications
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
		notify.set_sensitive(canNotify)
		
		
		def toggle2():
			fileWidget.set_sensitive(sound.get_active())
		
		def toggle():
			sound.set_sensitive(notify.get_active() and canNotify)
			fileWidget.set_sensitive(notify.get_active() and sound.get_active())
		
		toggle()
		notify.connect("toggled", lambda *a: toggle())
		sound.connect("toggled", lambda *a: toggle2())
		
		
		# Save
		def save(*args):
			self.settings['soundfile'] = str(fileWidget.get_filename())
			self.settings['notify'] = notify.get_active()
			self.settings['sound'] = sound.get_active()
		
			self.settings['username'] = username.get_text().strip()
			self.settings['password'] = password.get_text().strip()
			
			# Login again if credentials have changed
			self.loginStatus = not self.settings.isset("username") or not self.settings.isset("password")
			if self.settings['username'] != oldusername or self.settings['password'] != oldpassword:
				if not self.loginStatus:
	 				self.main.login()
	 			
	 			else:
	 				self.main.logout()
			
			self.onClose()
		
		self.closeButton.connect("clicked", save)
		
		
# Error Dialog -----------------------------------------------------------------
# ------------------------------------------------------------------------------
class ErrorDialog(Dialog):
	resource = "error.glade"
	instance = None
	
	def __init__(self, gui, description):
		self.description = description
		Dialog.__init__(self, gui)
	
	def onInit(self):
		self.dlg.set_title(lang.errorTitle)
		self.closeButton.set_label(lang.errorButton)
		
		self.get("text").set_size_request(160, -1)
		self.get("text").set_text(self.description)
			
			
			
			
# Warning Dialog ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class WarningDialog(Dialog):
	resource = "warning.glade"
	instance = None
	
	def __init__(self, gui, description):
		self.description = description
		Dialog.__init__(self, gui)
	
	def onInit(self):
		self.dlg.set_title(lang.warningTitle)
		self.closeButton.set_label(lang.warningButton)
		
		self.get("text").set_size_request(160, -1)
		self.get("text").set_text(self.description)
			
	
	
