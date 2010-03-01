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


# GUI --------------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import pango
import gobject

import calendar
import time
import math

import html
import tray
import text
import dialog
from lang import lang


class GUI(gtk.Window):
	def __init__(self, main):
		# Setup
		self.main = main
		gtk.Window.__init__(self, gtk.WINDOW_TOPLEVEL)		
		self.set_title("Atarashii")
		self.hide_on_delete()
		self.set_border_width(2)
		self.set_size_request(280, 400)
		self.set_icon_from_file(main.getImage())
		
		
		# Load Components
		gt = gtk.Builder()
		gt.add_from_file(main.getResource("main.glade"))
		frame = gt.get_object("frame")
		self.add(frame)
		
		
		# Link Components
		self.refreshButton = gt.get_object("refresh")
		self.refreshButton.connect("clicked", self.onRefresh)
		self.refreshButton.set_tooltip_text(lang.toolRefresh)
		
		self.historyButton = gt.get_object("history")
		self.historyButton.connect("clicked", self.onHistory)
		self.historyButton.set_tooltip_text(lang.toolHistory)
		
		self.readButton = gt.get_object("read")
		self.readButton.connect("clicked", self.onRead)
		self.readButton.set_tooltip_text(lang.toolRead)
		
		# Settings Button
		self.settingsButton = gt.get_object("settings")
		self.settingsButton.connect("toggled", lambda *args: self.onSettings(False))
		self.settingsButton.set_tooltip_text(lang.toolSettings)
		self.settingsToggle = False
		
		# About Button
		self.aboutButton = gt.get_object("about")
		self.aboutButton.connect("toggled", lambda *args: self.onAbout(False))
		self.aboutButton.set_tooltip_text(lang.toolAbout)
		self.aboutToggle = False
		
		self.quitButton = gt.get_object("quit")
		self.quitButton.connect("clicked", self.onQuit)
		self.quitButton.set_tooltip_text(lang.toolQuit)
		
		self.infoLabel = gt.get_object("label")
		
		self.htmlScroll = gt.get_object("htmlscroll")		
		self.textScroll = gt.get_object("textscroll")
		
		# Text Input
		self.text = text.TextInput(self)
		self.textScroll.add(self.text)
		
		# HTML
		self.html = html.HTML(self.main, self)
		self.htmlScroll.add(self.html)
		self.htmlScroll.set_shadow_type(gtk.SHADOW_IN)
		
		self.content = gt.get_object("content")
		self.content.set_border_width(2)
		
		# BArs
		self.toolbar = gt.get_object("toolbar")
		self.progress = gt.get_object("progressbar")
		self.status = gt.get_object("statusbar")
		
		
		# Restore Position & Size
		if main.settings.isset("position"):
			self.windowPosition = main.settings['position'][1:-1].split(",")
			self.move(int(self.windowPosition[0]), int(self.windowPosition[1]))
		
		if main.settings.isset("size"):
			size = main.settings['size'][1:-1].split(",")
			self.resize(int(size[0]), int(size[1]))
		else:
			self.resize(280,400)
		
		
		# Tray
		self.tray = tray.TrayIcon(self)
		
		
		# Events
		self.connect("delete_event", self.deleteEvent)
		self.connect("destroy", self.destroyEvent)
		self.connect("window-state-event", self.stateEvent)
		self.initEvent = self.connect("expose-event", self.drawEvent)
		
		
		# Dialogs
		self.aboutDialog = None
		self.settingsDialog = None
		
		# Variables
		self.windowPosition = None
		self.minimized = False
				
		# Statusbar Updater
		self.updateStatus()
		gobject.timeout_add(1000, lambda: self.updateStatus())
				
		# Show
		self.show_all()
		self.showInput()
	
	
	# Main Functions -----------------------------------------------------------
	# --------------------------------------------------------------------------
	def showInput(self):
		self.progress.hide()
		self.textScroll.show()
		self.text.resize()
		self.refreshButton.set_sensitive(True)
	
	def showProgress(self):
		def progressActivity():
			self.progress.pulse()
			return self.main.isSending or self.main.isConnecting or self.main.isLoadingHistory
	
		self.progress.set_fraction(0.0)
		self.progress.show()
		self.infoLabel.hide()
		self.textScroll.hide()
		gobject.timeout_add(100, lambda: progressActivity())
	
	def hideAll(self, progress = True):
		if progress:
			self.progress.hide()
		
		self.textScroll.hide()
		self.refreshButton.set_sensitive(False)
		self.readButton.set_sensitive(False)
		self.historyButton.set_sensitive(False)
	
	# Update Statusbar
	def updateStatus(self, once = False):
		if self.text.hasTyped:
			pass
	
		elif self.main.isReconnecting:
			wait = self.main.refreshTimeout - (calendar.timegm(time.gmtime()) - self.main.reconnectTime)
			if wait < 60:
				self.setStatus(lang.statusReconnectSeconds % wait)
		
			elif wait < 105:
				self.setStatus(lang.statusReconnectMinute)
			
			else:
				self.setStatus(lang.statusReconnectMinutes % math.ceil(wait / 60.0))
	
		elif self.main.isLoadingHistory:
			self.setStatus(lang.statusLoadHistory)
	
		elif self.main.isConnecting:
			self.setStatus(lang.statusConnecting % self.main.settings['username'])
			
		elif self.main.loginError:
			self.setStatus(lang.statusError)
		
		elif not self.main.loginStatus:
			self.setStatus(lang.statusLogout)
		
		elif self.main.isUpdating:
			self.refreshButton.set_sensitive(False)
			self.readButton.set_sensitive(False)
			self.setStatus(lang.statusUpdate)
		
		elif self.main.refreshTimeout == -1:
			self.setStatus(lang.statusConnected)
		
		elif (not self.text.isTyping or not self.text.hasFocus) and not self.main.isSending:
			wait = self.main.refreshTimeout - (calendar.timegm(time.gmtime()) - self.main.refreshTime)
			if wait == 0:
				self.refreshButton.set_sensitive(False)
				self.readButton.set_sensitive(False)
				self.setStatus(lang.statusUpdate)
			
			elif wait == 1:
				self.setStatus(lang.statusOneSecond)
			
			else:
				if wait < 60:
					self.setStatus(lang.statusSeconds % wait)
				
				elif wait < 105:
					self.setStatus(lang.statusMinute)
					
				else:
					self.setStatus(lang.statusMinutes % math.ceil(wait / 60.0))
	
		if once:
			return False
			
		else:
			return True
	
	def setStatus(self, status):
		self.status.pop(0)
		self.status.push(0, status)	
	
	
	# Info Label ---------------------------------------------------------------
	# --------------------------------------------------------------------------
	def setLabel(self):
		if self.main.replyUser == "" and self.main.retweetUser == "":
			self.infoLabel.set_markup("")
			self.infoLabel.hide()
			
		elif self.main.retweetUser != "":
			self.setLabelText(lang.labelRetweet % self.main.retweetUser)
			self.infoLabel.show()			
			
		elif self.main.replyText != "":
			self.setLabelText(lang.labelReplyText % self.main.replyText)
			self.infoLabel.show()	
			
		else:
			self.setLabelText(lang.labelReply % self.main.replyUser)
			self.infoLabel.show()
	
	def setLabelText(self, text):
		# Get Font Width
		font = self.infoLabel.create_pango_context().get_font_description()
		layout = self.infoLabel.create_pango_layout("")
		layout.set_markup(text)
		layout.set_font_description(font)
		
		# Truncate till it fits
		width = self.infoLabel.get_allocation()[2]
		cur = layout.get_pixel_size()[0]
		if cur > width:
			while cur > width:
				text = text[:-3]
				layout.set_markup(text + "...")
				cur = layout.get_pixel_size()[0]
			
			self.infoLabel.set_markup(text + "...")
		
		else:
			self.infoLabel.set_markup(text)
	
	
	# Error & Warning ----------------------------------------------------------
	# --------------------------------------------------------------------------
	def showError(self, error):
 		code = error.response.status
 		
		# Ratelimit error
 		if code == 400:
 			self.refreshButton.set_sensitive(False)
 			rateError = self.main.reconnect()
 			
 		else:
 			rateError = ""
 		
 		try:
	 		description = {
	 			404 : lang.errorLogin,
	 			401 : lang.errorLogin,
	 			400 : rateError,
	 			500 : lang.errorTwitter,
	 			502 : lang.errorDown,
	 			503 : lang.errorOverload
	 		}[code]
	 	
	 	except:
	 		description = lang.errorInternal % str(detail)
	 	
	 	dialog.ErrorDialog(self, description)
	
	def showWarning(self, limit):
		dialog.WarningDialog(self, lang.warningText % limit)
	
	
	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def getHeight(self, widget):
		size = widget.get_allocation()
		return size[3] - size[0]
	
	
	# Handlers -----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def onRefresh(self, *args):
		self.main.updater.refreshNow = True
	
	def onHistory(self, *args):
		gobject.idle_add(lambda: self.html.clear())
	
	def onRead(self, *args):
		gobject.idle_add(lambda: self.html.read())
	
	def onSettings(self, menu):
		if not self.settingsToggle:
			self.settingsToggle = True
			if self.settingsButton.get_active() and not self.settingsDialog:
				self.settingsDialog = dialog.SettingsDialog(self)
		
			elif menu and not self.settingsDialog:
				self.settingsDialog = dialog.SettingsDialog(self)
				self.settingsButton.set_active(True)
			
		
			elif menu and self.settingsDialog:
				self.settingsDialog.onClose()
				self.settingsButton.set_active(False)
		
			elif self.settingsDialog:
				self.settingsDialog.onClose()
				
			self.settingsToggle = False
	
	def onAbout(self, menu):
		if not self.aboutToggle:
			self.aboutToggle = True
			if self.aboutButton.get_active() and not self.aboutDialog:
				self.aboutDialog = dialog.AboutDialog(self)
		
			elif menu and not self.aboutDialog:
				self.aboutDialog = dialog.AboutDialog(self)
				self.aboutButton.set_active(True)
		
			elif menu and self.aboutDialog:
				self.aboutDialog.onClose()
				self.aboutButton.set_active(False)		
		
			elif self.aboutDialog:
				self.aboutDialog.onClose()
			
			self.aboutToggle = False
	
	def onQuit(self, widget = None, data = None):
 		if data:
 			data.set_visible(False)
 		
 		self.main.quit()
	
	
	# Events -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def deleteEvent(self, widget, event, data=None):
		self.windowPosition = self.get_position()
		self.main.settings['position'] = str(self.windowPosition)
		self.hide()
		return True
	
	def destroyEvent(self, widget, data=None):
		self.windowPosition = self.get_position()
		self.main.settings['position'] = str(self.windowPosition)
		self.hide()
		return True
		
	def stateEvent(self, window, event):
		if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
			self.minimized = event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED
	
	def drawEvent(self, *args):
		self.disconnect(self.initEvent)
		gobject.idle_add(lambda: self.main.onInit())
	
	# Show and Stuff -----------------------------------------------------------
	# --------------------------------------------------------------------------
	def forceFocus(self):
		self.grab_focus()
		self.present()
		return not self.is_active()
	
	def onScreen(self):
		screen = self.get_screen()
		size = self.size_request()
		position = self.get_position()
		if position[0] < 0 - size[0] or position[0] > screen.get_width() \
			or position[1] < 0 - size[1] or position[1] > screen.get_height():
			return False
			
		else:
			return True

	
