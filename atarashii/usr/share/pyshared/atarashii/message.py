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
		self.getLatest = self.main.getLatestMessageID
		self.itemCount = self.main.loadMessageCount
		
		self.getItemCount = self.main.getMessageCount
		self.setItemCount = self.main.setMessageCount
		
		self.langLoading = lang.messageLoading
		self.langEmpty = lang.messageEmpty
		self.langLoad = lang.messageLoadMore
		
		self.firstSetting = 'firstmessage_'
	
	
	# Render the Timeline ------------------------------------------------------
	# --------------------------------------------------------------------------
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
			tweet, img, mode = obj
			
			# Fix some stuff for the seperation of continous new/old items
			newTimeline = tweet.id > self.initID
			if newTimeline:
				self.count += 1
			
			if newest or self.initID == 0:
				newTimeline = False
			
			if newTimeline:
				newest = True
			
			# Create Tweet HTML
			text = self.formatter.parse(tweet.text)
			
			# Spacer
			if num > 0:
				if lastname != tweet.sender.screen_name or newTimeline:
					if tweet.id > self.initID:
						renderitems.insert(0, '<div class="spacer1"></div>')
					else:
						renderitems.insert(0, '<div class="spacer"></div>')
				
				elif tweet.id > self.initID:
					renderitems.insert(0, '<div class="spacer4"></div>')
				
				else:
					renderitems.insert(0, '<div class="spacer2"></div>')
			
			lastname = tweet.sender.screen_name
			
			# Realname
			profilename = tweet.sender.name.strip()
			if not tweet.sender.name.endswith('s') and not tweet.sender.name.endswith('x'):
				profilename += "'s"
				
			else:
				profilename += "'"
			
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
			
			if (num < len(self.items) - 1 and (tweet.sender.screen_name != self.items[num + 1][0].sender.screen_name or newAvatar)) or num == len(self.items) - 1 or newTimeline:
				avatar = ('<a href="http://twitter.com/%s"><img width="32" src="file://%s" title="' + lang.htmlInfo + '"/></a>') 
				avatar = avatar % (tweet.sender.screen_name, img, tweet.sender.name, tweet.sender.followers_count, tweet.sender.friends_count, tweet.sender.statuses_count)
			
			else:
				avatar = ""
			
			# At?
			if tweet.id <= self.initID:
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
			
			self.main.gui.setTitle()
			renderitems.insert(0, html)
			
		# Render
		self.setHTML(renderitems)
	
