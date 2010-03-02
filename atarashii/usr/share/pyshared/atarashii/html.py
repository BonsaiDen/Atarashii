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
		view.HTMLView.__init__(self, main, gui, self.gui.htmlScroll)


	# Screens ------------------------------------------------------------------
	# --------------------------------------------------------------------------
	def start(self):
		self.mode = "start"
		self.isRendering = True
		self.offsetCount = 0
		self.gui.htmlTab.set_markup(lang.tabsTweetsLoading)
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
		self.gui.htmlTab.set_markup(lang.tabsTweetsLoading)
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
	
	

	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
	def render(self):	
		self.position = self.scroll.get_vscrollbar().get_value()
		self.isRendering = True
		self.mode = "render"
		self.tweets.sort(self.compare)
		
		# Set the latest tweet for reloading on startup
		if len(self.tweets) > 0:
			id = len(self.tweets) - self.main.loadTweetCount
			if id < 0:
				id = 0
			
			self.main.settings['firsttweet_' + self.main.username] = str(self.tweets[id][0].id - 1)
		
		# Render
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
		count = 0
		for num, obj in enumerate(self.tweets):
			tweet, img, mode = obj
			
			# Fix some stuff for the seperation of continous new/old tweets
			newTimeline = tweet.id > self.main.updater.initID
			if newTimeline:
				count += 1
				
			if newest or self.main.updater.initID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML
			text = self.formatter.parse(tweet.text)
			self.atUser = self.main.username.lower() in [i.lower() for i in self.formatter.users]
			highlight = hasattr(tweet, "is_mentioned") and tweet.is_mentioned or self.atUser
			
			# Spacer
			if num > 0:
				if lastname != tweet.user.screen_name or newTimeline:
					if tweet.id > self.main.updater.initID:
						renderTweets.insert(0, '<div class="spacer1"></div>')
					else:
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
				
			elif tweet.id <= self.main.updater.initID:
				if self.atUser:
					clas = 'highlight'
				else:
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
								<a class="name" href="http://twitter.com/%s" title="''' + lang.htmlProfile + '''">
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
		if count > 0:
			self.gui.htmlTab.set_markup(lang.tabsTweetsNew % count)
		else:
			self.gui.htmlTab.set_markup(lang.tabsTweets)
		
		if len(self.tweets) > 0:
			html = """
			<html>
				<head>
					<meta content="text/html; charset=UTF-8" http-equiv="content-type"/>
					<link rel="stylesheet" type="text/css" media="screen" href="file://%s" />
				</head>
				<body>
					<div><div id="newcontainer">%s</div>
					<div class="loadmore"><a href="more:%d" title="%s"><b>%s</b></a></div>
				</body>
			</html>""" % (self.main.getResource("atarashii.css"), "".join(renderTweets), self.tweets[0][0].id, lang.htmlHistory, lang.htmlLoadMore)
		
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

	
