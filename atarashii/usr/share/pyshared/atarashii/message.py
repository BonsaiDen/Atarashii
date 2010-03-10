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
		lastHighlight = False
		
		# Do the rendering!
		for num, obj in enumerate(self.items):
			item, img, mode = obj
			self.isNewTimeline(item)
			text = self.formatter.parse(item.text)
			
			
			# Spacers ----------------------------------------------------------
			highlight = item.recipient_screen_name != self.main.username
			if num > 0:
				nextHighlight = self.items[num+1][0].recipient_screen_name != \
					self.main.username if num < len(self.items) - 1 else False
				
				renderitems.insert(0, self.insertSpacer(item, lastname, 
						item.sender, highlight, lastHighlight, False, True, 
						nextHighlight))
			
			lastname = item.sender.screen_name
			lastHighlight = highlight
			
			
			# Avatar -----------------------------------------------------------
			self.isNewAvatar(num)
			if (num < len(self.items) - 1 and \
				(item.sender.screen_name != \
				self.items[num + 1][0].sender.screen_name or \
				item.recipient_screen_name != \
				self.items[num + 1][0].recipient_screen_name or self.newAvatar \
				)) or num == len(self.items) - 1 or self.newTimeline:
				
				avatar = '''<a href="http://twitter.com/%s">
							<img width="32" src="file://%s" title="''' + \
							lang.htmlInfo + '''"/></a>'''
				
				avatar = avatar % (item.sender.screen_name, img, 
									item.sender.name, 
									item.sender.followers_count, 
									item.sender.friends_count, 
									item.sender.statuses_count)
			
			else:
				avatar = ""
			
			
			# Background -------------------------------------------------------
			cls = 'oldtweet' if item.id <= self.initID else 'tweet'
			if item.recipient_screen_name != self.main.username:
				mode = lang.messageTo
				name = item.recipient_screen_name
				reply = "display: none;"
			
			else:
				mode = lang.messageFrom
				name = item.sender.screen_name
				reply = ""
				cls = "highlightold" if item.id <= self.initID else "highlight"
			
			
			# HTML Snippet -----------------------------------------------------
			html = '''
			<div class="%s">
			<div class="avatar">
				%s
			</div>
			
			<div class="actions">
				<div class="doretweet" style="''' + reply + \
				'''"><a href="message:%s:%d:%d" title="''' + \
					(lang.htmlReply % item.sender.screen_name) + '''"></a>
				</div>
			</div>
			
			<div class="inner-text">
				<div>
					<span class="name"><b>''' + mode + \
					''' <a href="http://twitter.com/%s" title="''' + \
					lang.htmlProfile + \
					'''">%s</a></b></span> %s
				</div>
				<div class="time">
					<a href="http://twitter.com/%s/statuses/%d" title="''' + \
					(self.absolute_time(item.created_at)) + '''">%s</a>
				</div>
			</div>
			</div>'''
			
			# Insert values
			html = html % (
					cls, 
					avatar,
					
					# Actions
					item.sender.screen_name, item.sender.id, num, 	
					
					# Text
					item.sender.screen_name, 
					item.sender.name.strip(), 
					name, 
					text, 	
					
					# Time
					item.sender.screen_name,
					item.id,
					self.relative_time(item.created_at))
			
			# Close Newest Container
			if item.id == self.newestID:
				html = '</div>' + html
			
			renderitems.insert(0, html)
		
		# Render
		self.setHTML(renderitems)
	
