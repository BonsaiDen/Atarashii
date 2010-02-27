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


# Send Thread ------------------------------------------------------------------
# ------------------------------------------------------------------------------
import gobject
import threading

class Send(threading.Thread):
	def __init__(self, atarashii, text):
		threading.Thread.__init__(self)
		self.atarashii = atarashii
		self.text = text

	def run(self):
		buf = self.atarashii.input.get_buffer()
		if self.atarashii.reply_id != -1:
			try:
				update = self.atarashii.api.update_status(self.text, in_reply_to_status_id = self.atarashii.reply_id)
				self.atarashii.settings['lasttweet'] = str(update.id)
				self.atarashii.updater.setLast(update.id)
				self.atarashii.readButton.set_sensitive(True)
				
				file = self.atarashii.updater.getImage(update.user.profile_image_url, update.user.id)
				self.atarashii.html.list.append((update, file, False))
				gobject.idle_add(lambda: self.atarashii.html.push())
				self.atarashii.reply_user = ""
				self.atarashii.reply_text = ""
				self.atarashii.reply_id = -1
				buf.set_text("")
				self.atarashii.progress.hide()
				self.atarashii.scroll.show()
				self.atarashii.html.view.grab_focus()
				self.atarashii.textFocus = False
			
			except Exception, detail:
				self.atarashii.error(detail)
				self.atarashii.progress.hide()
				self.atarashii.scroll.show()
				gobject.idle_add(lambda: self.atarashii.input.grab_focus())
		
		else:
			try:
				update = self.atarashii.api.update_status(self.text)
				self.atarashii.updater.setLast(update.id)
				self.atarashii.readButton.set_sensitive(True)
				
				file = self.atarashii.updater.getImage(update.user.profile_image_url, update.user.id)
				self.atarashii.html.list.append((update, file, False))
				gobject.idle_add(lambda: self.atarashii.html.push())
				buf.set_text("")
				self.atarashii.progress.hide()
				self.atarashii.scroll.show()
				self.atarashii.html.view.grab_focus()
				self.atarashii.textFocus = False
			
			except Exception, detail:
				self.atarashii.error(detail)
				self.atarashii.progress.hide()
				self.atarashii.scroll.show()
				gobject.idle_add(lambda: self.atarashii.input.grab_focus())
		
		self.atarashii.sending = False
		gobject.idle_add(lambda: self.atarashii.sizeInput())
		self.atarashii.input.set_sensitive(True)

