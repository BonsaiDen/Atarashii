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


# Notifications ----------------------------------------------------------------
# ------------------------------------------------------------------------------
try:
	import pynotify
	import subprocess
	import threading

	class NotifierSound(threading.Thread):
		def __init__(self, sound):
			threading.Thread.__init__(self)
			self.sound = sound
	
		def run(self):
			try:
				subprocess.call(["mplayer", self.sound])

			finally:
				pass

	pynotify.init("Atarashii")
	class Notifier:
		def __init__(self, main):
			self.main = main
	
		def show(self, objs, sound = False):
			if sound:
				self.sound()
		
			for obj in objs:
				self.notify(obj[0], obj[1], obj[2], obj[3])
	
		def notify(self, title, text, icon = None, timeout = None):
			caps = pynotify.get_server_caps()    
			notification = pynotify.Notification(title, text, icon)
			if timeout:
				notification.set_timeout(timeout)
		
			return notification.show()
	
		def sound(self):
			snd = NotifierSound(self.main.settings['soundfile'])
			snd.setDaemon(True)
			snd.start()
	
	canNotify = True		
	
except:
	class Notifier():
		def __init__(self, main):
			pass
		
		def show(self, objs, sound = False):
			pass
			
	canNotify = False

