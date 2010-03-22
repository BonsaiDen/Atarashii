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

pynotify.init("Atarashii")

class Notifier:
    def __init__(self, main):
        self.main = main
        self.player = None
        
    def show(self, objs):
        if len(objs) > 0 and self.main.settings.is_true("sound") \
           and self.main.settings['soundfile'] != "None":
            
            try:
                # Check for Zombieeeeeees!
                try:
                    if self.player != None:
                        self.player.kill()
                        print "Zombieeeees!"
                
                except OSError:
                    pass
                
                self.player = subprocess.Popen(["mplayer", "-really-quiet",
                                          "-nolirc",
                                          self.main.settings['soundfile']])
            
            except OSError, error:
                print "Failed to play sound", error
        
        # Shot notification
        for obj in objs:
            try:
                pynotify.Notification(obj[0], obj[1], obj[2]).show()
                            
            except Exception, error:
                print "Notify error", error

