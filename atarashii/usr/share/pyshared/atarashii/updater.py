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


# Background Updater -----------------------------------------------------------
# ------------------------------------------------------------------------------
import time
import threading
import urllib
import os
import notify
import gobject
import calendar
from lang import lang


# Ratelimit Thread -------------------------------------------------------------
# ------------------------------------------------------------------------------
class Rater(threading.Thread):
	def __init__(self, updater):
		threading.Thread.__init__(self)
		self.updater = updater

	def run(self):
		req = self.updater.atarashii.api.rate_limit_status()
		minutes = (req['reset_time_in_seconds'] - calendar.timegm(time.gmtime())) / 60
		limit = req['remaining_hits']
		if limit > 0:
			self.updater.ratelimit = limit / 2.0
			self.updater.atarashii.update = int(minutes / (self.updater.ratelimit) * 60 * 1.25)
			if self.updater.atarashii.update < 45:
				self.updater.atarashii.update = 45
		
		count = req['hourly_limit']
		if count < 150:
			if not self.updater.atarashii.rateWarning:
				self.updater.atarashii.rateWarning = True
				gobject.idle_add(lambda: self.updater.atarashii.warning(count))
				
		else:
			self.updater.atarashii.rateWarning = False

			
# Updater Thread ---------------------------------------------------------------
# ------------------------------------------------------------------------------
class Updater(threading.Thread):
	def __init__(self, atarashii):
		threading.Thread.__init__(self)
		self.atarashii = atarashii
		self.notify = notify.Notifier(self.atarashii)
		self.running = True
		self.error = False
		self.started = False
		self.ratelimit = 150
		self.loadOlder = -1
		self.path = os.path.expanduser('~')
		self.updating = False
		self.html = self.atarashii.html
	
	# Sort the combined Timeline and Mentions
	def compare(self, x, y):
		if x.id > y.id:
			return -1
	
		elif x.id < y.id:
			return 1
		
		else:
			return 0
	
	def fixMentions(self, updates):
		# Remove double mentions
		for i in range(0, len(updates)):
			if updates[i] != None:
				for e in range(i + 1, len(updates)):
					if updates[e] != None and updates[i].id == updates[e].id:
							updates[e] = None
		
		return [i for i in updates if i != None]
	
	# Set the latest tweet ID
	def setLast(self, id):
		self.lastID = id
		self.atarashii.settings['lasttweet_' + self.atarashii.username] = str(id)
		if len(self.html.tweets) > 0:
			self.html.newestID = self.html.tweets[len(self.html.tweets)-1][0].id
		
		if self.lastID > self.initID:
			self.atarashii.readButton.set_sensitive(True)
	
	def updateLimit(self):
		i = Rater(self)
		i.setDaemon(True)
		i.start()
	
	
	# Initiate Timeline --------------------------------------------------------
	# --------------------------------------------------------------------------
	def init(self):
		self.started = False
		self.error = False
		self.lastID = -1
		if self.atarashii.settings.isset('lasttweet_' + self.atarashii.username):
			self.initID = long(self.atarashii.settings['lasttweet_' + self.atarashii.username])
		else:
			self.initID = -1
		
		try:
			updates = []
			
			# Get tweets since last exit
			if self.atarashii.settings.isset('firsttweet_' + self.atarashii.username):
				count = long(self.atarashii.settings['firsttweet_' + self.atarashii.username])
				
				# Check mentions first, so when the api lags we should still get 
				# the mentions on both the timeline and the mentions call and can distinguish them
				mentions = self.atarashii.api.mentions(since_id = count, count = 200)
				timeline = self.atarashii.api.home_timeline(since_id = count, count = 200)
				for i in mentions:
					i.is_mentioned = True
				
				updates = timeline + mentions
				if len(mentions) > 0:
					updates = self.fixMentions(updates)
					updates.sort(self.compare)	
			
			# Get initial tweets for this user
			else:
				timeline = self.atarashii.api.home_timeline(count = self.atarashii.loadTweets)
				if len(timeline) > 0:
					mentions = self.atarashii.api.mentions(since_id = timeline[len(timeline) -1 ].id, count = 200)
					for i in mentions:
						i.is_mentioned = True
					
					updates = timeline + mentions
					if len(mentions) > 0:
						updates = self.fixMentions(updates)
						updates.sort(self.compare)
					
				else:
					updates = timeline
			
			if len(updates) > 0:
				self.setLast(updates[0].id)
		
		except Exception, detail:
			if not self.atarashii.connected:
				self.atarashii.connected = False
				self.atarashii.setStatus(lang.statusError)
				self.atarashii.activateGUI(False)
				self.atarashii.updater.error = True
				gobject.idle_add(lambda: self.atarashii.error(detail))
				self.atarashii.typing = False
				self.atarashii.sizeInput()
				gobject.idle_add(lambda: self.atarashii.html.splash())
				self.atarashii.setStatus(lang.statusLogout)
				self.error = True
				return
				
			else:
				self.atarashii.error(detail)
				self.error = True
		
		# Connection was succesfull
		self.atarashii.connected = True
		self.atarashii.maxTweets = len(updates)
		
		# Values
		self.last = time.time()
		self.updateNow = False
		
		# Push Tweets to View
		if not self.error:
			updates.reverse()
			for i in updates:
				if i != None:
					file = self.getImage(i.user.profile_image_url, i.user.id)
					self.html.list.append((i, file, False))
			
			self.atarashii.update = -1
			self.updateLimit()
			self.atarashii.activateGUI(True)
			gobject.idle_add(lambda: self.html.push())

		self.started = True
	
	
	# Mainloop -----------------------------------------------------------------
	#- -------------------------------------------------------------------------
	def run(self):
		interval = 0
		while self.running:
			if not self.error and self.started:
				if self.loadOlder == -1:
					if self.atarashii.update != -1:
						if time.time() > self.last + self.atarashii.update or self.updateNow:
							self.updating = True
							gobject.idle_add(lambda: self.atarashii.updatestatus(0))
							self.updateNow = False
							self.update()
							self.last = time.time()	
						
						interval2 = self.atarashii.update + int(self.last - time.time()) - 1
						if interval != interval2:
							gobject.idle_add(lambda: self.atarashii.updatestatus(interval2))
							interval = interval2
						
						self.updating = False
			
				else:
					self.loadOld()
			
			time.sleep(0.1)

	
	# Update with new Tweets ---------------------------------------------------
	# --------------------------------------------------------------------------
	def update(self):
		start = time.time()
		try:
			mentions = self.atarashii.api.mentions(since_id = self.lastID, count = 200)
			timeline = self.atarashii.api.home_timeline(since_id = self.lastID, count = 200)
			for i in mentions:
				i.is_mentioned = True
			
			updates = timeline + mentions
			if len(mentions) > 0:
				updates = self.fixMentions(updates)
				updates.sort(self.compare)	
		
		except Exception, detail:
			self.atarashii.update = 60
			gobject.idle_add(lambda: self.atarashii.error(detail))
			return
		
		if len(updates) > 0:
			self.setLast(updates[0].id)
		
		# Filter non User Tweets
		ulist = []
		uids = []
		for i in updates:
			file = self.getImage(i.user.profile_image_url, i.user.id)
			if i.user.screen_name != self.atarashii.username:
				# Don't add mentions twice
				if not i.id in uids:
					uids.append(i.id)
					ulist.append((i.user.screen_name, i.text, file, None))
			
			self.html.list.append((i, file, False))
		
		# Show Notifications
		if len(ulist) > 0:
			if self.atarashii.settings.isTrue("notify"):
				ulist.reverse()
				self.notify.show(ulist, self.atarashii.settings.isTrue("sound"))
		
		# Update View
		if len(updates) > 0:
			gobject.idle_add(lambda: self.html.push())
		
		else:
			gobject.idle_add(lambda: self.html.render())
		
		# Rate Limiting
		self.updateLimit()
		self.atarashii.updateButton.set_sensitive(True)
		if self.lastID > self.initID:
			self.atarashii.readButton.set_sensitive(True)
	

	# Load older Tweets --------------------------------------------------------
	# --------------------------------------------------------------------------
	def loadOld(self):
		try:
			timeline = self.atarashii.api.home_timeline(max_id = self.loadOlder, count = self.atarashii.loadTweets)
			mentions = self.atarashii.api.mentions(max_id = self.loadOlder, since_id = timeline[len(timeline) -1].id, count = self.atarashii.loadTweets)
			for i in mentions:
				i.is_mentioned = True
			
			updates = timeline + mentions
			if len(mentions) > 0:
				updates = self.fixMentions(updates)
				updates.sort(self.compare)
			
			self.atarashii.maxTweets += len(updates)
			for i in updates:
				file = self.getImage(i.user.profile_image_url, i.user.id)
				self.html.list.append((i, file, True))
			
			self.loadOlder = -1
			self.html.loadOld = True
			self.html.historyLoaded = True
			self.html.historyCount += len(updates)
			self.atarashii.clearButton.set_sensitive(True)
			gobject.idle_add(lambda: self.html.push())
		
		except Exception, detail:
			gobject.idle_add(lambda: self.atarashii.error(detail))
			self.loadOlder = -1
		
		self.atarashii.scroll.show()
		self.atarashii.progress.hide()
	
	# Cache a user avatar	
	def getImage(self, url, id):
		image = url[url.rfind('/')+1:]
		imgdir = os.path.join(self.path, ".atarashii")
		if not os.path.exists(imgdir):
			os.mkdir(imgdir)
		
		file = os.path.join(imgdir, str(id) + '_' + image)
		if not os.path.exists(file):
			urllib.urlretrieve(url, file)
	
		return file		
		

