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

import sys
import os
import calendar
import time

gtk.gdk.threads_init()

import send
import gui
import settings
import updater
from lang import lang

# Import local Tweepy
sys.path.insert(0, __file__[:__file__.rfind('/')])
try:
	import tweepy
	
finally:
	sys.path.pop(0)

# Fix local bug with tweepy
import locale
locale.setlocale(locale.LC_ALL, 'C')


class Atarashii:
	def __init__(self, version, debug = None):
		# Setup
		self.version = version
		self.debug = debug
		
		# Load Settings
		self.settings = settings.Settings()
		
		# API
		self.api = None
		
		# Variables
		self.replyUser = -1
		self.replyText = ""
		self.replyID = -1
		
		self.retweetNum = -1
		self.retweetUser = ""	
		self.retweetText = ""
		
		self.loadTweetCount = 20
		self.maxTweetCount = 200
		
		# Timer
		self.refreshTime = calendar.timegm(time.gmtime())
		self.refreshTimeout = -1
		self.reconnectTime = -1
		
		# State
		self.loginError = False
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = False
		self.isReconnecting = False
		self.isUpdating = False
		self.isLoadingHistory = False
		
		self.rateWarningShown = False
		
		# GUI
		self.gui = gui.GUI(self)
		
		# Updater
		self.updater = updater.Updater(self)
		self.updater.setDaemon(True)
		self.updater.start()
		

	# Sending ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def send(self, text):
		self.isSending = True
		self.gui.text.set_sensitive(False)
		self.gui.showProgress()	
		if self.replyUser != "":
			self.gui.setStatus(lang.statusReply % self.replyUser)
			
		elif self.retweetUser != "":
			self.gui.setStatus(lang.statusRetweet % self.retweetUser)
			
		else:
			self.gui.setStatus(lang.statusSend)
			
		# Sender
		sender = send.Send(self)
		sender.setDaemon(True)
		sender.start()
	
	
	# Login & Logout -----------------------------------------------------------
	# --------------------------------------------------------------------------
	def onInit(self):
		self.login()
	
	def login(self):
		# Only login with username and pasword
 		if not self.settings.isset("username") or not self.settings.isset("password"):
 			# TODO self.html.splash()
 			return
 		
 		# Wait until the last update is complete
 		while self.isUpdating:
 			time.sleep(0.1)
		
		# Progress
		self.gui.hideAll()
		self.gui.showProgress()
		
		# Connect
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = True
		self.isReconnecting = False
		self.isUpdating = False
		self.loginError = False
		
		# Reset
		self.gui.updateStatus()
		self.gui.html.init(False)

		# Do it!
		auth = tweepy.BasicAuthHandler(self.settings["username"], self.settings["password"])
		self.api = tweepy.API(auth)
	
		# Init
		self.updater.doInit = True

	def onLogin(self):
		self.loginError = False
		self.loginStatus = True
		self.isConnecting = False
		self.gui.set_title("Atarashii | %s" % self.settings["username"])
		self.gui.updateStatus()
		self.gui.showInput()
		
	def onLoginFailed(self, error):
		self.loginError = True
		self.loginStatus = False
		self.isConnecting = False
		self.gui.set_title("Atarashii")
		self.gui.hideAll()
		self.gui.showError(error)
		self.gui.updateStatus()
		gobject.idle_add(lambda: self.gui.html.init(True))
	
	def logout(self):
		self.loginError = False
		self.loginStatus = False
		self.isSending = False
		self.isConnecting = False
		self.isReconnecting = False
		self.isUpdating = False
		self.gui.set_title("Atarashii")
		self.gui.hideAll()
		gobject.idle_add(lambda: self.gui.html.init(True))
	
	
	# Reconnect ----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def reconnect():
		limit = self.api.rate_limit_status()
		minutes = math.ceil((limit['reset_time_in_seconds'] - calendar.timegm(time.gmtime())) / 60.0)
		self.refreshTimeout = int(minutes * 60 + 2)
		
		if not self.isConnected:
			self.reconnectTime = calendar.timegm(time.gmtime())
			self.isReconnecting = True
			gobject.timeout_add(int(self.refreshTimeout * 1000), lambda: self.login())
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
		if self.settings.isset('lasttweet_' + self.settings['username']):
			return long(self.settings['lasttweet_' + self.settings['username']])
		
		else:
			return -1
			
	def getFirstID(self):
		if self.settings.isset('firsttweet_' + self.settings['username']):
			return long(self.settings['firsttweet_' + self.settings['username']])
		
		else:
			return -1


 	# Start & Quit -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		gtk.main()
		
	def quit(self):
 		self.settings['position'] = str(self.gui.get_position())
 		size = self.gui.get_allocation()
		self.settings['size'] = str((size[2], size[3]))
		self.settings.save()
 		gtk.main_quit()
 		sys.exit(1)


# Run for debugging
if __name__ == "__main__":
	Atarashii(0.94).start()
	
