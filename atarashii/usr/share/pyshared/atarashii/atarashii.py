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

# TODO direct messages by a toggle button
# TODO Use of streaming API?
# TODO Fix random crashes(maybe webkit) X Error/GDK Error due to clipping
# TODO Cleanup access to the html widget
# TODO Fix memory leak in the html view(seems to come straigt from libwebkit...)


# DBUS Integration -------------------------------------------------------------
# ------------------------------------------------------------------------------
import dbus, dbus.service
import sys

def isRunning(name):
	return name in dbus.Interface(dbus.SessionBus().get_object(
    	"org.freedesktop.DBus", "/org/freedesktop/DBus"),
      		"org.freedesktop.DBus").ListNames()

if isRunning('org.Atarashii'):
	print "Atrashii is already running"
	sys.exit(2)

DBUS = dbus.SessionBus()
DBUSNAME = dbus.service.BusName('org.Atarashii', bus = DBUS)


# Main Application -------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gnome
import gtk.glade
import gobject
import pango
import os
import calendar
import time
import math
import re

gtk.gdk.threads_init()

# Modules
from lang import lang
import html
import updater
import input
import settings
import login
import send
from notify import canNotify


class Atarashii:
	def delete_event(self, widget, event, data=None):
		self.position = self.window.get_position()
		self.settings['position'] = str(self.position)
		self.window.hide()
		return True
	
	def destroy(self, widget, data=None):
		self.position = self.window.get_position()
		self.settings['position'] = str(self.position)
		self.window.hide()
		return True
		
	def state(self, window, event):
		if event.changed_mask & gtk.gdk.WINDOW_STATE_ICONIFIED:
			self.minimized = event.new_window_state & gtk.gdk.WINDOW_STATE_ICONIFIED
	
	# Initiate
	def __init__(self, version, debug = None):		
		# Version
		self.version = version
	
		# Settings
		self.loadSettings()
	
		# Stuff
		self.minimized = False
		
		# Debugging
		if debug != None:
			self.img = os.path.join(debug, '/usr/share/icons/atarashii.png')
			self.resources = os.path.join(debug, "/usr/share/atarashii")
			
		else:
			self.img = '/usr/share/icons/atarashii.png'
			self.resources = "/usr/share/atarashii"
		
		self.update = -1
		self.replyRegex = re.compile('@([^\s]+)\s.*')
		self.loadTweets = 20
		self.maxTweets = 200
		self.reply_user = ""
		self.reply_id = -1
		self.retweet_num = -1
		self.retweet_user = ""
		self.typing = False
		self.hasTyped = False
		self.inputSize = 0
		self.inputError = None
		self.height = None
		self.customSize = False
		self.sending = False
		self.textFocus = False
		self.change = False
		self.oldsize = None
		self.defaultBG = None
		self.defaultFG = None
		self.connecting = False
		self.connected = False
		self.rateWarning = False
		self.settingsOpen = False
		self.aboutOpen = False
		self.waitForReconnect = False
		self.reconnectTime = 0
		self.isLoggedOut = not self.settings.isset("username") or not self.settings.isset("password")
		self.lastStatusID = None
		
		# Main Window
		self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
	#	self.window.set_property("skip-taskbar-hint", True)
		self.window.set_title("Atarashii")
		
		self.window.hide_on_delete()
		self.window.connect("delete_event", self.delete_event)
		self.window.connect("destroy", self.destroy)
		self.window.connect("window-state-event", self.state)
		self.initiated = self.window.connect("expose-event", self.draw)
		self.window.set_border_width(2)
		self.window.set_size_request(280, 400)
		self.window.set_icon_from_file(self.img)
		
		# Restore Position and size
		if self.settings.isset("position"):
			pos = self.settings['position'][1:-1].split(",")
			self.window.move(int(pos[0]), int(pos[1]))
		
		if self.settings.isset("size"):
			size = self.settings['size'][1:-1].split(",")
			self.window.resize(int(size[0]), int(size[1]))
		else:
			self.window.resize(280,400)
		
		# Toolbar
		self.toolbar = self.createToolbar()
		self.toolbar.set_icon_size(gtk.ICON_SIZE_SMALL_TOOLBAR)
		
		# Vbox
		self.box = gtk.VBox()
		self.box.pack_start(self.toolbar, False, True)
		
		# Split
		self.split = gtk.VBox(False, 5)
		self.split.set_border_width(2)
		
		# HTML View
		self.html = html.HTML(self)
		
		# Text Input
		self.label = gtk.Label()
		self.label.set_use_markup(True)
		self.label.set_alignment(0.0, 0.0)
		
		self.input = input.TextInput()
		self.input.connect("submit", self.submit)
		self.input.get_buffer().connect("changed", self.changed)
		self.input.connect("focus-in-event", self.textfocus)
		self.input.connect("focus-out-event", self.notextfocus)
		self.defaultFG = self.input.get_style().text[gtk.STATE_NORMAL]
		
		self.scroll = gtk.ScrolledWindow()
		self.scroll.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
		self.scroll.add(self.input)
		self.scroll.set_shadow_type(gtk.SHADOW_IN)
		
		self.split.pack_start(self.html.scroll, True, True)
		self.split.pack_start(self.label, False, True)
		self.split.pack_start(self.scroll, False, True)
		
		self.progress = gtk.ProgressBar()
		self.split.pack_start(self.progress, False, True)
		
		# Status
		self.status = gtk.Statusbar()
		
		# Window
		self.box.pack_start(self.split, True, True)
		self.box.pack_start(self.status, False)
		self.window.add(self.box)
		self.window.show_all()
		self.label.hide()
		self.activateGUI(False)
		
		# Resize Text Area
		self.sizeInput()

	
	# GUI Helpers --------------------------------------------------------------
	# --------------------------------------------------------------------------
	def activateGUI(self, mode):
		self.updateButton.set_sensitive(mode)
		self.input.set_sensitive(mode)
		if self.html.historyLoaded:
			self.clearButton.set_sensitive(mode)
		else:
			self.clearButton.set_sensitive(False)
			
		if mode == False:
			self.readButton.set_sensitive(False)
	
	def showProgess(self):
		self.progress.pulse()
		return self.sending or self.connecting or self.updater.loadOlder != -1
	
	# Update Statusbar
	def updatestatus(self, time, text = None):
		if text != None:
			self.setStatus(text)
	
		elif (not self.typing or not self.textFocus) and not self.sending:
			if time == 0:
				self.readButton.set_sensitive(False)
				self.updateButton.set_sensitive(False)
				self.setStatus(lang.statusUpdate)
		
			elif time == 1:
				self.setStatus(lang.statusOneSecond)
		
			else:
				if time < 60:
					self.setStatus(lang.statusSeconds % time)
				
				elif time < 105:
					self.setStatus(lang.statusMinute)
					
				else:
					self.setStatus(lang.statusMinutes % math.ceil(time / 60.0))
			
			#self.window.queue_draw()
			
	def setStatus(self, status):
		self.status.pop(0)
		self.status.push(0, status)	
	

	# Input Handling -----------------------------------------------------------
	# --------------------------------------------------------------------------
	def fixSize(self):
		self.inputError = self.inputSize - self.getHeight(self.input)
		self.sizeInput()
		self.loosefocus()
	
	def setLabelText(self, text):
		font = self.label.create_pango_context().get_font_description()
		layout = self.label.create_pango_layout("")
		layout.set_markup(text)
		layout.set_font_description(font)
		
		width = self.label.get_allocation()[2]
		cur = layout.get_pixel_size()[0]
		if cur > width:
			while cur > width:
				text = text[:-3]
				layout.set_markup(text + "...")
				cur = layout.get_pixel_size()[0]
			
			self.label.set_markup(text + "...")
		
		else:
			self.label.set_markup(text)
	
	def sizeInput(self):
		# Reply Info?
		if self.reply_user == "" and self.retweet_user == "":
			self.label.set_markup("")
			self.label.hide()
			
		elif self.retweet_user != "":
			self.setLabelText(lang.labelRetweet % self.retweet_user)
			self.label.show()			
			
		elif self.reply_text != "":
			self.setLabelText(lang.labelReplyText % self.reply_text)
			self.label.show()	
			
		else:
			self.setLabelText(lang.labelReply % self.reply_user)
			self.label.show()
		
		textSize = self.input.create_pango_context().get_font_description().get_size() / pango.SCALE
		if self.textFocus:
			lines = 5
		
		else:
			lines = 1
		
		# Resize
		height = self.getHeight(self.split)
		self.inputSize = (textSize + 4) * lines
		if self.inputError != None:
			self.inputSize += self.inputError
		
		self.scroll.set_size_request(0, self.inputSize)
		
		if lines == 1:
			self.progress.set_size_request(0, self.inputSize)
		
		# Detect Error
		if self.inputError == None:
			gobject.idle_add(lambda: self.fixSize())
		
		elif self.isLoggedOut:
			self.progress.hide()
			self.scroll.hide()
	
	def getHeight(self, widget):
		size = widget.get_allocation()
		return size[3] - size[0]
	
	
	# Reply and Retweet --------------------------------------------------------
	# --------------------------------------------------------------------------
	def reply(self, num = -1):
		self.change = True
		self.input.grab_focus()
		buf = self.input.get_buffer()
		f, l = buf.get_bounds()
		text = buf.get_text(f, l)
		
		if num != -1:
			self.reply_text = self.html.tweets[num][0].text
	
		if self.retweet_num > -1:
			self.retweet_num = -1
			text = ""
		
		if text[0:1] == "@":
			p = text.find(" ")
			if p == -1:
				p = len(text)
		
			text = ("@%s " % self.reply_user) + text[p + 1:]
	
		else:
			text = ("@%s " % self.reply_user) + text
	
		buf.set_text(text)
		self.change = False
		self.checkText(len(text))
		self.changed(buf)
		self.input.modify_text(gtk.STATE_NORMAL, self.defaultFG)

	# Retweet Something
	def retweet(self):
		self.input.grab_focus()
		self.reply_user = ""
		self.reply_id = -1
		tweet = self.html.tweets[self.retweet_num][0]
		buf = self.input.get_buffer()
		f, l = buf.get_bounds()
		text = buf.get_text(f, l)
		self.change = True
		text = "RT: @%s: %s" % (tweet.user.screen_name, tweet.text)
		self.retweet_user = tweet.user.screen_name
		buf.set_text(text)
		
		self.change = False
		self.checkText(len(text))
		self.changed(buf)
		self.input.modify_text(gtk.STATE_NORMAL, self.defaultFG)
	
	
	# Submit and change --------------------------------------------------------
	# --------------------------------------------------------------------------
	def submit(self, input):
		buf = input.get_buffer()
		f, l = buf.get_bounds()
		text = buf.get_text(f, l)
		if len(text) <= 140 and text.strip() != "":
			self.sending = True
			self.input.set_sensitive(False)
			self.scroll.hide()
			self.progress.set_fraction(0.0)
			self.progress.show()
			gobject.timeout_add(100, lambda: self.showProgess())

			if self.reply_user != "":
				self.setStatus(lang.statusReply % self.reply_user)
				
			elif self.retweet_user != "":
				self.setStatus(lang.statusRetweet % self.retweet_user)
				
			else:
				self.setStatus(lang.statusSend)
			
			sender = send.Send(self, text)
			sender.start()
	
	# Textbox Change Event
	def changed(self, buf):
		f, l = buf.get_bounds()
		text = buf.get_text(f, l)
		if text.strip()[0:1] != "@" and not self.change:
			self.reply_text = ""
			self.reply_user = ""
			self.reply_id = -1
			
		if text.strip() == "":
			buf.set_text("")
			text = ""
			
		if len(text) == 0 and not self.change:
			self.reply_text = ""
			self.reply_user = ""
			self.reply_id = -1
			self.retweet_num = -1
			self.retweet_user = ""
		
		# @ Reply
		at = self.replyRegex.match(text)
		if at != None:
			if self.reply_id == -1:
				self.reply_user = at.group(1)
			else:
				if at.group(1) != self.reply_user:
					self.reply_user = at.group(1)
					self.reply_id = -1
					self.reply_text = ""
			
		elif self.reply_id == -1:
			self.reply_user = ""
		
		# Resize
		self.sizeInput()	
		self.typing = len(text) > 0
		if self.typing:
			self.hasTyped = self.textFocus
			if self.textFocus:
				self.input.modify_text(gtk.STATE_NORMAL, self.defaultFG)
				if len(text) <= 140:
					self.setStatus(lang.statusLeft % (140 - len(text)))
				
				else:
					self.setStatus(lang.statusMore % (len(text) - 140))
		
		else:
			self.hasTyped = False
	
		self.checkText(len(text))
		
	def checkText(self, count):
		if self.defaultBG == None:
			self.defaultBG = self.input.get_style().base[gtk.STATE_NORMAL]
		
		if count > 140:
			self.input.modify_base(gtk.STATE_NORMAL, gtk.gdk.Color(255 * 255, 200 * 255, 200 * 255))
			
		else:
			self.input.modify_base(gtk.STATE_NORMAL, self.defaultBG)
		#	self.status.modify_fg(gtk.STATE_NORMAL, self.defaultFG)
	
	
	# Text Focus Events --------------------------------------------------------
	# --------------------------------------------------------------------------
	def textfocus(self, *args):
		self.textFocus = True
		self.sizeInput()
		if not self.hasTyped:
			self.input.modify_text(gtk.STATE_NORMAL, self.defaultFG)
			self.input.get_buffer().set_text("")
	
	def notextfocus(self, *args):
		pass
	
	def loosefocus(self):
		if not self.textFocus:
			self.sizeInput()
			if not self.hasTyped:
				self.input.modify_text(gtk.STATE_NORMAL, self.input.get_style().text[gtk.STATE_INSENSITIVE])
				self.input.get_buffer().set_text(lang.textEntry)
			
		return False
	
	def htmlfocus(self, *args):
		gobject.timeout_add(100, lambda: self.loosefocus())
		self.textFocus = False
	
	 
 	# Toolbar-------------------------------------------------------------------
 	# --------------------------------------------------------------------------
 	def createToolbar(self):
		gui = """<ui>
			<toolbar name="toolbar_main">
				<toolitem action="update" />
				<toolitem action="clear" />
				<toolitem action="read" />
				<separator />
				<toolitem action="settings" />
				<toolitem action="about" />
				<toolitem action="exit" />
			</toolbar>
		</ui>"""
		
		self.actions = gtk.ActionGroup("Actions")
		self.actions.add_actions([
			("update", gtk.STOCK_REFRESH, "_Update", "<ctrl>U", lang.toolUpdate, self.on_update),
			("clear", gtk.STOCK_GOTO_TOP, "_Clear History", "<ctrl>C", lang.toolClear, self.on_clear),
			("read", gtk.STOCK_APPLY, "_Mark all Tweets as read", "<ctrl>M", lang.toolRead, self.on_read),
			("settings", gtk.STOCK_PREFERENCES, "_Settings", "<ctrl>S", lang.toolSettings, self.on_settings),
			("about", gtk.STOCK_ABOUT, "_About", None, lang.toolAbout, self.on_about),
			("exit", gtk.STOCK_QUIT, "_Exit", "<ctrl>E", lang.toolExit, self.on_exit)
		])

		ui = gtk.UIManager()
		ui.insert_action_group(self.actions, pos=0)
		self.window.add_accel_group(ui.get_accel_group())
		ui.add_ui_from_string(gui)
		
		self.updateButton = ui.get_widget("/toolbar_main/update")
		self.clearButton = ui.get_widget("/toolbar_main/clear")
		self.readButton = ui.get_widget("/toolbar_main/read")
		return ui.get_widget("/toolbar_main")

	# Load the Settings
	def loadSettings(self):
		self.settings = settings.Settings()
		if self.settings['username'] == None:
			self.settings['username'] = ""
		
		if self.settings['password'] == None:
			self.settings['password'] = ""
		
		self.username = self.settings['username']
		self.password = self.settings['password']


	# Dialogs ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def on_read(self, *args):
		if self.updater.initID != int(self.settings['lasttweet_' + self.username]):
			self.readButton.set_sensitive(False)
			self.updater.initID = int(self.settings['lasttweet_' + self.username])
			if not self.html.historyLoaded:
				self.html.tweets = self.html.tweets[len(self.html.tweets) - self.loadTweets:]
			
			self.html.render()
	
 	def on_update(self, event, *args):
 		if not self.updater.updating:
 			self.updatestatus(0)
 			self.updater.updateNow = True
 	
 	def on_clear(self, event, *args):
 		gobject.idle_add(lambda: self.html.clear())
 	
 	
 	def on_settings(self, event, *args):
 		if self.settingsOpen:
 			return
 			
 		self.settingsOpen = True
		glade = gtk.glade.XML(os.path.join(self.resources, "settings.glade"))
		dialog = glade.get_widget("settingsdialog")
		dialog.set_property("skip-taskbar-hint", True)
		dialog.set_title(lang.settingsTitle)
		dialog.set_transient_for(self.window)
		button = glade.get_widget("confirm")
		button.set_label(lang.settingsButton)
		glade.get_widget("usernamelabel").set_text(lang.settingsUsername)
		glade.get_widget("passwordlabel").set_text(lang.settingsPassword)
		username = glade.get_widget("username")
		password = glade.get_widget("password")
		notify = glade.get_widget("notify")
		sound = glade.get_widget("sound")
		notify.set_label(lang.settingsNotify)
		sound.set_label(lang.settingsSound)
		
		username.set_text(self.settings['username'])
		password.set_text(self.settings['password'])

		# Sound File
		file = glade.get_widget("soundfile")
		filter = gtk.FileFilter()
		filter.set_name(lang.settingsFileFilter)
		filter.add_pattern("*.mp3")
		filter.add_pattern("*.wav")
		filter.add_pattern("*.ogg")
		file.add_filter(filter)
		file.set_title(lang.settingsFile)
		file.set_filename(str(self.settings['soundfile']))
		
		# Notification Settings
		notify.set_active(self.settings.isTrue("notify"))
		sound.set_active(self.settings.isTrue("sound"))
		notify.set_sensitive(canNotify)
		
		def toggle2():
			file.set_sensitive(sound.get_active())
		
		def toggle():
			sound.set_sensitive(notify.get_active() and canNotify)
			file.set_sensitive(notify.get_active() and sound.get_active())
		
		toggle()
		notify.connect("toggled", lambda *a: toggle())
		sound.connect("toggled", lambda *a: toggle2())
		
		oldusername = self.settings['username']
		oldpassword = self.settings['password']
		
		def save(*args):
			self.settings['soundfile'] = str(file.get_filename())
			self.settings['notify'] = notify.get_active()
			self.settings['sound'] = sound.get_active()
		
			self.settings['username'] = username.get_text().strip()
			self.settings['password'] = password.get_text().strip()

			self.username = self.settings['username']
			self.password = self.settings['password']
			
			# Login again if credentials have changed
			self.isLoggedOut = not self.settings.isset("username") or not self.settings.isset("password")
			if username.get_text().strip() != oldusername or password.get_text().strip() != oldpassword:
				if not self.isLoggedOut:
	 				self.login()
	 			
	 			else:
	 				self.logout()
			
			self.settingsOpen = False
			dialog.hide()
		
		def close(*args):
			self.settingsOpen = False
		
		dialog.connect("delete_event", close)
		button.connect("clicked", save)
		dialog.show_all()
 	
 	def on_about(self, *args):
 		if self.aboutOpen:
 			return
 			
 		self.aboutOpen = True
		glade = gtk.glade.XML(os.path.join(self.resources, "about.glade"))
		dialog = glade.get_widget("aboutdialog")
		dialog.set_property("skip-taskbar-hint", True)
		dialog.set_transient_for(self.window)		
		glade.get_widget("title").set_markup('<span size="x-large"><b>Atarashii %s</b></span>' % self.version)
		glade.get_widget("image").set_from_file(self.img)
		button = glade.get_widget("okbutton")
		button.set_label(lang.aboutOKButton)
		
		info = glade.get_widget("infobox")
		text = glade.get_widget("textwindow")
	
		license = glade.get_widget("license")
		license.set_label(lang.aboutLicenseButton)
		
		def close(*args):
			self.aboutOpen = False
			dialog.hide()
		
		def toggle(widget, *args):
			if widget.get_property("active"):
				text.show()
				info.hide()
				
			else:
				info.show()
				text.hide()
		
		license.connect("toggled", toggle)
		dialog.connect("delete_event", close)
		button.connect("clicked", close)
		dialog.show_all()
		text.hide()
		dialog.set_title(lang.aboutTitle)
 	
 	def on_exit(self, widget = None, data = None):
 		if data:
 			data.set_visible(False)
 		
 		self.settings['position'] = str(self.window.get_position())
 		size = self.window.get_allocation()
		self.settings['size'] = str((size[2], size[3]))
 		
 		gtk.main_quit()
 		sys.exit(1)
 	
	
	# Errors and Warning -------------------------------------------------------
	# --------------------------------------------------------------------------
	def reconnectInfo(self):
		wait = self.update - (calendar.timegm(time.gmtime()) - self.reconnectTime)
		if wait < 60:
			self.setStatus(lang.statusReconnectSeconds % wait)
		
		elif wait < 105:
			self.setStatus(lang.statusReconnectMinute)
			
		else:
			self.setStatus(lang.statusReconnectMinutes % math.ceil(wait / 60.0))
			
		return self.waitForReconnect
	
 	def error(self, detail):
 		try:
 			code = int(detail.reason.split("=")[1].strip())
		except:
			code = 0

		# Ratelimit error
 		if code == 400:
 			limit = self.api.rate_limit_status()
			minutes = math.ceil((limit['reset_time_in_seconds'] - calendar.timegm(time.gmtime())) / 60.0)
			self.update = int(minutes * 60 + 2)
			self.updateButton.set_sensitive(False)
 			if not self.connected:
 				self.reconnectTime = calendar.timegm(time.gmtime())
 				self.waitForReconnect = True
 				gobject.timeout_add(int(self.update * 1000), lambda: self.login())
 				gobject.timeout_add(1000, lambda: self.reconnectInfo())
 				rateError = lang.errorRatelimitReconnect % math.ceil(minutes)
 			else:
 				rateError = lang.errorRatelimit % math.ceil(minutes)
 			
 		else:
 			rateError = ""
 		
 		try:
	 		error = {
	 			404 : lang.errorLogin,
	 			401 : lang.errorLogin,
	 			400 : rateError,
	 			500 : lang.errorTwitter,
	 			502 : lang.errorDown,
	 			503 : lang.errorOverload
	 		}[code]
	 	
	 	except:
	 		error = lang.errorInternal % str(detail)
	 	
		glade = gtk.glade.XML(os.path.join(self.resources, "error.glade"))
		dialog = glade.get_widget("errordialog")
		dialog.set_property("skip-taskbar-hint", True)
		dialog.set_title(lang.errorTitle)
		dialog.set_transient_for(self.window)
		glade.get_widget("text").set_size_request(160, -1)
		glade.get_widget("text").set_text(error)
		button = glade.get_widget("okbutton")
		button.connect("clicked", lambda *a: dialog.hide())
		dialog.show_all()
	
	def warning(self, limit):
		glade = gtk.glade.XML(os.path.join(self.resources, "warning.glade"))
		dialog = glade.get_widget("warningdialog")
		dialog.set_title(lang.warningTitle)
		dialog.set_transient_for(self.window)
		glade.get_widget("text").set_size_request(160, -1)
		glade.get_widget("text").set_text(lang.warningText % limit)
		button = glade.get_widget("okbutton")
		button.connect("clicked", lambda *a: dialog.hide())
		dialog.show_all()
	
 	# Initiate more stuff on first draw ----------------------------------------
	# --------------------------------------------------------------------------
 	def draw(self, *args):
 		self.window.disconnect(self.initiated)
 		
		self.tray = gtk.StatusIcon()
		self.tray.set_from_file(self.img)
		self.tray.set_tooltip("Atarashii")
		self.tray.set_visible(True)
		self.tray.connect("activate", self.trayActivate)
		
		# Tray Menu
		menu = gtk.Menu()
		
		menuItem = gtk.ImageMenuItem(gtk.STOCK_REFRESH)
		menuItem.set_label(lang.menuUpdate)
		menuItem.connect('activate', self.on_update, self.tray)	
		menu.append(menuItem)
		
		menuItem = gtk.ImageMenuItem(gtk.STOCK_PREFERENCES)
		menuItem.set_label(lang.menuSettings)
		menuItem.connect('activate', self.on_settings, self.tray)	
		menu.append(menuItem)
		
		menuItem = gtk.ImageMenuItem(gtk.STOCK_ABOUT)
		menuItem.set_label(lang.menuAbout)
		menuItem.connect('activate', self.on_about, self.tray)	
		menu.append(menuItem)
		
		menu.append(gtk.SeparatorMenuItem())
		
		menuItem = gtk.ImageMenuItem(gtk.STOCK_QUIT)
		menuItem.set_label(lang.menuExit)
		menuItem.connect('activate', self.on_exit, self.tray)	
		menu.append(menuItem)
		
		self.tray.connect("popup-menu", self.trayPopup, menu)
 		
 		# Connect
		self.login()
		gobject.idle_add(lambda: self.createTray())
 		
 	
 	def login(self):
 		self.waitForReconnect = False
 		if not self.isLoggedOut:
	  		i = login.Login(self)
	 		i.setDaemon(True)
	 		i.start()
	 		gobject.timeout_add(100, lambda: self.showProgess())
	 	
	 	else:
	 		self.setStatus(lang.statusLogout)
	 
 	def logout(self):
 		self.html.view.grab_focus()
 		self.updater.started = False
 		self.connected = False
 		self.connecting = False
 		self.waitForReconnect = False
 		self.setStatus(lang.statusLogout)
 		self.scroll.hide()
 		self.label.hide()
 		self.progress.hide()
 		self.activateGUI(False)
 		self.html.init(True)
 	
 	
	# Tray icon stuff  ---------------------------------------------------------
	# --------------------------------------------------------------------------
	def trayPopup(self, widget, button, time, data = None):
		if button == 3:
			if data:
				data.show_all()
				data.popup(None, None, None, 3, time)
	
 	def createTray(self):
		self.tray.set_from_file(self.img)
		return False
		
 	# Tray Icon clicked
 	def trayActivate(self, *args):
 		if self.minimized:
 			self.window.deiconify()
 			dec = True
 		else:
 			dec = False
 	
		if not self.window.get_property("visible"):
			self.window.present()
			self.window.move(*self.position)
			gobject.idle_add(lambda: self.window.grab_focus())
	
		else:
			screen = self.window.get_screen()
			pos = self.window.get_position()
			pos = [pos[0], pos[1]]
			while pos[0] < 0:
				pos[0] += screen.get_width()
			
			while pos[0] > screen.get_width():
				pos[0] -= screen.get_width()
				
			while pos[1] < 0:
				pos[1] += screen.get_height()
			
			while pos[1] > screen.get_height():
				pos[1] -= screen.get_height()	
			
			self.settings['position'] = str(pos)
			self.position = pos
			
			if self.onScreen() and not dec:
				self.window.hide()
				
			else:
				self.window.move(*self.position)
				gobject.timeout_add(10, lambda: self.forceFocus())
	
	def inOverlayed(self):
 		windows = self.window.get_screen().get_toplevel_windows()
 		win = self.window.get_window()
 		x, y, w, h, b = win.get_geometry()
 		for i in windows:
 			if win != i:
 				x2, y2, w2, h2, b2 = i.get_geometry()
				if x >= x2 and x + w <= x2 + w2:
					if y >= y2 and y + h <= y2 + h2:
 						return True
 						
 		return False
	
	def forceFocus(self):
		self.window.grab_focus()
		self.window.present()
		return not self.window.is_active()
	
	def onScreen(self):
		screen = self.window.get_screen()
		size = self.window.size_request()
		position = self.window.get_position()
		if position[0] < 0 - size[0] or position[0] > screen.get_width() or position[1] < 0 - size[1] or position[1] > screen.get_height():
			return False
			
		else:
			return True
	
 	# Start program ------------------------------------------------------------
	# --------------------------------------------------------------------------
	def main(self):
		self.updater = updater.Updater(self)
		self.updater.setDaemon(True)
		self.updater.start()
		
		# Keep it running! Even iv webkit raises an xorg exception
		gtk.main()
		
# Run for debugging
if __name__ == "__main__":
	path = os.path.abspath(os.path.dirname(sys.argv[0]))
	Atarashii(path).main()
	
