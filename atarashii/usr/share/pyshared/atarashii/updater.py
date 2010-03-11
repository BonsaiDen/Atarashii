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
import sys
import os
import notify
import gobject
import calendar

from lang import lang
from constants import *

# Import local Tweepy
sys.path.insert(0, __file__[:__file__.rfind('/')])
try:
	import tweepy
	
finally:
	sys.path.pop(0)


class Updater(threading.Thread):
	def __init__(self, main):
		threading.Thread.__init__(self)
		self.main = main
		self.settings = main.settings
		
		# Notifier
		self.notify = notify.Notifier(main)
		
		# Variables
		self.running = True
		self.started = False
		self.doInit = False
		self.refreshNow = False
		self.refreshMessages = False
		
		self.loadHistoryID = HTML_UNSET_ID
		self.loadHistoryMessageID = HTML_UNSET_ID
		self.ratelimit = 150		
		self.messageCounter = 0
		
		self.path = os.path.expanduser('~')
		
		
	# Init the Updater ---------------------------------------------------------
	# --------------------------------------------------------------------------
	def init(self):
		self.gui = self.main.gui
		
		# Init Views
		self.html = self.gui.html
		self.message = self.gui.message
	
		# Reset
		self.messageCounter = 0
		self.doInit = False
		self.started = False
		self.refreshNow = False
		self.main.refreshTimeout = UNSET_TIMEOUT
		self.html.loadHistoryID = HTML_UNSET_ID
		self.message.loadHistoryID = HTML_UNSET_ID
		
		self.message.lastID = HTML_UNSET_ID
		self.html.lastID = HTML_UNSET_ID
		self.message.loaded = HTML_RESET
		self.html.loaded = HTML_RESET	
	
		# InitID = the last read tweet
		self.html.initID = self.main.getLatestID()
		self.message.initID = self.main.getLatestMessageID()
	
		# xAuth Login, yes the app stuff is here, were else should it go?
		# Why should anyone else use the Atarashii App for posting from HIS 
		# client? :D
		auth = tweepy.OAuthHandler("PYuZHIEoIGnNNSJb7nIY0Q", 
					"Fw91zqMpMECFMJkdM3SFM7guFBGiFfkDRu0nDOc7tg", secure = True)		
		try:
			# Try using an old token
			tokenOK = False
			keyName = 'xkey_' + self.main.username
			secretName = 'xsecret_' + self.main.username
			if self.settings.isset(keyName) and self.settings.isset(secretName):
				auth.set_access_token(self.settings[keyName], 
										self.settings[secretName])
				try:
					auth.get_username()
					tokenOK = True
				
				except:
					self.settings[keyName] = ""
					self.settings[secretName] = ""
			
			# Get a new token!
			if not tokenOK:
				gobject.idle_add(lambda: self.gui.enterPassword())
				
				# Wait for password entry
				while self.main.apiTempPassword == None:
					time.sleep(0.1)
				
				# Try to login with the new password
				if self.main.apiTempPassword != "":
					token = auth.get_xauth_access_token(self.main.username, 
													self.main.apiTempPassword)
					
					self.main.apiTempPassword = None
					self.settings[keyName] = token.key
					self.settings[secretName] = token.secret
					
				else:
					gobject.idle_add(lambda: self.main.onLoginFailed())
					self.main.apiTempPassword = None
					return
		
		except Exception, error:
			self.main.apiTempPassword = None
			gobject.idle_add(lambda: self.main.onLoginFailed(error))
			return False
		
		# Create the api instance
		self.api = self.main.api = tweepy.API(auth)
				
		# Set loading to pending
		self.message.loaded = HTML_LOADING
		self.html.loaded = HTML_LOADING
		
		# Lazy loading
		if self.gui.mode == MODE_MESSAGES:
			if not self.getInitMessages():
				self.message.loaded = HTML_RESET
				self.html.loaded = HTML_RESET
				return
			
		elif self.gui.mode == MODE_TWEETS:
			if not self.getInitTweets():
				self.message.loaded = HTML_RESET
				self.html.loaded = HTML_RESET
				return
		
		else: # TODO implement loading of search
			pass
		
		# Stuff ----------------------------------------------------------------
		self.started = True
		gobject.idle_add(lambda: self.main.onLogin())
		gobject.idle_add(lambda: self.gui.checkRead())
		
		# Load other stuff
		if self.gui.mode == MODE_TWEETS:
			self.getInitMessages()
			if self.gui.mode == MODE_MESSAGES:
				gobject.idle_add(lambda: self.gui.showInput())
			else:
				gobject.idle_add(lambda: self.gui.checkRefresh())	
		
		elif self.gui.mode == MODE_MESSAGES:
			self.getInitTweets()
			if self.gui.mode == MODE_TWEETS:
				gobject.idle_add(lambda: self.gui.showInput())
			else:
				gobject.idle_add(lambda: self.gui.checkRefresh())	
		
		else: # TODO implement loading of search
			pass
		
		# Init Timer
		self.main.refreshTime = calendar.timegm(time.gmtime())		
		gobject.idle_add(lambda: self.gui.checkRead())
	
	
	# Load initial tweets ------------------------------------------------------
	def getInitTweets(self):
		updates = []
		try:
			updates = self.tryGetUpdates(self.main.getFirstID())
		
		except Exception, error:
			gobject.idle_add(lambda: self.main.onLoginFailed(error))
			return False
	
		if len(updates) > 0:
			self.setLastTweet(updates[0].id)
	
		updates.reverse()
		for i in updates:
			if i != None:
				imgfile = self.getImage(i)
				self.html.updateList.append((i, imgfile))
		
		def render():
			self.html.pushUpdates()
			self.html.loaded = HTML_LOADED
		
		gobject.idle_add(lambda: render())
		return True
	
	
	# Load initial messages ----------------------------------------------------
	def getInitMessages(self):
		messages = []
		try:
			messages = self.tryGetMessages(self.main.getFirstMessageID())
		
		except Exception, error:
			gobject.idle_add(lambda: self.main.onLoginFailed(error))
			return False
		
		if len(messages) > 0:
			self.setLastMessage(messages[0].id)
		
		messages.reverse()
		for i in messages:
			if i != None:
				imgfile = self.getImage(i, True)
				self.message.updateList.append((i, imgfile))
	
		def render():
			self.message.pushUpdates()
			self.message.loaded = HTML_LOADED
		
		gobject.idle_add(lambda: render())
		return True
	
	
	# Mainloop -----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def run(self):
		while self.running:
			if self.doInit:
				self.init()
		
			elif self.started:
				if self.html.loadHistoryID != HTML_UNSET_ID:
					self.loadHistory()
					
				elif self.message.loadHistoryID != HTML_UNSET_ID:
					self.loadHistoryMessage()
					
				elif self.main.refreshTimeout != HTML_UNSET_ID:
					self.checkForUpdate()
			
			time.sleep(0.1)
	
	
	# Update -------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def checkForUpdate(self):
		if self.main.refreshTime == UNSET_TIMEOUT:
			return
	
		if calendar.timegm(time.gmtime()) > self.main.refreshTime + \
			self.main.refreshTimeout or self.refreshNow or self.refreshMessages:
			
			self.main.isUpdating = True
			self.update()
			gobject.idle_add(
						lambda: self.gui.refreshButton.set_sensitive(True))
			
			gobject.idle_add(lambda: self.gui.checkRead())
			self.main.refreshTime = calendar.timegm(time.gmtime())
			self.refreshMessages = False
			self.refreshNow = False
			self.main.isUpdating = False
			gobject.idle_add(lambda: self.gui.updateStatus(True))
	
	
	def update(self):
		# Fetch Tweets
		updates = []
		if not self.refreshMessages:
			try:
				updates = self.tryGetUpdates(self.html.lastID)
			
			# Something went wrong...
			except Exception, error:
				gobject.idle_add(lambda: self.html.render())
				gobject.idle_add(lambda: self.gui.showError(error))
				self.main.refreshTimeout = 60
				self.main.refreshTime = calendar.timegm(time.gmtime())
				return
		
			if len(updates) > 0:
				self.setLastTweet(updates[0].id)
		
		# Messages
		messages = []
		if (self.messageCounter > 1 or self.refreshMessages) and \
			not self.refreshNow:

			try:
				messages = self.tryGetMessages(self.message.lastID)

			# Something went wrong...
			except Exception, error:
				gobject.idle_add(lambda: self.message.render())	
				gobject.idle_add(lambda: self.gui.showError(error))
				return
			
			if len(messages) > 0:
				self.setLastMessage(messages[0].id)
				
			self.messageCounter = 0
		
		elif not self.refreshNow:
			self.messageCounter += 1
		
		# Notify
		self.showNotifications(updates, messages)
		
		# Update View
		if len(updates) > 0:
			gobject.idle_add(lambda: self.html.pushUpdates())
		
		else:
			gobject.idle_add(lambda: self.html.render())		
		
		if len(messages) > 0:
			gobject.idle_add(lambda: self.message.pushUpdates())
		
		else:
			gobject.idle_add(lambda: self.message.render())		
	
	
	# Notifications ------------------------------------------------------------
	# --------------------------------------------------------------------------
	def showNotifications(self, updates, messages):
		tweetList = []
		tweetIDS = []
		messageIDS = []
		for i in messages:
			imgfile = self.getImage(i, True)
			if i.sender.screen_name.lower() != self.main.username.lower():
				if not i.id in messageIDS:
					messageIDS.append(i.id)
					tweetList.append([
						lang.notificationMessage % i.sender.screen_name, 
						i.text, imgfile])
			
			self.message.updateList.append((i, imgfile))	
		
		for i in updates:
			imgfile = self.getImage(i)
			if i.user.screen_name.lower() != self.main.username.lower():
				# Don't add mentions twice
				if not i.id in tweetIDS:
					tweetIDS.append(i.id)
					if hasattr(i, "retweeted_status"):
						name = "RT %s" % i.retweeted_status.user.screen_name
						text = i.retweeted_status.text
					else:
						name = i.user.screen_name
						text = i.text
					
					tweetList.append([name, text, imgfile])
			
			self.html.updateList.append((i, imgfile))
		
		# Show Notifications
		count = len(tweetList)
		if count > 0 and self.settings.isTrue("notify"):
			tweetList.reverse()
			if count > 1:
				for num, i in enumerate(tweetList):
					tweetList[num][0] = lang.notificationIndex % (
										tweetList[num][0], num+1, count)
			
			self.notify.show(tweetList, self.settings.isTrue("sound"))
	
	
	# Load History -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def loadHistory(self):
		updates = []
		try:
			updates = self.tryGetUpdates(maxID = self.html.loadHistoryID, 
										maxCount = self.main.loadTweetCount)
		
		# Something went wrong...
		except Exception, error:
			self.html.loadHistoryID = HTML_UNSET_ID
			self.main.isLoadingHistory = False
			gobject.idle_add(lambda: self.gui.showError(error))
			return
		
		# Loaded
		self.main.maxTweetCount += len(updates)
		for i in updates:
			imgfile = self.getImage(i)
			self.html.historyList.append((i, imgfile))
		
		self.html.loadHistoryID = HTML_UNSET_ID
		self.main.isLoadingHistory = False
		
		if len(updates) > 0:
			self.html.loadHistory = True
			self.html.historyLoaded = True
			self.html.historyCount += len(updates)
			self.gui.historyButton.set_sensitive(True)
		
		gobject.idle_add(lambda: self.html.pushUpdates())
		gobject.idle_add(lambda: self.gui.showInput())
	
	# Load Message History -----------------------------------------------------
	def loadHistoryMessage(self):
		messages = []
		try:
			messages = self.tryGetMessages(maxID = self.message.loadHistoryID, 
										maxCount = self.main.loadMessageCount)
		
		# Something went wrong...
		except Exception, error:
			self.message.loadHistoryID = HTML_UNSET_ID
			self.main.isLoadingHistory = False
			gobject.idle_add(lambda: self.gui.showError(error))
			return
		
		# Loaded
		self.main.maxMessageCount += len(messages)
		for i in messages:
			imgfile = self.getImage(i, True)
			self.message.historyList.append((i, imgfile))
		
		self.message.loadHistoryID = HTML_UNSET_ID
		self.main.isLoadingHistory = False
		
		if len(messages) > 0:
			self.message.loadHistory = True
			self.message.historyLoaded = True
			self.message.historyCount += len(messages)
			self.gui.historyButton.set_sensitive(True)
		
		gobject.idle_add(lambda: self.message.pushUpdates())
		gobject.idle_add(lambda: self.gui.showInput())
	
	
	# Main Function that fetches the updates -----------------------------------
	# --------------------------------------------------------------------------
	def getUpdates(self, sinceID = 0, maxID = None, maxCount = 200):
		gobject.idle_add(lambda: self.gui.updateStatus(True))
		updates = []
		mentions = []
	
		# Get new Tweets
		if sinceID != HTML_UNSET_ID:
			if maxID == None:
				mentions = self.api.mentions(since_id = sinceID, 
													count = maxCount)
				updates = self.api.home_timeline(since_id = sinceID, 
														count = maxCount)
				
			else:				
				updates = self.api.home_timeline(max_id = maxID, 
														count = maxCount)
				if len(updates) > 0:
					mentions = self.api.mentions(max_id = maxID, 
										since_id = updates[len(updates) - 1].id, 
										count = maxCount)
		
		# Init the Timeline
		else:
			updates = self.api.home_timeline(count = self.main.loadTweetCount)
			if len(updates) > 0:
				mentions = self.api.mentions(
								since_id = updates[len(updates) - 1].id,
								count = 200)
				
		# Sort and Stuff
		for i in mentions:
			i.is_mentioned = True
		
		self.refreshNow = False
		
		# Ratelimit
		self.updateLimit()
		
		# Return
		updates = updates + mentions
		if len(mentions) > 0:
			return self.processUpdates(updates)
		
		else:
			return updates
	
	# Try to get updates X times and then fail
	def tryGetUpdates(self, sinceID = 0, maxID = None, maxCount = 200):
		count = 0
		while True:
			count += 1
			try:
				# Try to get the updates and then break
				return self.getUpdates(sinceID = sinceID, maxID = maxID, 
								maxCount = maxCount)
			
			# Something went wrong, either try it again or break with the error
			except Exception, error:
				if count == 2:
					raise error
	
	
	# Main Function that fetches the messages ----------------------------------
	# --------------------------------------------------------------------------
	def getMessages(self, sinceID = 0, maxID = None, maxCount = 200):
		messages = []
	
		# Get new Tweets
		if sinceID != HTML_UNSET_ID:
			if maxID == None:
				messages = self.api.direct_messages(since_id = sinceID, 
													count = maxCount)
				messages += self.api.sent_direct_messages(since_id = sinceID, 
													count = maxCount)
				
			else:				
				messages = self.api.direct_messages(max_id = maxID, 
													count = maxCount)
				messages += self.api.sent_direct_messages(max_id = maxID, 
													count = maxCount)
		
		# Init the Timeline
		else:
			messages = self.api.direct_messages(
											count = self.main.loadMessageCount)
			messages += self.api.sent_direct_messages(
											count = self.main.loadMessageCount)
		
		self.refreshMessages = False
		
		# Ratelimit
		self.updateLimit()
		
		# Return
		return self.processUpdates(messages)
	
	# Try to get messages X times and then fail
	def tryGetMessages(self, sinceID = 0, maxID = None, maxCount = 200):
		count = 0
		while True:
			count += 1
			try:
				# Try to get the updates and then break
				return self.getMessages(sinceID = sinceID, maxID = maxID, 
								maxCount = maxCount)
			
			# Something went wrong, either try it again or break with the error
			except Exception, error:
				if count == 2:
					raise error
	
	
	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def setLastTweet(self, itemID):
		self.html.lastID = itemID
		self.settings['lasttweet_' + self.main.username] = itemID
		if len(self.html.items) > 0:
			self.html.newestID = self.html.items[len(self.html.items) - 1][0].id
	
	def setLastMessage(self, itemID):
		self.message.lastID = itemID
		self.settings['lastmessage_' + self.main.username] = itemID
		if len(self.message.items) > 0:
			self.message.newestID = self.message.items[
											len(self.message.items) - 1][0].id
	
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
		ratelimit = self.api.oauth_rate_limit_status()
		if ratelimit == None:
			self.main.refreshTimeout = 60
			return
		
		minutes = (ratelimit['reset'] - calendar.timegm(time.gmtime())) / 60
		limit = ratelimit['remaining']
		if limit > 0:
			limit = limit / (2.0 + (2.0 / 2))
			self.main.refreshTimeout = int(minutes / limit * 60 * 1.10)
			if self.main.refreshTimeout < 45:
				self.main.refreshTimeout = 45
		
		# Check for ratelimit
		count = ratelimit['limit']
		if count < 350:
			if not self.main.rateWarningShown:
				self.main.rateWarningShown= True
				gobject.idle_add(lambda: self.gui.showWarning(count))
		
		else:
			self.main.rateWarningShown = False
	
	# Cache a user avatar	
	def getImage(self, item, message = False):#url, userid):
		if message:
			url = item.sender.profile_image_url
			userid = item.sender.id
		else:
			if hasattr(item, "retweeted_status"):
				url = item.retweeted_status.user.profile_image_url
				userid = item.retweeted_status.user.id	
			else:
				url = item.user.profile_image_url
				userid = item.user.id
	
	
		image = url[url.rfind('/')+1:]
		imgdir = os.path.join(self.path, ".atarashii")
		if not os.path.exists(imgdir):
			os.mkdir(imgdir)
		
		imgfile = os.path.join(imgdir, str(userid) + '_' + image)
		if not os.path.exists(imgfile):
			urllib.urlretrieve(url, imgfile)
		
		return imgfile		
		
