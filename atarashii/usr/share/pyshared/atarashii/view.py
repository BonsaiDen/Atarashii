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


# Basic HTML View --------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import calendar
import rfc822
import urllib
import webkit

import math

import time
import datetime
import webbrowser

from lang import lang
import format


class HTMLView(webkit.WebView):
	def __init__(self, main, gui, scroll):
		self.main = main
		self.gui = gui
		
		webkit.WebView.__init__(self)
		self.connect("navigation-requested", self.openLink)
		self.connect("load-finished", self.loaded)
		self.connect("load-started", self.onLoading)
		self.connect("focus-in-event", self.gui.text.htmlFocus)
		self.scroll = scroll
		self.set_maintains_back_forward_list(False)
		self.mode = ""
		self.count = 0
		self.formatter = format.Formatter()
		self.init(True)
	
	
	# Screens ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		self.mode = "start"
		self.isRendering = True
		self.offsetCount = 0
		self.load_string("""
		<html>
			<head>
				<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
				<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
			</head>
			<body class="unloaded">
				<div class="loading"><b>%s</b></div>
			</body>
		</html>""" % (self.main.getResource("atarashii.css"), lang.htmlLoading), "text/html", "UTF-8", "file:///main/")
	
	def splash(self):
		self.mode = "splash"
		self.isRendering = True
		self.offsetCount = 0
		self.load_string("""
		<html>
			<head>
				<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
				<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
			</head>
			<body class="unloaded">
				<div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
			</body>
		</html>""" % (self.main.getResource("atarashii.css"), self.main.getImage(), lang.htmlWelcome), "text/html", "UTF-8", "file:///main/")

	
	# Initiate a empty timeline ------------------------------------------------
	# --------------------------------------------------------------------------
	def init(self, splash = False):
		self.isRendering = False
		self.tweets = []
		self.updateList = []
		self.position = 0
		self.offsetCount = 0
		self.historyLoaded = False
		self.historyPosition = -1
		self.historyCount = 0
		self.firstLoad = True
		self.newestID = -1
		self.newTweets = False
		self.loadHistory = False
		
		if splash:
			self.splash()
	
	# Fix scrolling isses on page load
	def loaded(self, *args):
		self.isRendering = False
		if len(self.tweets) > 0 and self.newTweets and not self.loadHistory:
			try:
				self.execute_script('document.title=document.getElementById("newcontainer").offsetHeight;')
				offset = int(self.get_main_frame().get_title())
			
			except:
				offset = 0
		
		else:
			offset = 0
		
		if not self.firstLoad and self.position > 0:
			self.scroll.get_vscrollbar().set_value(self.position + offset)
		
		elif self.firstLoad:
			height = self.gui.getHeight(self)
			if offset > height:
				self.scroll.get_vscrollbar().set_value(offset - height)
		
		if len(self.tweets) > 0:
			self.firstLoad = False
		
		self.loadHistory = False
		self.newTweets = False
	
	
	# Clear the History
	def clear(self):
		self.historyLoaded = False
		self.tweets = self.tweets[self.historyCount:]
		self.main.maxTweetCount -= self.historyCount
		self.historyCount = 0
		self.main.gui.historyButton.set_sensitive(False)
		self.render()
	
	def read(self):
		if self.main.updater.initID != self.main.getLatestID():
			self.main.gui.readButton.set_sensitive(False)
			self.main.updater.initID = self.main.getLatestID()
			if not self.historyLoaded:
				pos = len(self.tweets) - self.main.loadTweetCount
				if pos < 0:
					pos = 0
				
				self.tweets = self.tweets[pos:]
			
			self.render()
	
	
	# Add Items ----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def pushUpdates(self):
		while len(self.updateList) > 0:
			self.add(self.updateList.pop(0))
	
		self.render()

	# Add Tweets to the internal List
	def add(self, tweet):		
		tweetid = tweet[0].id
		found = False
		for i in self.tweets:
			if i[0].id == tweetid:
				found = True
				break
		
		if not found:
			if tweet[2]:
				self.tweets.insert(0, tweet)

			else:
				self.tweets.append(tweet)
			
			self.newTweets = True
			if len(self.tweets) > self.main.maxTweetCount:
				self.tweets.pop(0)
	
	def compare(self, x, y):
		if x[0].id > y[0].id:
			return 1
	
		elif x[0].id < y[0].id:
			return -1
		
		else:
			return 0
	
	
	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def relative_time(self, t):
		delta = long(calendar.timegm(time.gmtime())) - long(calendar.timegm(t.timetuple()))
		if delta <= 1:
			return lang.htmlAboutSecond
		
		elif delta <= 45:
			return lang.htmlSecond % delta
		
		elif delta <= 90:
			return lang.htmlAboutMinute
		
		elif delta <= 60 * 45:
			return lang.htmlMinute % math.ceil(delta / 60.0)
			
		elif delta <= 60 * 60 * 1.5:
			return lang.htmlAboutHour
			
		elif delta <= 60 * 60 * 20:
			return lang.htmlHour % math.ceil(delta / (60.0 * 60.0))
			
		elif delta <= 60 * 60 * 24 * 1.5:
			return lang.htmlAboutDay
			
		elif delta <= 60 * 60 * 48:
			return lang.htmlYesterday
			
		elif delta <= 60 * 60 * 96:
			return lang.htmlDay % math.ceil(delta / (60.0 * 60.0 * 24.0))
		
		else:
			t = time.localtime(calendar.timegm(t.timetuple()))
			return time.strftime(lang.htmlExact, t)
				
	def absolute_time(self, t):
		delta = long(calendar.timegm(time.gmtime())) - long(calendar.timegm(t.timetuple()))
		t = time.localtime(calendar.timegm(t.timetuple()))
		if delta <= 60 * 60 * 24:
			return time.strftime(lang.htmlTime, t)
			
		else:
			return time.strftime(lang.htmlTimeDay, t)
	
	# Open a Link
	def openLink(self, view, frame, req):
		uri = req.get_uri()
		if uri.startswith("file:///"):
			return False
		
		if uri.startswith("more:"):
			if not self.main.isLoadingHistory:
				self.main.updater.loadHistoryID = int(uri.split(":")[1]) - 1
				if self.main.updater.loadHistoryID != -1:
					self.main.isLoadingHistory = True
					self.gui.showProgress()
					gobject.idle_add(lambda: self.main.gui.updateStatus(True))
		
		elif uri.startswith("moremessages:"):
			if not self.main.isLoadingHistory:
				self.main.updater.loadHistoryMessageID = int(uri.split(":")[1]) - 1
				if self.main.updater.loadHistoryMessageID != -1:
					self.main.isLoadingHistory = True
					self.gui.showProgress()
					gobject.idle_add(lambda: self.main.gui.updateStatus(True))
		
		elif uri.startswith("reply:"):
			foo, self.main.replyUser, self.main.replyID, num = uri.split(":")
			gobject.idle_add(lambda: self.main.reply(int(num)))
		
		elif uri.startswith("message:"):
			foo, self.main.messageUser, self.main.messageID, num = uri.split(":")
			self.main.messageText = self.tweets[int(num)][0].text
			gobject.idle_add(lambda: self.main.message(int(num)))
		
		elif uri.startswith("retweet:"):
			self.main.retweetNum = int(uri.split(":")[1])
			self.main.retweetText = self.tweets[self.main.retweetNum][0].text
			self.main.retweetUser = self.tweets[self.main.retweetNum][0].user.screen_name
			gobject.idle_add(lambda: self.main.retweet())
		
		else:
			webbrowser.open(uri)
		
		return True
	
	
	# Fix Reloading
	def onLoading(self, *args):
		if not self.isRendering:
			if self.mode == "render":
				self.render()
	
			elif self.mode == "start":
				self.start()
			
			elif self.mode == "splash":
				self.splash()
				
			return True
