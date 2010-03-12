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
import gobject
import webkit

import calendar
import math
import time
import datetime
import webbrowser

import format
from lang import lang
from constants import *


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
		self.mode = HTML_STATE_NONE
		self.count = 0
		self.formatter = format.Formatter()
		self.getLatest = None
		self.itemCount = 20
		self.getItemCount = None
		self.setItemCount = None
		
		self.langLoading = ""
		self.langLoad = ""
		self.langEmpty = ""
		
		self.init(True)
	
	
	# Initiate a empty timeline ------------------------------------------------
	# --------------------------------------------------------------------------
	def init(self, splash = False):
		self.isRendering = False
		self.items = []
		self.updateList = []
		self.historyList = []
		self.position = 0
		self.offsetCount = 0
		self.historyLoaded = False
		self.historyPosition = HTML_UNSET_ID
		self.historyCount = 0
		self.firstLoad = True
		self.newestID = HTML_UNSET_ID
		self.newitems = False
		self.loadHistory = False
		self.loadHistoryID = HTML_UNSET_ID
		self.loaded = HTML_UNSET_ID
		self.initID = HTML_UNSET_ID
		self.lastID = HTML_UNSET_ID
		self.count = 0
		
		if splash:
			self.splash()
	
	
	# Loading HTML -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		self.offsetCount = 0
		self.renderHTML("""
			<body class="unloaded">
				<div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
			</body>""" % (self.main.getImage(), self.langLoading),
			HTML_STATE_START)
	
	
	def splash(self):
		self.offsetCount = 0
		self.renderHTML("""
			<body class="unloaded">
				<div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
			</body>""" % (self.main.getImage(), lang.htmlWelcome),
			HTML_STATE_SPLASH)


	# Render the actual HTML ---------------------------------------------------
	# --------------------------------------------------------------------------	
	def renderHTML(self, html, mode):
		self.mode = mode
		self.isRendering = True
		self.load_string("""
		<html>
		<head>
		<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
		<link rel="stylesheet" type="text/css" media="screen" href="file://%s"/>
		</head>
		%s
		</html>""" % (self.main.getResource("atarashii.css"), html),
						"text/html", "UTF-8", "file:///main/")
	
	def setHTML(self, renderitems):
		self.main.gui.setTitle()
		if len(self.items) > 0:
			self.renderHTML("""
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
				</body>""" % ("".join(renderitems), 
								self.items[0][0].id, self.langLoad),
								HTML_STATE_RENDER)
		
		else:
			self.renderHTML("""
				<body class="unloaded">
					<div class="loading"><b>%s</b></div>
				</body>""" % self.langEmpty, HTML_STATE_RENDER)
	
	
	def insertSpacer(self, item, user, highlight, mentioned, message = False, 
					next = False):
		
		# Red spacer that indicates something did fall through
		spacer = "foo"
		
		
		# New Tweets
		if item.id > self.initID:
			# Name change
			if self.lastname != user.screen_name or self.newTimeline:
				spacer = "1" # Dark Gray
			
			else:
				# More @username
				if highlight:
					if not self.lastHighlight:
						spacer = "1" # Dark Gray
					else:
						spacer = "4" if message else "6" # Normal/Dark Blue
				
				# More mentions
				elif mentioned:
					spacer = "5" # Yellow
				
				# Just more normal tweets
				else:
					if next and self.lastHighlight:
						spacer = "1" # Dark Gray
					else:
						spacer = "6" if message else "4" # Dark/Normal Blue
		
		# Old Tweets
		else:	
			# Name change
			if self.lastname != user.screen_name or self.newTimeline:
				spacer = "" # Normal Gray
			
			else:
				# More @username
				if highlight:
					if not self.lastHighlight:
						spacer = "" # Normal Gray
					else:
						spacer = "2" if message else "7" # White/Light Blue
				
				# More mentions
				elif mentioned:
					spacer = "5" # Yellow
				
				# Just more normal tweets
				else:
					if next and self.lastHighlight:
						spacer = "" # Normal Gray
					else:
						spacer = "7" if message else "2" # Light Blue/White		
		
		return '<div class="spacer%s"></div>' % spacer
	
	
	# Fix scrolling isses on page load -----------------------------------------
	# --------------------------------------------------------------------------
	def getOffset(self):
		try:
			self.execute_script(
				'''document.title=
					document.getElementById("newcontainer").offsetHeight;''')
			return int(self.get_main_frame().get_title())
		
		except:
			return 0
	
	def loaded(self, *args):
		self.isRendering = False
		if len(self.items) > 0 and self.newitems and not self.loadHistory:
			offset = self.getOffset()
		
		else:
			offset = 0
		
		# Re-scroll
		if not self.firstLoad and self.position > 0:
			pos = self.position + offset
			self.checkScroll(pos)
			gobject.timeout_add(25, lambda: self.checkScroll(pos))
		
		# scroll to first new tweet
		elif self.firstLoad or (offset > 0 and self.position == 0):
			height = self.gui.getHeight(self)
			if offset > height:
				self.scroll.get_vscrollbar().set_value(offset - height)
				gobject.timeout_add(25, self.checkOffset)

		if len(self.items) > 0:
			self.firstLoad = False
		
		self.loadHistory = False
		self.newitems = False
	
	
	# Double check for some stupid scrolling bugs with webkit
	def checkScroll(self, pos):
		self.scroll.get_vscrollbar().set_value(pos)
	
	def checkOffset(self):
		offset = self.getOffset()
		height = self.gui.getHeight(self)
		if offset > height:
			self.scroll.get_vscrollbar().set_value(offset - height)
	
		
	# Fix Reloading
	def onLoading(self, *args):
		if not self.isRendering:
			if self.mode == HTML_STATE_RENDER:
				self.render()
	
			elif self.mode == HTML_STATE_START:
				self.start()
			
			elif self.mode == HTML_STATE_SPLASH:
				self.splash()
				
			return True
	
	
	# History / Read Button ----------------------------------------------------
	# --------------------------------------------------------------------------
	def clear(self):
		self.historyLoaded = False
		self.items = self.items[self.historyCount:]
		self.setItemCount(self.getItemCount() - self.historyCount)
		self.historyCount = 0
		self.main.gui.historyButton.set_sensitive(False)
		self.render()
	
	def read(self):
		if self.initID != self.getLatest():
			self.main.gui.readButton.set_sensitive(False)
			self.initID = self.getLatest()
			if not self.historyLoaded:
				pos = len(self.items) - self.itemCount
				if pos < 0:
					pos = 0
				
				self.items = self.items[pos:]
			
			self.render()
	
	
	# Add Items ----------------------------------------------------------------
	# --------------------------------------------------------------------------
	def pushUpdates(self):
		while len(self.updateList) > 0:
			self.add(self.updateList.pop(0))
	
		while len(self.historyList) > 0:
			self.add(self.historyList.pop(0), True)
		
		self.render()
	
	# Add items to the internal List
	def add(self, item, append = False):		
		# Don't add items with the same ID twice
		if not item[0].id in [i[0].id for i in self.items]:
			if append:
				self.items.insert(0, item)

			else:
				self.items.append(item)
			
			self.newitems = True
			if len(self.items) > self.main.maxTweetCount:
				self.items.pop(0)
	
	
	def compare(self, x, y):
		if x[0].id > y[0].id:
			return 1
	
		elif x[0].id < y[0].id:
			return -1
		
		else:
			return 0
	
	
	# Setup rendering ----------------------------------------------------------
	# --------------------------------------------------------------------------
	def initRender(self):
		self.position = self.scroll.get_vscrollbar().get_value()
		self.items.sort(self.compare)
		self.count = 0
		
		# Set the latest tweet for reloading on startup
		if len(self.items) > 0:
			itemid = len(self.items) - self.itemCount
			if itemid < 0:
				itemid = 0
			
			setting = self.firstSetting + self.main.username
			self.main.settings[setting] = self.items[itemid][0].id - 1
			
		# Newest Stuff
		if self.newestID == HTML_UNSET_ID:
			self.newestID = self.initID
	
		# Newest Stuff
		self.newest = False
		self.newestAvatar = False
		self.newTimline = False
	
	
	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
	def render(self):
		self.initRender()
		self.lastname = ""
		self.lastHighlight = False

		# Do the rendering!
		self.renderitems = []
		for num, obj in enumerate(self.items):
			item, img = obj
			self.isNewTimeline(item)		
			html = self.renderItem(num, item, img)
			
			# Close Newest Container
			if item.id == self.newestID:
				html = '</div>' + html
			
			self.renderitems.insert(0, html)
		
		# Render
		self.setHTML(self.renderitems)
	
	
	# Helpers ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def relative_time(self, t):
		delta = long(calendar.timegm(time.gmtime())) - \
				long(calendar.timegm(t.timetuple()))
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
			
		elif delta <= 60 * 60 * 72:
			return lang.htmlDay % math.ceil(delta / (60.0 * 60.0 * 24.0))
		
		else:
			t = time.localtime(calendar.timegm(t.timetuple()))
			return time.strftime(lang.htmlExact, t)
	
	def absolute_time(self, t):
		delta = long(calendar.timegm(time.gmtime())) - \
				long(calendar.timegm(t.timetuple()))
		t = time.localtime(calendar.timegm(t.timetuple()))
		if delta <= 60 * 60 * 24:
			return time.strftime(lang.htmlTime, t)
			
		else:
			return time.strftime(lang.htmlTimeDay, t)
	
	# Checks for new Tweets
	def isNewTimeline(self, item):
		self.newTimeline = item.id > self.initID
		if self.newTimeline:
			self.count += 1
		
		if self.newest or self.initID == 0:
			self.newTimeline = False
		
		if self.newTimeline:
			self.newest = True
		
	def isNewAvatar(self, num):
		if num < len(self.items) - 1:
			self.newAvatar = self.items[num + 1][0].id > self.initID
		else:
			self.newAvatar = False
			
		if num > 0 and self.items[num - 1][0].id <= self.initID:
			self.newTimeline = False
		
		if self.newestAvatar or self.initID == 0:
			self.newAvatar = False
		
		if self.newAvatar:
			self.newestAvatar = True	
	
	
	# Handle the opening of links ----------------------------------------------
	# --------------------------------------------------------------------------
	def openLink(self, view, frame, req):
		uri = req.get_uri()
		
		# Local links
		if uri.startswith("file:///"):
			return False
		
		# Load history
		if uri.startswith("more:"):
			if not self.main.isLoadingHistory:
				self.loadHistoryID = int(uri.split(":")[1]) - 1
				if self.loadHistoryID != HTML_UNSET_ID:
					self.main.isLoadingHistory = True
					self.gui.showProgress()
					gobject.idle_add(lambda: self.main.gui.updateStatus(True))
					self.main.gui.text.htmlFocus()
		
		# Replies
		elif uri.startswith("reply:"):
			foo, self.main.replyUser, self.main.replyID, num = uri.split(":")
			self.main.gui.text.reply()
			self.main.gui.text.htmlFocus()
		
		# Send a message
		elif uri.startswith("message:"):
			o, self.main.messageUser, self.main.messageID, num = uri.split(":")
			self.main.messageText = self.unescape(self.items[int(num)][0].text)
			self.main.gui.text.message()
			self.main.gui.text.htmlFocus()
		
		# Retweet someone
		elif uri.startswith("retweet:"):
			foo, num, tweetid = uri.split(":")
			num, tweetid = int(num), long(tweetid)
			name = self.getUser(num).screen_name
			def oldRetweet():
				self.main.retweetText = self.unescape(self.getText(num))
				self.main.retweetUser = name
				self.main.gui.text.retweet()
				self.main.gui.text.htmlFocus()
			
			def newRetweet():
				self.main.retweet(name, tweetid)
			
			# Which style?
			rt = self.main.settings["retweets"]
			if name.lower() == self.main.username.lower():
				rt = RETWEET_OLD
			
			if rt == RETWEET_ASK:
				self.main.gui.askForRetweet(name, newRetweet, oldRetweet)
			
			elif rt == RETWEET_NEW:
				newRetweet()
			
			elif rt == RETWEET_OLD:
				oldRetweet()
		
		# Regular links
		else:
			webbrowser.open(uri)
		
		return True
		
	# Unescape chars
	def unescape(self, text):
		ent = {
			"&": "&amp;", 
			'"': "&quot;", 
			"'": "&apos;", 
			">": "&gt;", 
			"<": "&lt;"
		}
		for k, v in ent.iteritems():
			text = text.replace(v, k)
		
		return text

