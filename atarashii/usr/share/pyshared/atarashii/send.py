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

from constants import *


# Send Tweets/Messages ---------------------------------------------------------
# ------------------------------------------------------------------------------
class Send(threading.Thread):
	def __init__(self, main, mode, text):
		threading.Thread.__init__(self)
		self.main = main
		self.mode = mode
		self.text = text

	def run(self):
		self.main.wasSending = True
		if self.mode == MODE_TWEETS:
			self.sendTweet(self.text)
		
		elif self.mode == MODE_MESSAGES:
			self.sendMessage(self.text)
		
		self.main.isSending = False


	# Send a Tweet -------------------------------------------------------------
	# --------------------------------------------------------------------------
	def sendTweet(self, text):
		if self.main.replyID != UNSET_ID_NUM:
			try:
				# Send Tweet
				update = self.main.api.update_status(text, 
									in_reply_to_status_id = self.main.replyID)
				self.main.updater.setLastTweet(update.id)
				self.main.gui.readButton.set_sensitive(True)
				
				# Insert temporary tweet
				imgfile = self.main.updater.getImage(update)
				self.main.gui.html.updateList.append((update, imgfile))
				gobject.idle_add(lambda: self.main.gui.html.pushUpdates())
				
				# Reset
				self.main.replyUser = UNSET_TEXT
				self.main.replyText = UNSET_TEXT
				self.main.replyID = UNSET_ID_NUM
				self.main.gui.text.setText(UNSET_TEXT)
				
				# Focus HTML
				self.main.gui.showInput(False)
				self.main.gui.html.grab_focus()
				self.main.wasSending = False
			
			except Exception, error:
				print error
				gobject.idle_add(lambda: self.main.gui.showError(error))
		
		# Normal Tweet / Retweet
		else:
			try:
				# Send Tweet
				update = self.main.api.update_status(text)
				self.main.updater.setLastTweet(update.id)
				self.main.gui.readButton.set_sensitive(True)
				
				# Insert temporary tweet
				imgfile = self.main.updater.getImage(update)
				self.main.gui.html.updateList.append((update, imgfile))
				gobject.idle_add(lambda: self.main.gui.html.pushUpdates())

				# Reset
				self.main.replyUser = UNSET_TEXT
				self.main.replyText = UNSET_TEXT
				self.main.replyID = UNSET_ID_NUM
				self.main.retweetUser = UNSET_TEXT	
				self.main.retweetText = UNSET_TEXT
				self.main.gui.text.setText(UNSET_TEXT)
				
				# Focus HTML
				self.main.gui.showInput(False)
				self.main.gui.html.grab_focus()
				self.main.wasSending = False
			
			except Exception, error:
	 			print error
				gobject.idle_add(lambda: self.main.gui.showError(error))				
	
	
	# Send a Direct Message ----------------------------------------------------
	# --------------------------------------------------------------------------
	def sendMessage(self, text):
		try:
			# Send Message
			if self.main.messageID != UNSET_ID_NUM:
				message = self.main.api.send_direct_message(text = text, 
											user_id = self.main.messageID)
			else:
				message = self.main.api.send_direct_message(text = text, 
											screen_name = self.main.messageUser)
			
			self.main.updater.setLastMessage(message.id)
			self.main.gui.readButton.set_sensitive(True)
			
			# Insert temporary message
			imgfile = self.main.updater.getImage(message, True)
			self.main.gui.message.updateList.append((message, imgfile))
			gobject.idle_add(lambda: self.main.gui.message.pushUpdates())
			
			# Reset
			self.main.messageUser = UNSET_TEXT
			self.main.messageID = UNSET_ID_NUM
			self.main.messageText = UNSET_TEXT
			self.main.gui.text.setText(UNSET_TEXT)
			
			# Focus HTML
			self.main.gui.showInput(False)
			self.main.gui.message.grab_focus()
			self.main.wasSending = False
		
		except Exception, error:
			print error
			gobject.idle_add(lambda: self.main.gui.showError(error))
	

# New style Retweets -----------------------------------------------------------
# ------------------------------------------------------------------------------
class Retweet(threading.Thread):
	def __init__(self, main, name, tweetid):
		threading.Thread.__init__(self)
		self.main = main
		self.name = name
		self.tweetid = tweetid
	
	def run(self):
		self.main.wasSending = True
		self.main.wasRetweeting = True
		try:
			# Send Tweet
			self.main.api.retweet(self.tweetid)

			# Focus HTML
			self.main.gui.showInput(False)
			self.main.gui.html.grab_focus()
			self.main.wasSending = False
			gobject.idle_add(lambda: self.main.gui.showRetweetInfo(self.name))
		
		except Exception, error:
			print error
			gobject.idle_add(lambda: self.main.gui.showError(error))	
		
		self.main.isSending = False


