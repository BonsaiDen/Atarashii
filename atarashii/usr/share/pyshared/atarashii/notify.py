#  This file is part of Atarashii.
#
#  Atarashii is free software: you can redistribute it and/or
#  modify it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  Atarashii is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Atarashii. If not, see <http://www.gnu.org/licenses/>.


# Notifications ----------------------------------------------------------------
# ------------------------------------------------------------------------------
import pynotify
import subprocess
import threading

pynotify.init("Atarashii")


class NotifierSound(threading.Thread):
    def __init__(self, sound):
        threading.Thread.__init__(self)
        self.sound = sound
    
    def run(self):
        try:
            subprocess.call(["mplayer", self.sound])
        
        finally:
            pass


class Notifier:
    def __init__(self, main):
        self.main = main
    
    def show(self, objs):
        if self.main.settings.is_true("sound"):
            self.sound()
        
        for obj in objs:
            self.notify(obj[0], obj[1], obj[2])
    
    def notify(self, title, text, icon = None):
        notification = pynotify.Notification(title, text, icon)
        return notification.show()
    
    def sound(self):
        if self.main.settings['soundfile'] != "None":
            snd = NotifierSound(self.main.settings['soundfile'])
            snd.setDaemon(True)
            snd.start()

