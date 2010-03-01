#  This file is part of  main.
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


# HTML View --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import calendar
import rfc822
import urllib
import webkit

import re
import math

import time
import datetime
import webbrowser

from lang import lang
import format


class HTML(webkit.WebView):
	def __init__(self, main, gui):
		self.main = main
		self.gui = gui
		
		webkit.WebView.__init__(self)
		self.connect("navigation-requested", self.openLink)
		self.connect("load-finished", self.loaded)
		self.connect("load-started", self.onLoading)
		self.connect("focus-in-event", self.gui.text.htmlFocus)
		self.scroll = self.gui.htmlScroll
		self.set_maintains_back_forward_list(False)
		self.mode = ""
		self.formatter = format.Formatter()
		self.init(True)
	
	
	# Screens ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
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
		self.mode = "start"
	
	def splash(self):
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
		self.mode = "splash"
	
	
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
	
	
	# Add Tweets ---------------------------------------------------------------
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

	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
	def render(self):	
		self.isRendering = True
		self.mode = "render"
		self.tweets.sort(self.compare)
		
		# Set the latest tweet for reloading on startup
		self.username = self.main.settings['username']
		if len(self.tweets) > 0:
			id = len(self.tweets) - self.main.loadTweetCount
			if id < 0:
				id = 0
			
			self.main.settings['firsttweet_' + self.username] = str(self.tweets[id][0].id - 1)
		
		# Render
		self.position = self.scroll.get_vscrollbar().get_value()
		renderTweets = []
		lastname = ""
				
		# Newest Stuff
		if self.newestID == -1:
			self.newestID = self.main.updater.initID
		
		newest = False
		newestAvatar = False
		container = False
		lastHighlight = False
		
		# Do the rendering!
		for num, obj in enumerate(self.tweets):
			tweet, img, mode = obj
			
			# Fix some stuff for the seperation of continous new/old tweets
			newTimeline = tweet.id > self.main.updater.initID
			if newest or self.main.updater.initID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML
			text = self.formatter.parse(tweet.text)
			self.atUser = self.username in self.formatter.users
			highlight = hasattr(tweet, "is_mentioned") and tweet.is_mentioned or self.atUser
			
			# Spacer
			if num > 0:
				if lastname != tweet.user.screen_name or newTimeline:
					renderTweets.insert(0, '<div class="spacer"></div>')
				
				elif highlight != lastHighlight:
					renderTweets.insert(0, '<div class="spacer3"></div>')
					
				elif hasattr(tweet, "is_mentioned") and tweet.is_mentioned:
					renderTweets.insert(0, '<div class="spacer5"></div>')
					
				elif highlight:
					renderTweets.insert(0, '<div class="spacer6"></div>')
					
				elif tweet.id > self.main.updater.initID:
					renderTweets.insert(0, '<div class="spacer4"></div>')
					
				else:
					renderTweets.insert(0, '<div class="spacer2"></div>')
			
			lastname = tweet.user.screen_name
			lastHighlight = highlight
			
			# Is this tweet a reply?
			reply = ""
			if tweet.in_reply_to_screen_name and tweet.in_reply_to_status_id:
				reply = ('<a href="http://twitter.com/%s/statuses/%d">' + lang.htmlInReply + '</a>') 
				reply = reply % (tweet.in_reply_to_screen_name, tweet.in_reply_to_status_id, tweet.in_reply_to_screen_name)
			
			# Realname
			profilename = tweet.user.name.strip()
			if not tweet.user.name.endswith('s') and not tweet.user.name.endswith('x'):
				profilename += "'s"
				
			else:
				profilename += "'"
			
			# Display Avatar?
			if num < len(self.tweets) - 1:
				newAvatar = self.tweets[num + 1][0].id > self.main.updater.initID
			else:
				newAvatar = False
				
			if num > 0 and self.tweets[num - 1][0].id <= self.main.updater.initID:
				newTimeline = False
			
			if newestAvatar or self.main.updater.initID == 0:
				newAvatar = False
			
			if newAvatar:
				newestAvatar = True
			
			if (num < len(self.tweets) - 1 and (tweet.user.screen_name != self.tweets[num + 1][0].user.screen_name or newAvatar)) or num == len(self.tweets) - 1 or newTimeline:
				avatar = ('<a href="http://twitter.com/%s"><img width="32" src="file://%s" title="' + lang.htmlInfo + '"/></a>') 
				avatar = avatar % (tweet.user.screen_name, img, tweet.user.name, tweet.user.followers_count, tweet.user.friends_count, tweet.user.statuses_count)
			
			else:
				avatar = ""
			
			# At?
			if hasattr(tweet, "is_mentioned") and tweet.is_mentioned:
				clas = 'mentioned'
				
			elif self.atUser:
				clas = 'highlight'
				
			elif tweet.id <= self.main.updater.initID:
				clas = 'oldtweet'
				
			else:
				clas = 'tweet'
			
			# Source
			by = ""
			source = tweet.source
			if source != "web":
				try:
					if tweet.source_url != "":
						source = '<a href="%s" title="%s">%s</a>' % (tweet.source_url, tweet.source_url, tweet.source)
			
				except:
					pass
			
				by = lang.htmlBy % source
			
			# Protected
			locked = ""
			if hasattr(tweet, "protected") and tweet.protected:
				locked = '<div class="protected"></div>'
			else:
				locked = '<div class="space">&nbsp;</div>'
			
			# HTML
			html = '''
					<div class="%s">
						<div class="avatar">
							%s
						</div>
						
						<div class="actions">
							<div class="doreply">
								<a href="reply:%s:%d:%d" title="''' + (lang.htmlReply % tweet.user.screen_name) + '''"> </a>
							</div>
							<div class="doretweet">
								<a href="retweet:%d" title="''' + (lang.htmlRetweet % tweet.user.screen_name) + '''"> </a>
							</div>
						</div>
						
						<div class="inner-text">
							<div>
								<a class="name" href="http://twitter.com/%s" title="''' + (lang.htmlProfile % lang.htmlProfile) + '''">
									<b>%s</b>
								</a> ''' + locked + ''' %s
							</div>
							<div class="time">
								<a href="http://twitter.com/%s/statuses/%d" title="''' + (self.absolute_time(tweet.created_at)) + '''">%s</a>
								''' + by + '''
							</div>
							<div class="reply">%s</div>
						</div>
					</div>'''	
			
			
			html = html % (
					clas, 
					avatar,
					
					# Actions
					tweet.user.screen_name, tweet.id, num, 
					num,		
					
					# Text
					tweet.user.screen_name, 
					profilename, 
					tweet.user.screen_name, 
					text, 	
					
					# Time
					tweet.user.screen_name, tweet.id, self.relative_time(tweet.created_at), 
					reply)
			
			if tweet.id == self.newestID:
				html = '</div>' + html
			
			renderTweets.insert(0, html)
			
		
		# Render Page
		if len(self.tweets) > 0:
			html = """
			<html>
				<head>
					<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
				</head>
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
				</body>
			</html>""" % (self.main.getResource("atarashii.css"), "".join(renderTweets), self.tweets[0][0].id, lang.htmlLoadMore)
		
		else:
			html = """
			<html>
				<head>
					<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
				</head>
				<body class="unloaded">
					<div class="loading"><b>%s</b></div>
				</body>
			</html>""" % (self.main.getResource("atarashii.css"), lang.htmlEmpty)
		
		self.load_string(html, "text/html", "UTF-8", "file:///main/")
	
	
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
			
		else:
			return lang.htmlDay % math.ceil(delta / (60.0 * 60.0 * 24.0))
				
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
		
		elif uri.startswith("reply:"):
			if not self.main.updater.error:
				foo, self.main.replyUser, self.main.replyID, num = uri.split(":")
				gobject.idle_add(lambda: self.main.reply(int(num)))
		
		elif uri.startswith("retweet:"):
			if not self.main.updater.error:
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
	
