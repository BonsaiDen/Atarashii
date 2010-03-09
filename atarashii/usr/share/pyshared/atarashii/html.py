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
		self.getLatest = self.main.getLatestID
		self.itemCount = self.main.loadTweetCount
		
		self.getItemCount = self.main.getTweetCount
		self.setItemCount = self.main.setTweetCount
		
		self.langLoading = lang.htmlLoading
		self.langEmpty = lang.htmlEmpty
		self.langLoad = lang.htmlLoadMore
		
		self.firstSetting = 'firsttweet_'
		

	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
	def getUser(self, num):
		item = self.items[num][0]
		if hasattr(item, "retweeted_status"):
			return item.retweeted_status.user
		else:
			return item.user
	
	def getText(self, num):
		item = self.items[num][0]
		if hasattr(item, "retweeted_status"):
			return item.retweeted_status.text
		
		else:
			return item.text
	
	
	def render(self):	
		self.initRender()
		
		# Render
		renderitems = []
		lastname = ""
				
		# Newest Stuff
		newest = False
		newestAvatar = False
		container = False
		lastHighlight = False

		# Do the rendering!
		self.count = 0
		for num, obj in enumerate(self.items):
			item, img, mode = obj
			
			# Check for new style retweet
			retweeted = False
			retweet = ""
			if hasattr(item, "retweeted_status"):
				tweet = item.retweeted_status
				retweeted = True
				
				# Retweet Info
				retweet = '<a href="http://twitter.com/%s" title="''' + \
						(self.relative_time(item.created_at)) + '">' + lang.htmlInRetweet + '</a>'
				retweet = retweet % (item.user.screen_name, 
										item.user.screen_name)
			
			else:
				tweet = item
			
			user = tweet.user
			
			# Fix some stuff for the seperation of continous new/old items
			newTimeline = item.id > self.initID
			if newTimeline:
				self.count += 1
			
			if newest or self.initID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML
			text = self.formatter.parse(tweet.text)
			self.atUser = self.main.username.lower() in \
							[i.lower() for i in self.formatter.users]
			
			highlight = hasattr(tweet, "is_mentioned") and \
						tweet.is_mentioned or self.atUser
			
			# Spacer
			if num > 0:
				spacer = ""
				if lastname != user.screen_name or newTimeline:
					if lastHighlight != highlight:
						spacer = "1" if item.id > self.initID else ""
					
					elif item.id > self.initID:
						spacer = "1"
				
				elif highlight != lastHighlight:
					spacer = "1" if item.id > self.initID else ""
					
				elif hasattr(tweet, "is_mentioned") and tweet.is_mentioned:
					spacer = "5"
				
				elif item.id > self.initID:
					spacer = "6" if highlight else "4"
				
				elif highlight:
					spacer = "7"
				
				elif lastHighlight:
					spacer = "1"
				
				else:
					spacer = "2"
				
				renderitems.insert(0, '<div class="spacer%s"></div>' % spacer)
					
			
			lastname = user.screen_name
			lastHighlight = highlight
			
			# Is this tweet a reply?
			reply = ""
			if tweet.in_reply_to_screen_name and tweet.in_reply_to_status_id:
				reply = '<a href="http://twitter.com/%s/statuses/%d">' + \
						lang.htmlInReply + '</a>'
				reply = reply % (tweet.in_reply_to_screen_name, 
								tweet.in_reply_to_status_id,
								tweet.in_reply_to_screen_name)
			
			
			# Display Avatar?
			if num < len(self.items) - 1:
				newAvatar = self.items[num + 1][0].id > self.initID
			else:
				newAvatar = False
				
			if num > 0 and self.items[num - 1][0].id <= self.initID:
				newTimeline = False
			
			if newestAvatar or self.initID == 0:
				newAvatar = False
			
			if newAvatar:
				newestAvatar = True
			
			if (num < len(self.items) - 1 and \
				(user.screen_name != \
				self.getUser(num+1).screen_name or newAvatar)) or \
				num == len(self.items) - 1 or newTimeline:
			
				avatar = '''<a href="http://twitter.com/%s">
							<img width="32" src="file://%s" title="''' + \
							lang.htmlInfo + '''"/></a>'''
				
				avatar = avatar % (user.screen_name, img, 
									user.name, user.followers_count,
									user.friends_count,
									user.statuses_count)
			
			else:
				avatar = ""
			
			# At?
			if hasattr(tweet, "is_mentioned") and tweet.is_mentioned:
				clas = 'mentioned'
				
			elif item.id <= self.initID:
				clas = 'highlightold' if self.atUser else 'oldtweet'
			
			else:
				clas = 'highlight' if self.atUser else 'tweet'
			
			# Source
			by = ""
			source = tweet.source
			if source != "web":
				try:
					if tweet.source_url != "":
						source = '<a href="%s" title="%s">%s</a>' % \
							(tweet.source_url, tweet.source_url, tweet.source)
			
				except:
					pass
			
				by = lang.htmlBy % source
			
			# Protected
			locked = ''
			if hasattr(user, "protected") and user.protected:
				locked = ('<span class="protected" title="' + \
					lang.htmlProtected + '"></span>') % user.screen_name
			
			# HTML Snippet
			html = '''
			<div class="%s">
			<div class="avatar">
				%s
			</div>
			
			<div class="actions">
				<div class="doreply">
					<a href="reply:%s:%d:%d" title="''' + \
					(lang.htmlReply % user.screen_name) + '''"> </a>
				</div>
				<div class="doretweet">
					<a href="retweet:%d:%d" title="''' + \
					(lang.htmlRetweet % user.screen_name) + '''"> </a>
				</div>
			</div>
			
			<div class="inner-text">
				<div><span class="name">''' + ("<b>RT</b>" if retweeted else "") + '''
					<a href="http://twitter.com/%s" title="''' + \
					lang.htmlProfile + '''">
						<b>%s</b>
					</a></span> ''' + locked + ''' %s
				</div>
				<div class="time">
					<a href="http://twitter.com/%s/statuses/%d" title="''' + \
					(self.absolute_time(tweet.created_at)) + '''">%s</a>
					''' + by + '''
				</div>
				<div class="reply">%s</div>
				<div class="reply">%s</div>
			</div>
			<div class="clearfloat"></div>
			</div>'''	
			
			# Insert values
			html = html % (
					clas, 
					avatar,
					
					# Actions
					user.screen_name, tweet.id, num, 
					num, tweet.id,		
					
					# Text
					user.screen_name, 
					user.name.strip(), 
					user.screen_name, 
					text, 	
					
					# Time
					user.screen_name,
					tweet.id,
					self.relative_time(tweet.created_at),
					reply, retweet)
			
			if item.id == self.newestID:
				html = '</div>' + html
			
			self.main.gui.setTitle()
			renderitems.insert(0, html)
		
		# Render
		self.setHTML(renderitems)

