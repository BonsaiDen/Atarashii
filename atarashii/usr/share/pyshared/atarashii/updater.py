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


# Background Twitter Updater ---------------------------------------------------
# ------------------------------------------------------------------------------
import time
import threading
import urllib
import os
import notify
import gobject
import calendar

import ratelimit
from lang import lang


class Updater(threading.Thread):
	def __init__(self, main):
		threading.Thread.__init__(self)
		self.main = main
		self.settings = main.settings
		self.html = self.main.gui.html
		
		# Notifier
		self.notify = notify.Notifier(main)
		
		# Variables
		self.running = True
		self.error = False
		self.started = False
		self.doInit = False
		self.refreshNow = False
		
		self.lastID = -1
		self.ratelimit = 150
		self.loadHistoryID = -1
		self.path = os.path.expanduser('~')
		
		
	# Init the Updater ---------------------------------------------------------
	# --------------------------------------------------------------------------
	def init(self):
		# Reset
		self.doInit = False
		self.lastID = -1
		self.started = False
		self.error = False
		self.refreshNow = False
		self.main.refreshTimeout = -1
		self.loadHistoryID = -1
		
		# InitID = the last read tweet
		self.initID = self.main.getLatestID()
		
		# Fetch Tweets
		updates = []
		try:
			updates = self.getUpdates(self.main.getFirstID())
		
		# Something went wrong...
		except Exception, error:
			gobject.idle_add(lambda: self.main.onLoginFailed(error))
			return
		

		# We've connected!
		if len(updates) > 0:
			self.setLast(updates[0].id)
		
		self.updateLimit()
		self.started = True
		gobject.idle_add(lambda: self.main.onLogin())
		
		# Push to HTML
		updates.reverse()
		for i in updates:
			if i != None:
				imgfile = self.getImage(i.user.profile_image_url, i.user.id)
				self.html.updateList.append((i, imgfile, False))

		gobject.idle_add(lambda: self.html.pushUpdates())
	
	
	# Mainloop -----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def run(self):
		while self.running:
			if self.doInit:
				self.init()
		
			elif not self.error and self.started:
				if self.loadHistoryID == -1:
					if self.main.refreshTimeout != -1:
						if calendar.timegm(time.gmtime()) > self.main.refreshTime + self.main.refreshTimeout or self.refreshNow:
							self.main.isUpdating = True
							self.updateTweets()
							self.main.isUpdating = False
		
				else:
					self.loadHistory()
			
			time.sleep(0.1)
	
	# Update -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def updateTweets(self):
		# Fetch Tweets
		updates = []
		try:
			updates = self.getUpdates(self.lastID)
		
		# Something went wrong...
		except Exception, error:
			gobject.idle_add(lambda: self.main.gui.showError(error))
			self.main.refreshTimeout = 60
			self.main.refreshTime = calendar.timegm(time.gmtime())
			return
		
		if len(updates) > 0:
			self.setLast(updates[0].id)
		
		# Filter non User Tweets
		tweetList = []
		tweetIDS = []
		username = self.settings['username']
		for i in updates:
			imgfile = self.getImage(i.user.profile_image_url, i.user.id)
			if i.user.screen_name != username:
				# Don't add mentions twice
				if not i.id in tweetIDS:
					tweetIDS.append(i.id)
					tweetList.append((i.user.screen_name, i.text, imgfile, None))
			
			self.html.updateList.append((i, imgfile, False))
		
		# Show Notifications
		if len(tweetList) > 0:
			if self.settings.isTrue("notify"):
				tweetList.reverse()
				self.notify.show(tweetList, self.settings.isTrue("sound"))
		
		# Update View
		if len(updates) > 0:
			gobject.idle_add(lambda: self.html.pushUpdates())
		
		else:
			gobject.idle_add(lambda: self.html.render())
		
		# Rate Limiting
		self.updateLimit()
		gobject.idle_add(lambda: self.main.gui.refreshButton.set_sensitive(True))
		if self.lastID > self.initID:
			gobject.idle_add(lambda: self.main.gui.readButton.set_sensitive(True))
	
	
	# Load History -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def loadHistory(self):
		# Fetch Tweets
		updates = []
		try:
			updates = self.getUpdates(maxID = self.loadHistoryID, maxCount = self.main.loadTweetCount)
		
		# Something went wrong...
		except Exception, error:
			print error
			self.loadHistoryID = -1
			self.main.isLoadingHistory = False
			gobject.idle_add(lambda: self.main.gui.showError(error))
			self.main.refreshTimeout = 60
			self.main.refreshTime = calendar.timegm(time.gmtime())
			return
		
		# Loaded
		self.main.maxTweetCount += len(updates)
		for i in updates:
			imgfile = self.getImage(i.user.profile_image_url, i.user.id)
			self.html.updateList.append((i, imgfile, True))
		
		self.loadHistoryID = -1
		self.main.isLoadingHistory = False
		
		self.html.loadHistory = True
		self.html.historyLoaded = True
		self.html.historyCount += len(updates)
		self.main.gui.historyButton.set_sensitive(True)
		
		gobject.idle_add(lambda: self.html.pushUpdates())
		gobject.idle_add(lambda: self.main.gui.showInput())
	
	
	# Main Function that fetches the updates -----------------------------------
	# --------------------------------------------------------------------------
	def getUpdates(self, sinceID = 0, maxID = None, maxCount = 200):
		gobject.idle_add(lambda: self.main.gui.updateStatus(True))
		updates = []
		mentions = []
	
		# Get new Tweets
		if sinceID != -1:
			if maxID == None:
				mentions = self.main.api.mentions(since_id = sinceID, count = maxCount)
				updates = self.main.api.home_timeline(since_id = sinceID, count = maxCount)
				
			else:				
				updates = self.main.api.home_timeline(max_id = maxID, count = maxCount)
				if len(updates) > 0:
					mentions = self.main.api.mentions(max_id = maxID, since_id = updates[len(updates) -1].id, count = maxCount)
		
		# Init the Timeline
		else:
			updates = self.main.api.home_timeline(count = self.main.loadTweetCount)
			if len(updates) > 0:
				mentions = self.main.api.mentions(since_id = updates[len(updates) - 1].id, count = 200)
		
		
		# Sort and Stuff
		for i in mentions:
			i.is_mentioned = True
		
		self.refreshNow = False
		self.main.refreshTime = calendar.timegm(time.gmtime())
		
		# Return
		updates = updates + mentions
		if len(mentions) > 0:
			return self.processUpdates(updates)
		
		else:
			return updates
	
	
	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def setLast(self, tweetID):
		self.lastID = tweetID
		self.settings['lasttweet_' + self.settings['username']] = str(tweetID)
		if len(self.html.tweets) > 0:
			self.html.newestID = self.html.tweets[len(self.html.tweets)-1][0].id
		
		if self.lastID > self.initID:
			self.main.gui.readButton.set_sensitive(True)
	
	def processUpdates(self, updates):
		def compare(x, y):
			if x.id > y.id:
				return -1
	
			elif x.id < y.id:
				return 1
		
			else:
				return 0
	
		# Remove double mentions
		for i in range(0, len(updates)):
			if updates[i] != None:
				for e in range(i + 1, len(updates)):
					if updates[e] != None and updates[i].id == updates[e].id:
							updates[e] = None
		
		updates = [i for i in updates if i != None]
		updates.sort(compare)
		return updates
	
	# Update the refreshTimeout
	def updateLimit(self):
		i = ratelimit.RateLimiter(self)
		i.setDaemon(True)
		i.start()
	
	# Cache a user avatar	
	def getImage(self, url, userid):
		image = url[url.rfind('/')+1:]
		imgdir = os.path.join(self.path, ".atarashii")
		if not os.path.exists(imgdir):
			os.mkdir(imgdir)
		
		imgfile = os.path.join(imgdir, str(userid) + '_' + image)
		if not os.path.exists(imgfile):
			urllib.urlretrieve(url, imgfile)
		
		return imgfile		
		
