#  This file is part of  main.
#
#  main is free software: you can redistribute it and/or 
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  main is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
# 
#  You should have received a copy of the GNU General Public License along with
#  main. If not, see <http://www.gnu.org/licenses/>.


# Sender Thread ------------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading

class Send(threading.Thread):
	def __init__(self, main):
		threading.Thread.__init__(self)
		self.main = main

	def run(self):
		text = self.main.gui.text.getText()
		
		# Reply
		if self.main.replyID!= -1:
			try:
				# Send Tweet
				update = self.main.api.update_status(text, in_reply_to_status_id = self.main.replyID)
				self.main.updater.setLast(update.id)
				self.main.gui.readButton.set_sensitive(True)
				
				# Insert temporary tweet
				imgfile = self.main.updater.getImage(update.user.profile_image_url, update.user.id)
				self.main.gui.html.updateList.append((update, imgfile, False))
				gobject.idle_add(lambda: self.main.gui.html.pushUpdates())
				
				# Reset
				self.main.replyUser = ""
				self.main.replyText = ""
				self.main.replyID = -1
				self.main.gui.text.setText("")
				
				# Focus HTML
				self.main.gui.text.hasFocus = False
				self.main.gui.showInput()
				self.main.gui.html.grab_focus()
			
			except Exception, error:
				print error
				self.main.gui.showError(error)
				self.main.gui.showInput()
				gobject.idle_add(lambda: self.main.gui.text.grab_focus())
		
		# Normal Tweet / Retweet
		else:
			try:
				# Send Tweet
				update = self.main.api.update_status(text)
				self.main.updater.setLast(update.id)
				self.main.gui.readButton.set_sensitive(True)
				
				# Insert temporary tweet
				imgfile = self.main.updater.getImage(update.user.profile_image_url, update.user.id)
				self.main.gui.html.updateList.append((update, imgfile, False))
				gobject.idle_add(lambda: self.main.gui.html.pushUpdates())
				
				# Reset
				self.main.gui.text.setText("")
				
				# Focus HTML
				self.main.gui.text.hasFocus = False
				self.main.gui.showInput()
				self.main.gui.html.grab_focus()
			
			except Exception, error:
				print error
				self.main.gui.showError(error)
				self.main.gui.showInput()
				gobject.idle_add(lambda: self.main.gui.text.grab_focus())
		
		self.main.isSending = False
		self.main.gui.text.set_sensitive(True)

