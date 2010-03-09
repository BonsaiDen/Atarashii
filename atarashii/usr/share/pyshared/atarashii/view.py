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
		self.position = 0
		self.offsetCount = 0
		self.historyLoaded = False
		self.historyPosition = -1
		self.historyCount = 0
		self.firstLoad = True
		self.newestID = -1
		self.newitems = False
		self.loadHistory = False
		self.loadHistoryID = -1
		self.loaded = -1
		self.initID = -1
		self.lastID = -1
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
			</body>""" % (self.main.getImage(), self.langLoading), "start")
	
	
	def splash(self):
		self.offsetCount = 0
		self.renderHTML("""
			<body class="unloaded">
				<div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
			</body>""" % (self.main.getImage(), lang.htmlWelcome), "splash")


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
		if len(self.items) > 0:
			self.renderHTML("""
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
				</body>""" % ("".join(renderitems), 
								self.items[0][0].id, self.langLoad), "render")
		
		else:
			self.renderHTML("""
				<body class="unloaded">
					<div class="loading"><b>%s</b></div>
				</body>""" % self.langEmpty, "render")
	
	
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
			if self.mode == "render":
				self.render()
	
			elif self.mode == "start":
				self.start()
			
			elif self.mode == "splash":
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
	
		self.render()

	# Add items to the internal List
	def add(self, tweet):		
		itemid = tweet[0].id
		found = False
		for i in self.items:
			if i[0].id == itemid:
				found = True
				break
		
		if not found:
			if tweet[2]:
				self.items.insert(0, tweet)

			else:
				self.items.append(tweet)
			
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
		
		# Set the latest tweet for reloading on startup
		if len(self.items) > 0:
			id = len(self.items) - self.itemCount
			if id < 0:
				id = 0
			
			setting = self.firstSetting + self.main.username
			self.main.settings[setting] = self.items[id][0].id - 1
			
		# Newest Stuff
		if self.newestID == -1:
			self.newestID = self.initID
	
	
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
				if self.loadHistoryID != -1:
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
				self.main.retweetNum = num
				self.main.retweetText = self.unescape(self.getText(num))
				self.main.retweetUser = name
				self.main.gui.text.retweet()
				self.main.gui.text.htmlFocus()
			
			def newRetweet():
				self.main.retweet(name, tweetid)
			
			# Which style?
			rt = self.main.settings["retweets"]
			if name.lower() == self.main.username.lower():
				rt = 2
			
			if rt == 0:
				self.main.gui.askForRetweet(name, newRetweet, oldRetweet)
			
			elif rt == 1:
				newRetweet()
			
			elif rt == 2:
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

