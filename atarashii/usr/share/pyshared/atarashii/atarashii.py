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



# DBUS Integration -------------------------------------------------------------
# ------------------------------------------------------------------------------
import dbus, dbus.service
import sys

if 'org.Atarashii' in dbus.Interface(dbus.SessionBus().get_object("org.freedesktop.DBus", "/org/freedesktop/DBus"), "org.freedesktop.DBus").ListNames():
	sys.exit(2)

DBUS = dbus.SessionBus()
DBUSNAME = dbus.service.BusName('org.Atarashii', bus = DBUS)


# Atarashii --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gtk.glade
import gobject

import os
import calendar
import time
import math

gtk.gdk.threads_init()
gtk.gdk.threads_enter()


import send
import gui
import settings
import updater
from lang import lang

class Atarashii:
	def __init__(self, version, debug = None):
		# Setup
		self.version = version
		self.debug = debug
		
		# Load Settings
		self.settings = settings.Settings()
		
		# API
		self.api = None
		self.apiTempPassword = None
		
		# Variables
		self.replyUser = -1
		self.replyText = ""
		self.replyID = -1
		
		self.retweetNum = -1
		self.retweetUser = ""	
		self.retweetText = ""
		
		self.messageUser = ""
		self.messageID = -1
		self.messageText = ""
		
		self.loadTweetCount = 20
		self.maxTweetCount = 200
		self.loadMessageCount = 20
		self.maxMessageCount = 200
		
		# Timer
		self.refreshTime = calendar.timegm(time.gmtime())
		self.refreshTimeout = -1
		self.reconnectTime = -1
		self.reconnectTimeout = None
		
		# State
		self.loginError = False
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = False
		self.isReconnecting = False
		self.isUpdating = False
		self.isLoadingHistory = False
		self.wasSending = False
		self.rateWarningShown = False
		
		# Current Username
		self.username = self.settings['username'] or ""
		
		# Updater
		self.updater = updater.Updater(self)
		self.updater.setDaemon(True)	
		
		# GUI
		self.gui = gui.GUI(self)
		
		# Start
		self.updater.start()
		

	# Sending ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def send(self, text):
		self.isSending = True
		self.gui.text.set_sensitive(False)
		self.gui.modeButton.set_sensitive(False)
		self.gui.showProgress()	
		if self.replyUser != "":
			self.gui.setStatus(lang.statusReply % self.replyUser)
			
		elif self.retweetUser != "":
			self.gui.setStatus(lang.statusRetweet % self.retweetUser)
			
		elif self.messageText != "":
			self.gui.setStatus(lang.statusMessageReply % self.messageUser)
			
		elif self.messageUser != "":
			self.gui.setStatus(lang.statusMessage % self.messageUser)
			
		else:
			self.gui.setStatus(lang.statusSend)
		
		# Sender
		sender = send.Send(self, self.gui.mode, text)
		sender.setDaemon(True)
		sender.start()
	
	
	# Login & Logout -----------------------------------------------------------
	# --------------------------------------------------------------------------
	def onInit(self):
		self.login()
	
	def login(self):
		if self.username == "":
			return

 		# Wait until the last update is complete
 		while self.isUpdating:
 			time.sleep(0.1)
		
		# Set Mode
		self.gui.setMode(self.settings.isTrue('mode_' + self.username, False))
		
		# Progress
		self.gui.hideAll(False)
		self.gui.showProgress()
		
		# Connect
		if self.reconnectTimeout != None:
			gobject.source_remove(self.reconnectTimeout)
		
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = True
		self.isReconnecting = False
		self.reconnectTimeout = None
		self.isUpdating = False
		self.loginError = False
		
		# Reset
		self.gui.updateStatus()
		self.gui.html.init(True)
		if self.gui.mode:
			self.gui.html.start()
		
		self.gui.settingsButton.set_sensitive(False)
		self.gui.tray.settingsMenu.set_sensitive(False)
		self.gui.message.init(True)
		if not self.gui.mode:
			self.gui.message.start()

		self.updater.doInit = True
	
	def onLogin(self):
		self.loginError = False
		self.loginStatus = True
		self.isConnecting = False
		self.gui.settingsButton.set_sensitive(True)
		self.gui.tray.settingsMenu.set_sensitive(True)
		self.gui.set_title(lang.titleLoggedIn % self.username)
		self.gui.updateStatus()
		self.gui.showInput()
		
	def onLoginFailed(self, error = None):
		self.gui.setMode(False)
		self.loginError = True if error != None else False
		self.loginStatus = False
		self.isConnecting = False
		self.gui.settingsButton.set_sensitive(True)
		self.gui.tray.settingsMenu.set_sensitive(True)
		self.gui.set_title(lang.title)
		self.gui.hideAll()
		self.gui.updateStatus()
		if error:
			self.gui.showError(error)
		
		gobject.idle_add(lambda: self.gui.html.init(True))
	
	def logout(self):
		self.gui.setMode(False)
		self.loginError = False
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = False
		self.isReconnecting = False
		self.isUpdating = False
		self.gui.settingsButton.set_sensitive(True)
		self.gui.updateStatus()
		self.gui.set_title(lang.title)
		self.gui.hideAll()
		gobject.idle_add(lambda: self.gui.html.init(True))
	
	
	# Reconnect ----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def reconnect(self):
		if self.api.ratelimit != None:
			minutes = math.ceil((self.api.ratelimit['reset'] - calendar.timegm(time.gmtime())) / 60.0)
		else:
			minutes = 5
		
		self.refreshTimeout = int(minutes * 60 + 2)
		
		if not self.loginStatus:
			self.reconnectTime = calendar.timegm(time.gmtime())
			self.isReconnecting = True
			self.reconnectTimeout = gobject.timeout_add(int(self.refreshTimeout * 1000), lambda: self.login())
			return lang.errorRatelimitReconnect % math.ceil(minutes)
		
		else:
			return lang.errorRatelimit % math.ceil(minutes)	
	
	
	# HTML ---------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def reply(self, num = -1):
		self.gui.text.reply(num)

	# Retweet Something
	def retweet(self):
		self.gui.text.retweet()
	
	# Message to someone
	def message(self, num):
		self.gui.text.message(num)
		
	
	# Helper Functions ---------------------------------------------------------
	# --------------------------------------------------------------------------
	def getImage(self):
		if self.debug == None:
			return '/usr/share/icons/atarashii.png'
		else:
			return os.path.join(self.debug, 'atarashii/usr/share/icons/atarashii.png')
		
	def getResource(self, res):
		if self.debug == None:
			return os.path.join("/usr/share/atarashii", res)
		else:
			return os.path.join(self.debug, "atarashii/usr/share/atarashii", res)
	
	def getLatestID(self):
		if self.settings.isset('lasttweet_' + self.username):
			return long(self.settings['lasttweet_' + self.username])
		
		else:
			return -1
			
	def getFirstID(self):
		if self.settings.isset('firsttweet_' + self.username):
			return long(self.settings['firsttweet_' + self.username])
		
		else:
			return -1

	def getLatestMessageID(self):
		if self.settings.isset('lastmessage_' + self.username):
			return long(self.settings['lastmessage_' + self.username])
		
		else:
			return -1
	
	def getFirstMessageID(self):
		if self.settings.isset('firstmessage_' + self.username):
			return long(self.settings['firstmessage_' + self.username])
		
		else:
			return -1

	def setTweetCount(self, count):
		self.maxTweetCount = count
	
	def getTweetCount(self):
		return self.maxTweetCount

	def setMessageCount(self, count):
		self.maxMessageCount = count
	
	def getMessageCount(self):
		return self.maxMessageCount


 	# Start & Quit -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		gtk.main()
		
	def saveSettings(self):
 		self.settings['position'] = str(self.gui.get_position())
 		size = self.gui.get_allocation()
		self.settings['size'] = str((size[2], size[3]))
		self.settings['username'] = self.username
		self.settings.save()
		
	def saveMode(self):
		if self.username != "":
			self.settings['mode_' + self.username] = self.gui.mode
	
	def quit(self):
		self.saveMode()
		self.saveSettings()
 		gtk.main_quit()
 		sys.exit(1)

	
