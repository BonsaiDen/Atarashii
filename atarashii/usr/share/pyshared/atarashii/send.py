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


# Sender Thread ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading
import sys

# Import local Tweepy
try:
	sys.path.insert(0, __file__[:__file__.rfind('/')])
	from tweepy.error import TweepError
	
finally:
	sys.path.pop(0)

from constants import *


# Send Tweets/Messages ---------------------------------------------------------
# ------------------------------------------------------------------------------
class Send(threading.Thread):
	def __init__(self, main, mode, text):
		threading.Thread.__init__(self)
		self.gui = main.gui
		self.main = main
		self.mode = mode
		self.text = text
	
	
	# Do a send ----------------------------------------------------------------
	def run(self):
		self.main.wasSending = True
		try:
			if self.mode == MODE_TWEETS:
				self.sendTweet(self.text)
		
			elif self.mode == MODE_MESSAGES:
				self.sendMessage(self.text)
		
			else: # TODO implement search
				pass
			
			# Reset GUI
			gobject.idle_add(self.resetGUI)
		
		# Show Error Message
		except TweepError, error:
			gobject.idle_add(lambda: self.gui.showError(error))
	
		
		self.main.isSending = False
	
	
	# Reset GUI ----------------------------------------------------------------
	def resetGUI(self):
		# Reply
		self.main.replyUser = UNSET_TEXT
		self.main.replyText = UNSET_TEXT
		self.main.replyID = UNSET_ID_NUM
		
		# Retweets
		self.main.retweetUser = UNSET_TEXT	
		self.main.retweetText = UNSET_TEXT
		
		# Message
		self.main.messageUser = UNSET_TEXT
		self.main.messageID = UNSET_ID_NUM
		self.main.messageText = UNSET_TEXT
		
		# Reset Input
		self.gui.text.setText(UNSET_TEXT)
		self.gui.showInput(False)
		if self.gui.mode == MODE_MESSAGES:
			self.gui.message.grab_focus()
		
		elif self.gui.mode == MODE_TWEETS:
			self.gui.html.grab_focus()	
		
		else: # TODO implement search
			pass
		
		self.main.wasSending = False
	
		
	# Send a Tweet -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def sendTweet(self, text):
		if self.main.replyID != UNSET_ID_NUM:
			# Send Tweet
			update = self.main.api.update_status(text, 
								in_reply_to_status_id = self.main.replyID)
			self.main.updater.setLastTweet(update.id)
			
			# Insert temporary tweet
			imgfile = self.main.updater.getImage(update)
			self.gui.html.updateList.append((update, imgfile))
			gobject.idle_add(lambda: self.gui.html.pushUpdates())
		
		# Normal Tweet / Retweet
		else:
			# Send Tweet
			update = self.main.api.update_status(text)
			self.main.updater.setLastTweet(update.id)
			
			# Insert temporary tweet
			imgfile = self.main.updater.getImage(update)
			self.gui.html.updateList.append((update, imgfile))
			gobject.idle_add(lambda: self.gui.html.pushUpdates())
	
	
	# Send a Direct Message ----------------------------------------------------
	# --------------------------------------------------------------------------
	def sendMessage(self, text):
		# Send Message
		if self.main.messageID != UNSET_ID_NUM:
			message = self.main.api.send_direct_message(text = text, 
										user_id = self.main.messageID)
		else:
			message = self.main.api.send_direct_message(text = text, 
										screen_name = self.main.messageUser)
		
		self.main.updater.setLastMessage(message.id)
		
		# Insert temporary message
		imgfile = self.main.updater.getImage(message, True)
		self.gui.message.updateList.append((message, imgfile))
		gobject.idle_add(lambda: self.gui.message.pushUpdates())


# New style Retweets -----------------------------------------------------------
# ------------------------------------------------------------------------------
class Retweet(threading.Thread):
	def __init__(self, main, name, tweetid):
		threading.Thread.__init__(self)
		self.gui = main.gui
		self.main = main
		self.name = name
		self.tweetid = tweetid
	
	def run(self):
		self.main.wasSending = True
		self.main.wasRetweeting = True
		try:
			# Retweet
			self.main.api.retweet(self.tweetid)

			# Focus HTML
			self.gui.showInput(False)
			if self.gui.mode == MODE_MESSAGES:
				self.gui.message.grab_focus()
		
			elif self.gui.mode == MODE_TWEETS:
				self.gui.html.grab_focus()	
			
			else: # TODO implement search
				pass
			
			self.main.wasSending = False
			gobject.idle_add(lambda: self.gui.showRetweetInfo(self.name))
		
		except TweepError, error:
			gobject.idle_add(lambda: self.gui.showError(error))	
		
		self.main.isSending = False
	
