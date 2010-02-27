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

from lang import lang

try:
	import gnome as web
	
except:
	try:
		import webbrowser as web
		
	except:
		web = None


class HTML():
	def __init__(self, atarashii):
		self.atarashii = atarashii
		self.scroll = gtk.ScrolledWindow()
		self.scroll.set_property("hscrollbar-policy",gtk.POLICY_AUTOMATIC)
		self.scroll.set_shadow_type(gtk.SHADOW_IN)
		self.view = None
		self.init(True)
		
	def createView(self):
		self.view = webkit.WebView()
		self.view.connect("button-press-event", self.open_context)
		self.view.connect("navigation-requested", self.open_link)
		self.view.connect("load-finished", self.loaded)
		self.view.connect("focus-in-event", self.atarashii.htmlfocus)
		self.view.set_maintains_back_forward_list(False)
		self.scroll.add(self.view)
		self.view.show()
	
	# Initiate a empty timeline
	def init(self, splash = False):
		self.tweets = []
		self.list = []
		self.position = 0
		self.offsetCount = 0
		self.historyLoaded = False
		self.historyPosition = -1
		self.historyCount = 0
		self.firstLoad = True
		self.newestID = -1
		self.newTweets = False
		self.loadOld = False
		self.createView()	
		if splash:
			self.splash()
	
	# Fix scrolling isses on page load
	def loaded(self, *args):
		if len(self.tweets) > 0 and self.newTweets and not self.loadOld:
			try:
				self.view.execute_script('document.title=document.getElementById("newcontainer").offsetHeight;')
				offset = int(self.view.get_main_frame().get_title())
			
			except:
				offset = 0
		
		else:
			offset = 0
		
		if not self.firstLoad and self.position > 0:
			self.scroll.get_vscrollbar().set_value(self.position + offset)
		
		if len(self.tweets) > 0:
			self.firstLoad = False
		
		self.loadOld = False
		self.newTweets = False
	
	# Display "loading" info
	def start(self):
		self.offsetCount = 0
		self.view.load_string("""
		<html>
			<head>
				<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
				<link rel="stylesheet" type="text/css" media="screen" href="file://%s/atarashii.css" />
			</head>
			<body class="unloaded">
				<div class="loading"><b>%s</b></div>
			</body>
		</html>""" % (self.atarashii.resources, lang.htmlLoading), "text/html", "UTF-8", "file:///atarashii/")
	
	# Display the splash screen
	def splash(self):
		self.offsetCount = 0
		self.view.load_string("""
		<html>
			<head>
				<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
				<link rel="stylesheet" type="text/css" media="screen" href="file://%s/atarashii.css" />
			</head>
			<body class="unloaded">
				<div class="loading"><img src="file://%s" /><br/><b>%s</b></div>
			</body>
		</html>""" % (self.atarashii.resources, self.atarashii.img, lang.htmlWelcome), "text/html", "UTF-8", "file:///atarashii/")
	
	# Clear the History
	def clear(self):
		self.historyLoaded = False
		self.tweets = self.tweets[self.historyCount:]
		self.atarashii.maxTweets -= self.historyCount
		self.historyCount = 0
		self.atarashii.clearButton.set_sensitive(False)
		self.render()
	
	# Push Tweets to the View
	def push(self):
		while len(self.list) > 0:
			self.add(self.list.pop(0))
	
		self.render()

	# Add Tweets to the internal List
	def add(self, tweet):
		id = tweet[0].id
		found = False
		for i in self.tweets:
			if i[0].id == id:
				found = True
				break
		
		if not found:
			if tweet[2]:
				self.tweets.insert(0, tweet)

			else:
				self.tweets.append(tweet)
			
			self.newTweets = True
			if len(self.tweets) > self.atarashii.maxTweets:
				self.tweets.pop(0)
	
	def compare(self, x, y):
		if x[0].id > y[0].id:
			return 1
	
		elif x[0].id < y[0].id:
			return -1
		
		else:
			return 0

	# Render the Timeline
	def render(self):	
		# Sort Tweets
		self.tweets.sort(self.compare)
		
		# Set the latest tweet for reloading on startup
		if len(self.tweets) > 0:
			id = len(self.tweets) - self.atarashii.loadTweets
			if id < 0:
				id = 0
			
			self.atarashii.settings['firsttweet_' + self.atarashii.username] = str(self.tweets[id][0].id - 1)
		
		# Regex
		urlRegex = re.compile("((mailto\:|(news|(ht|f)tp(s?))\://){1}\S+)")
		atRegex = re.compile("@((){1}\S+)")
		tagRegex = re.compile("\#((){1}[^\?\s+-]+)") #re.compile("\#((){1}\S+)")
		
		# Render
		self.position = self.scroll.get_vscrollbar().get_value()
		renderTweets = []
		lastname = ""
				
		# Newest Stuff
		if self.newestID == -1:
			self.newestID = self.atarashii.updater.initID
		
		newest = False
		newestAvatar = False
		container = False
		lastHighlight = False
		for num, obj in enumerate(self.tweets):
			tweet, img, mode = obj
			
			# Fix some stuff for the seperation of continous new/old tweets
			newTimeline = tweet.id > self.atarashii.updater.initID
			if newest or self.atarashii.updater.initID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML			
			text = urlRegex.sub(self.urllink, " " + tweet.text + " ")
			self.atUser = False
			text = atRegex.sub(self.atlink, text)		
			text = tagRegex.sub(self.hashlink, text)
			text = text.strip()
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
					
				elif tweet.id > self.atarashii.updater.initID:
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
				newAvatar = self.tweets[num + 1][0].id > self.atarashii.updater.initID
			else:
				newAvatar = False
				
			if num > 0 and self.tweets[num - 1][0].id <= self.atarashii.updater.initID:
				newTimeline = False
			
			if newestAvatar or self.atarashii.updater.initID == 0:
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
				
			elif tweet.id <= self.atarashii.updater.initID:
				clas = 'oldtweet'
				
			else:
				clas = 'tweet'
			
			# HTML
			by = ""
			source = tweet.source
			if source != "web":
				try:
					if tweet.source_url != "":
						source = '<a href="%s" title="%s">%s</a>' % (tweet.source_url, tweet.source_url, tweet.source)
			
				except:
					pass
			
				by = lang.htmlBy % source
					
			html = '''
					<div class="%s">
						<div class="avatar">
							%s
						</div>
						
						<div class="actions">
							<div class="doreply">
								<a href="reply:%s:%d:%d" title="''' + (lang.htmlReply % tweet.user.screen_name) + '''"><b>@</b></a>
							</div>
							<div class="doretweet">
								<a href="retweet:%d" title="''' + (lang.htmlRetweet % tweet.user.screen_name) + '''">RT</a>
							</div>
						</div>
						
						<div class="inner-text">
							<div>
								<a class="name" href="http://twitter.com/%s" title="''' + (lang.htmlProfile % lang.htmlProfile) + '''">
									<b>%s</b>
								</a> %s
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
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s/atarashii.css" />
				</head>
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="more:%d"><b>%s</b></a></div>
				</body>
			</html>""" % (self.atarashii.resources, "".join(renderTweets), self.tweets[0][0].id, lang.htmlLoadMore)
		
		else:
			html = """
			<html>
				<head>
					<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s/atarashii.css" />
				</head>
				<body class="unloaded">
					<div class="loading"><b>%s</b></div>
				</body>
			</html>""" % (self.atarashii.resources, lang.htmlEmpty)
		
		#f = open("debug.html", "wb")
		#f.write(html)
		#f.close()
		self.view.load_string(html, "text/html", "UTF-8", "file:///atarashii/")
	
	# Create the relative time description
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
	def open_link(self, view, frame, req):
		uri = req.get_uri()
		if uri.startswith("file:///"):
			return False
		
		if uri.startswith("more:"):
			self.atarashii.updater.loadOlder = int(uri.split(":")[1]) - 1
			if self.atarashii.updater.loadOlder != -1:
				self.atarashii.scroll.hide()
				self.atarashii.progress.set_fraction(0.0)
				self.atarashii.progress.show()
				self.atarashii.setStatus(lang.statusLoadOlder)
				gobject.timeout_add(100, lambda: self.atarashii.showProgess())
		
		elif uri.startswith("reply:"):
			if not self.atarashii.updater.error:
				foo, self.atarashii.reply_user, self.atarashii.reply_id, num = uri.split(":")
				gobject.idle_add(lambda: self.atarashii.reply(int(num)))
		
		elif uri.startswith("retweet:"):
			if not self.atarashii.updater.error:
				self.atarashii.retweet_num = int(uri.split(":")[1])
				gobject.idle_add(lambda: self.atarashii.retweet())
		
		else:
			if web != None:
				try:
					web.url_show(uri)
					
				except:
					web.open(url)
		
		return True
	
	# Block the Context Menu
	def open_context(self, html, e):
		if e.button == 3:
			return True
		
		return False
	
	# Regex stuff
	def escape(self, text):
		ent = {"&": "&amp;", '"': "&quot;", "'": "&apos;", ">": "&gt;", "<": "&lt;"}
		return "".join(ent.get(c,c) for c in text)
	
	def hashlink(self, match):
		tag = unicode(match.group().strip())
		tag = tag[tag.find('#')+1:]
		return (' <a href="http://search.twitter.com/search?%s" title="' + lang.htmlSearch + '">#%s</a>') % (urllib.urlencode({'q': '#' + tag}), tag, tag)
	
	def urllink(self, match):
		url = match.group()
		if len(url) > 30:
			text = url[0:27] + "..."
		else:
			text = url
		
		return '<a href="%s" title="%s">%s</a>' % (self.escape(url), self.escape(url), text)
	
	def atlink(self, match):
		at = match.group()[1:]
		if at == self.atarashii.username:
			self.atUser = True
	
		return '<a href="http://twitter.com/%s">@%s</a>' % (at, at)

		
		
