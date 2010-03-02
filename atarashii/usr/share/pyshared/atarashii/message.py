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


# HTML View --------------------------------------------------------------------
# ------------------------------------------------------------------------------
import pygtk
pygtk.require('2.0')
import gtk
import gobject

import view

from lang import lang

class HTML(view.HTMLView):
	def __init__(self, main, gui):
		self.main = main
		self.gui = gui
		view.HTMLView.__init__(self, main, gui, self.gui.messageScroll)


	# Screens ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		self.mode = "start"
		self.isRendering = True
		self.offsetCount = 0
		self.gui.messageTab.set_markup(lang.tabsMessageLoading)
		self.load_string("""
		<html>
			<head>
				<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
				<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
			</head>
			<body class="unloaded">
				<div class="loading"><b>%s</b></div>
			</body>
		</html>""" % (self.main.getResource("atarashii.css"), lang.messageLoading), "text/html", "UTF-8", "file:///main/")
	
	def splash(self):
		self.mode = "splash"
		self.isRendering = True
		self.offsetCount = 0
		self.gui.messageTab.set_markup(lang.tabsMessageLoading)
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
	
	
	# Clear the History
	def clear(self):
		self.historyLoaded = False
		self.tweets = self.tweets[self.historyCount:]
		self.main.maxMessageCount -= self.historyCount
		self.historyCount = 0
		self.gui.historyButton.set_sensitive(False)
		self.render()
	
	def read(self):
		if self.main.updater.initMessageID != self.main.getLatestMessageID():
			self.gui.messageTab.set_markup(lang.tabsMessage)
			self.gui.readButton.set_sensitive(False)
			self.main.updater.initMessageID = self.main.getLatestMessageID()
			if not self.historyLoaded:
				pos = len(self.tweets) - self.main.loadMessageCount
				if pos < 0:
					pos = 0
				
				self.tweets = self.tweets[pos:]
			
			self.render()
	
	
	
	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
	def render(self):	
		self.position = self.scroll.get_vscrollbar().get_value()
		self.isRendering = True
		self.mode = "render"
		self.tweets.sort(self.compare)
		
		# Set the latest tweet for reloading on startup
		if len(self.tweets) > 0:
			id = len(self.tweets) - self.main.loadMessageCount
			if id < 0:
				id = 0
			
			self.main.settings['firstmessage_' + self.main.username] = str(self.tweets[id][0].id - 1)
		
		# Render
		renderTweets = []
		lastname = ""
				
		# Newest Stuff
		if self.newestID == -1:
			self.newestID = self.main.updater.initMessageID
		
		newest = False
		newestAvatar = False
		container = False
		lastHighlight = False
		
		# Do the rendering!
		count = 0
		for num, obj in enumerate(self.tweets):
			tweet, img, mode = obj
			
			# Fix some stuff for the seperation of continous new/old tweets
			newTimeline = tweet.id > self.main.updater.initMessageID
			if newTimeline:
				count += 1
			
			if newest or self.main.updater.initMessageID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML
			text = self.formatter.parse(tweet.text)
			
			# Spacer
			if num > 0:
				if lastname != tweet.sender.screen_name or newTimeline:
					if tweet.id > self.main.updater.initMessageID:
						renderTweets.insert(0, '<div class="spacer1"></div>')
					else:
						renderTweets.insert(0, '<div class="spacer"></div>')
				
				elif tweet.id > self.main.updater.initMessageID:
					renderTweets.insert(0, '<div class="spacer4"></div>')
				
				else:
					renderTweets.insert(0, '<div class="spacer2"></div>')
			
			lastname = tweet.sender.screen_name
			
			# Realname
			profilename = tweet.sender.name.strip()
			if not tweet.sender.name.endswith('s') and not tweet.sender.name.endswith('x'):
				profilename += "'s"
				
			else:
				profilename += "'"
			
			# Display Avatar?
			if num < len(self.tweets) - 1:
				newAvatar = self.tweets[num + 1][0].id > self.main.updater.initMessageID
			else:
				newAvatar = False
				
			if num > 0 and self.tweets[num - 1][0].id <= self.main.updater.initMessageID:
				newTimeline = False
			
			if newestAvatar or self.main.updater.initMessageID == 0:
				newAvatar = False
			
			if newAvatar:
				newestAvatar = True
			
			if (num < len(self.tweets) - 1 and (tweet.sender.screen_name != self.tweets[num + 1][0].sender.screen_name or newAvatar)) or num == len(self.tweets) - 1 or newTimeline:
				avatar = ('<a href="http://twitter.com/%s"><img width="32" src="file://%s" title="' + lang.htmlInfo + '"/></a>') 
				avatar = avatar % (tweet.sender.screen_name, img, tweet.sender.name, tweet.sender.followers_count, tweet.sender.friends_count, tweet.sender.statuses_count)
			
			else:
				avatar = ""
			
			# At?
			if tweet.id <= self.main.updater.initMessageID:
				clas = 'oldtweet'
				
			else:
				clas = 'tweet'
			
			# HTML
			if tweet.recipient_screen_name != self.main.username:
				mode = "An"
				name = tweet.recipient_screen_name
				reply = "display: none;"
			
			else:
				mode = "Von"
				name = tweet.sender.screen_name
				reply = ""
			
			html = '''
					<div class="%s">
						<div class="avatar">
							%s
						</div>
						
						<div class="actions">
							<div class="doretweet" style="''' + reply + '''">
								<a href="message:%s:%d:%d" title="''' + (lang.htmlReply % tweet.sender.screen_name) + '''"> </a>
							</div>
						</div>
						
						<div class="inner-text">
							<div>
								<span class="name"><b>''' + mode + ''' <a href="http://twitter.com/%s" title="''' + lang.htmlProfile + '''">%s</a></b></span> <div class="space">&nbsp;</div> %s
							</div>
							<div class="time">
								<a href="http://twitter.com/%s/statuses/%d" title="''' + (self.absolute_time(tweet.created_at)) + '''">%s</a>
							</div>
						</div>
					</div>'''
			
			
			html = html % (
					clas, 
					avatar,
					
					# Actions
					tweet.sender.screen_name, tweet.sender.id, num, 	
					
					# Text
					tweet.sender.screen_name, 
					profilename, 
					name, 
					text, 	
					
					# Time
					tweet.sender.screen_name, tweet.id, self.relative_time(tweet.created_at))
			
			if tweet.id == self.newestID:
				html = '</div>' + html
			
			renderTweets.insert(0, html)
			
		
		# Render Page
		if count > 0:
			self.gui.messageTab.set_markup(lang.tabsMessageNew % count)
		else:
			self.gui.messageTab.set_markup(lang.tabsMessage)
		
		if len(self.tweets) > 0:
			html = """
			<html>
				<head>
					<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
				</head>
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="moremessages:%d" title="%s"><b>%s</b></a></div>
				</body>
			</html>""" % (self.main.getResource("atarashii.css"), "".join(renderTweets), self.tweets[0][0].id, lang.htmlHistoryMessage, lang.htmlLoadMore)
		
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

	
