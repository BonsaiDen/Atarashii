#  This file is part of  Atarashii.
#
#   Atarashii is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#   Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Login Thread -----------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading
import sys

# Import local Tweepy
sys.path.insert(0, __file__[:__file__.rfind('/')])
try:
	import tweepy
	
finally:
	sys.path.pop(0)

import locale
import time
from lang import lang
locale.setlocale(locale.LC_ALL, 'C')

class Login(threading.Thread):
	def __init__(self, atarashii):
		threading.Thread.__init__(self)
		self.atarashii = atarashii
		
	def run(self):
 		if self.atarashii.username != "":
 			while self.atarashii.updater.updating:
 				time.sleep(0.1)
 			
 			self.atarashii.updater.started = False
 			self.atarashii.html.tweets = []
 			self.atarashii.list = []
 			self.atarashii.connected = False
 			self.atarashii.connecting = True
			self.atarashii.scroll.hide()
			self.atarashii.progress.set_fraction(0.0)
			self.atarashii.progress.show()
			self.atarashii.setStatus(lang.statusConnecting % self.atarashii.username)
	 		self.atarashii.window.set_title("Atarashii | %s" % self.atarashii.username)
			
			gobject.idle_add(lambda: self.atarashii.html.start())
			
			auth = tweepy.BasicAuthHandler(self.atarashii.username, self.atarashii.password)
			self.atarashii.api = tweepy.API(auth)
			self.atarashii.setStatus(lang.statusConnected)
			self.atarashii.updater.init()
			
			if self.atarashii.connected:
				self.atarashii.scroll.show()
				
			else:
				gobject.idle_add(lambda: self.atarashii.html.init(True))
					
			self.atarashii.progress.hide()
			self.atarashii.connecting = False

